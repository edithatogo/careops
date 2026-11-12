import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { calculateScenario, CalculationInputError } from '../src/index.mjs';

const fixturePath = new URL('../fixtures/activity-cost-scenario.synthetic.json', import.meta.url);
const fixture = JSON.parse(await readFile(fixturePath, 'utf8'));
const packageRoot = fileURLToPath(new URL('..', import.meta.url));

function copyFixture() {
  return structuredClone(fixture);
}

test('calculates fictional activity and optional aggregate values by period with sensitivity', () => {
  const result = calculateScenario(fixture);
  assert.equal(result.baseActivityTotalMinorUnits, 112_000);
  assert.equal(result.scenarioActivityTotalMinorUnits, 117_600);
  assert.equal(result.aggregateProviderStatus, 'accepted');
  assert.equal(result.aggregateTotalMinorUnits, 20_000);
  assert.equal(result.totalScenarioCostMinorUnits, 137_600);
  assert.equal(result.period, '2026-07');
  assert.deepEqual(result.activities.map((row) => row.activityId), ['ACT-001', 'ACT-002']);
  assert.deepEqual(result.acceptedAggregateItems.map((row) => row.sourceQualifiedId), ['OH-001']);
});

test('is byte-stable across input row order', () => {
  const reverse = copyFixture();
  reverse.activities.reverse();
  reverse.aggregateProvider.items.reverse();
  assert.equal(JSON.stringify(calculateScenario(fixture)), JSON.stringify(calculateScenario(reverse)));
});

test('optional aggregate provider absence leaves the activity-only result explicit', () => {
  const input = copyFixture();
  delete input.aggregateProvider;
  const result = calculateScenario(input);
  assert.equal(result.aggregateProviderStatus, 'absent');
  assert.equal(result.aggregateTotalMinorUnits, 0);
  assert.equal(result.totalScenarioCostMinorUnits, result.scenarioActivityTotalMinorUnits);
});

test('incompatible and stale optional providers contribute no aggregate values', () => {
  const incompatible = copyFixture();
  incompatible.aggregateProvider.contractVersion = 2;
  assert.equal(calculateScenario(incompatible).aggregateProviderStatus, 'incompatible');

  const stale = copyFixture();
  stale.aggregateProvider.snapshotDate = '2026-10-19';
  assert.equal(calculateScenario(stale).aggregateProviderStatus, 'stale');
});

test('missing provider fields and mismatched periods are excluded from totals', () => {
  const missing = copyFixture();
  delete missing.aggregateProvider.snapshotId;
  assert.equal(calculateScenario(missing).aggregateProviderStatus, 'missing');

  const wrongPeriod = copyFixture();
  wrongPeriod.aggregateProvider.items[0].period = '2026-08';
  assert.equal(calculateScenario(wrongPeriod).aggregateProviderStatus, 'period-mismatch');

  const wrongKey = copyFixture();
  wrongKey.aggregateProvider.idempotencyKey = 'unscoped-retry-key';
  assert.equal(calculateScenario(wrongKey).aggregateProviderStatus, 'correlation-mismatch');
});

test('identical aggregate retries are idempotent and conflicting retries are rejected', () => {
  const retry = copyFixture();
  retry.aggregateProvider.items.push(structuredClone(retry.aggregateProvider.items[0]));
  assert.equal(calculateScenario(retry).aggregateTotalMinorUnits, 20_000);

  const conflict = copyFixture();
  conflict.aggregateProvider.items.push({ ...conflict.aggregateProvider.items[0], amountMinorUnits: 20_001 });
  assert.throws(() => calculateScenario(conflict), (error) =>
    error instanceof CalculationInputError && error.code === 'DUPLICATE_CONFLICT');
});

test('rejects missing, invalid, duplicate and incompatible activity inputs', () => {
  const missing = copyFixture();
  delete missing.activities[0].quantity;
  assert.throws(() => calculateScenario(missing), (error) => error.code === 'INVALID_ACTIVITY');

  const invalid = copyFixture();
  invalid.activities[0].unitRateMinorUnits = -1;
  assert.throws(() => calculateScenario(invalid), (error) => error.code === 'INVALID_ACTIVITY');

  const duplicate = copyFixture();
  duplicate.activities.push(structuredClone(duplicate.activities[0]));
  assert.throws(() => calculateScenario(duplicate), (error) => error.code === 'DUPLICATE_ACTIVITY');

  const unsupported = copyFixture();
  unsupported.contractVersion = 2;
  assert.throws(() => calculateScenario(unsupported), (error) => error.code === 'INCOMPATIBLE_CONTRACT');
});

test('requires units and period in each calculation input', () => {
  const unitMismatch = copyFixture();
  unitMismatch.activities[0].rateUnit = 'AUD/day';
  assert.throws(() => calculateScenario(unitMismatch), (error) => error.code === 'INVALID_ACTIVITY');

  const invalidPeriod = copyFixture();
  invalidPeriod.period = 'July 2026';
  assert.throws(() => calculateScenario(invalidPeriod), (error) => error.code === 'INVALID_SCENARIO');
});

test('source package includes the Apache licence, notice, contract and no build dependencies', async () => {
  const packageManifest = JSON.parse(await readFile(new URL('../package.json', import.meta.url), 'utf8'));
  assert.equal(packageManifest.license, 'Apache-2.0');
  assert.deepEqual(packageManifest.dependencies ?? {}, {});
  const parentLicense = await readFile(resolve(packageRoot, '../../LICENSE'));
  const packageLicense = await readFile(new URL('../LICENSE', import.meta.url));
  assert.deepEqual(packageLicense, parentLicense);
  const packageResult = execFileSync('npm', ['pack', '--dry-run', '--json'], {
    cwd: packageRoot,
    encoding: 'utf8',
  });
  const archive = JSON.parse(packageResult)[0];
  const packed = new Set(archive.files.map((file) => file.path));
  for (const name of ['LICENSE', 'NOTICE', 'README.md', 'package.json', 'src/index.mjs']) {
    assert.ok(packed.has(name), `Source package is missing ${name}.`);
  }
  assert.equal(packed.has('fixtures/activity-cost-scenario.synthetic.json'), false);
  assert.equal(packed.has('test/index.test.mjs'), false);
});
