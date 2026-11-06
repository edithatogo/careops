export const CONTRACT_VERSION = 1;

export class CalculationInputError extends Error {
  constructor(code, message) {
    super(message);
    this.name = 'CalculationInputError';
    this.code = code;
  }
}

function fail(code, message) {
  throw new CalculationInputError(code, message);
}

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function isPeriod(value) {
  if (typeof value !== 'string' || !/^\d{4}-(0[1-9]|1[0-2])$/.test(value)) return false;
  return true;
}

function isIsoDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(`${value}T00:00:00.000Z`);
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value;
}

function assertSafeInteger(value, code, message) {
  if (!Number.isSafeInteger(value) || value < 0) fail(code, message);
}

function sumUniqueAggregateItems(provider, scenario) {
  if (provider === undefined || provider === null) {
    return { status: 'absent', totalMinorUnits: 0, items: [] };
  }
  if (!isObject(provider) || provider.contractVersion !== CONTRACT_VERSION) {
    return { status: 'incompatible', totalMinorUnits: 0, items: [] };
  }
  if (typeof provider.providerId !== 'string' || provider.providerId.length === 0 ||
      typeof provider.snapshotId !== 'string' || provider.snapshotId.length === 0 ||
      typeof provider.correlationId !== 'string' || typeof provider.idempotencyKey !== 'string') {
    return { status: 'missing', totalMinorUnits: 0, items: [] };
  }
  if (provider.correlationId !== scenario.scenarioId ||
      provider.idempotencyKey !== `${provider.providerId}:${provider.snapshotId}:${provider.correlationId}`) {
    return { status: 'correlation-mismatch', totalMinorUnits: 0, items: [] };
  }
  if (!isIsoDate(provider.snapshotDate) || !Number.isSafeInteger(provider.maxAgeDays) || provider.maxAgeDays < 0 ||
      !Array.isArray(provider.items)) {
    return { status: 'missing', totalMinorUnits: 0, items: [] };
  }
  const ageDays = (Date.parse(`${scenario.evaluatedAt}T00:00:00.000Z`) -
    Date.parse(`${provider.snapshotDate}T00:00:00.000Z`)) / 86_400_000;
  if (ageDays < 0 || ageDays > provider.maxAgeDays) {
    return { status: 'stale', totalMinorUnits: 0, items: [] };
  }

  const unique = new Map();
  for (const item of provider.items) {
    if (!isObject(item) || typeof item.sourceQualifiedId !== 'string' || item.sourceQualifiedId.length === 0 ||
        !Number.isSafeInteger(item.amountMinorUnits) || item.amountMinorUnits < 0 ||
        !isPeriod(item.period) || typeof item.currencyCode !== 'string') {
      return { status: 'missing', totalMinorUnits: 0, items: [] };
    }
    if (item.period !== scenario.period) {
      return { status: 'period-mismatch', totalMinorUnits: 0, items: [] };
    }
    if (item.currencyCode !== scenario.currencyCode) {
      return { status: 'currency-mismatch', totalMinorUnits: 0, items: [] };
    }
    const normalized = JSON.stringify({
      sourceQualifiedId: item.sourceQualifiedId,
      period: item.period,
      currencyCode: item.currencyCode,
      amountMinorUnits: item.amountMinorUnits,
    });
    const existing = unique.get(item.sourceQualifiedId);
    if (existing !== undefined && existing !== normalized) {
      fail('DUPLICATE_CONFLICT', `Conflicting retry for aggregate identity ${item.sourceQualifiedId}.`);
    }
    unique.set(item.sourceQualifiedId, normalized);
  }

  const items = [...unique.keys()].sort().map((key) => JSON.parse(unique.get(key)));
  const totalMinorUnits = items.reduce((sum, item) => sum + item.amountMinorUnits, 0);
  assertSafeInteger(totalMinorUnits, 'AGGREGATE_OVERFLOW', 'Aggregate total exceeds the supported integer range.');
  return { status: 'accepted', totalMinorUnits, items };
}

export function calculateScenario(input) {
  if (!isObject(input) || input.contractVersion !== CONTRACT_VERSION) {
    fail('INCOMPATIBLE_CONTRACT', 'Calculation input must declare contract version 1.');
  }
  if (typeof input.scenarioId !== 'string' || input.scenarioId.length === 0 ||
      !isPeriod(input.period) || !isIsoDate(input.evaluatedAt) ||
      typeof input.currencyCode !== 'string' || !/^[A-Z]{3}$/.test(input.currencyCode) ||
      !Number.isSafeInteger(input.rateSensitivityBps) || input.rateSensitivityBps < 0 ||
      !Array.isArray(input.activities) || input.activities.length === 0) {
    fail('INVALID_SCENARIO', 'Scenario identity, YYYY-MM period, evaluation date, currency, sensitivity and activities are required.');
  }

  const seenIds = new Set();
  const activities = [];
  for (const activity of input.activities) {
    if (!isObject(activity) || typeof activity.activityId !== 'string' || activity.activityId.length === 0 ||
        !Number.isFinite(activity.quantity) || activity.quantity < 0 ||
        typeof activity.quantityUnit !== 'string' || activity.quantityUnit.length === 0 ||
        !Number.isSafeInteger(activity.unitRateMinorUnits) || activity.unitRateMinorUnits < 0 ||
        activity.rateUnit !== `${input.currencyCode}/${activity.quantityUnit}`) {
      fail('INVALID_ACTIVITY', 'Each activity needs a unique id, non-negative quantity, explicit units and a non-negative integer rate in minor currency units.');
    }
    if (seenIds.has(activity.activityId)) fail('DUPLICATE_ACTIVITY', `Duplicate activity identity ${activity.activityId}.`);
    seenIds.add(activity.activityId);
    const baseCostMinorUnits = Math.round(activity.quantity * activity.unitRateMinorUnits);
    assertSafeInteger(baseCostMinorUnits, 'ACTIVITY_OVERFLOW', 'Activity cost exceeds the supported integer range.');
    const scenarioCostMinorUnits = Math.round(baseCostMinorUnits * input.rateSensitivityBps / 10_000);
    assertSafeInteger(scenarioCostMinorUnits, 'ACTIVITY_OVERFLOW', 'Sensitivity-adjusted cost exceeds the supported integer range.');
    activities.push({
      activityId: activity.activityId,
      quantity: activity.quantity,
      quantityUnit: activity.quantityUnit,
      rateUnit: activity.rateUnit,
      unitRateMinorUnits: activity.unitRateMinorUnits,
      baseCostMinorUnits,
      scenarioCostMinorUnits,
    });
  }
  activities.sort((left, right) => left.activityId.localeCompare(right.activityId, 'en'));

  const baseActivityTotalMinorUnits = activities.reduce((sum, item) => sum + item.baseCostMinorUnits, 0);
  const scenarioActivityTotalMinorUnits = activities.reduce((sum, item) => sum + item.scenarioCostMinorUnits, 0);
  assertSafeInteger(baseActivityTotalMinorUnits, 'ACTIVITY_OVERFLOW', 'Base activity total exceeds the supported integer range.');
  assertSafeInteger(scenarioActivityTotalMinorUnits, 'ACTIVITY_OVERFLOW', 'Scenario activity total exceeds the supported integer range.');

  const aggregate = sumUniqueAggregateItems(input.aggregateProvider, input);
  const totalScenarioCostMinorUnits = scenarioActivityTotalMinorUnits + aggregate.totalMinorUnits;
  assertSafeInteger(totalScenarioCostMinorUnits, 'TOTAL_OVERFLOW', 'Scenario total exceeds the supported integer range.');

  return {
    contractVersion: CONTRACT_VERSION,
    scenarioId: input.scenarioId,
    period: input.period,
    evaluatedAt: input.evaluatedAt,
    currencyCode: input.currencyCode,
    rateSensitivityBps: input.rateSensitivityBps,
    activities,
    baseActivityTotalMinorUnits,
    scenarioActivityTotalMinorUnits,
    aggregateProviderStatus: aggregate.status,
    acceptedAggregateItems: aggregate.items,
    aggregateTotalMinorUnits: aggregate.totalMinorUnits,
    totalScenarioCostMinorUnits,
  };
}
