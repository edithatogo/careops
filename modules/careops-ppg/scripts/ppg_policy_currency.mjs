// Usage: node scripts/ppg_policy_currency.mjs PRIVATE_ADAPTER NEW_RECEIPT [PRIOR_RECEIPT]
import fs from "node:fs";
import { coveragePage } from "./ppg_currency_report.mjs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
const [adapter, receipt, previous, mode] = process.argv.slice(2);
if (
  ![adapter, receipt, ...(previous ? [previous] : [])].every((v) =>
    v && path.resolve(v).split(path.sep).includes(".local")
  ) || fs.existsSync(receipt)
) throw Error("Private adapter and new receipt required");
const c = await (await import(pathToFileURL(path.resolve(adapter)))).connect();
const hash = (v) => createHash("sha256").update(v).digest("hex");
const send = (key, route, payload, extra = {}) =>
  c.send({
    key: "currency-" + key,
    route,
    payload,
    payloadSHA256: hash(
      Buffer.isBuffer(payload) ? payload : JSON.stringify(payload),
    ),
    ...extra,
  });
const list = await c.get(
  "lists/getbytitle('PPG Source Update Leads')?$select=Id,EnableVersioning",
);
const cat = await c.get(
  "lists/getbytitle('PPG Catalogue')?$select=Id,DefaultDisplayFormUrl",
);
if (!list.EnableVersioning || !cat.DefaultDisplayFormUrl) {
  throw Error("Expected versioned leads and catalogue form");
}
const base = "lists(guid'" + list.Id + "')";
const policies = await c.all(
  "lists(guid'" + cat.Id +
    "')/items?$select=Id,DocumentUID,sourceDocumentId,sourceTitle,sourceCustodian&$top=1000",
);
const norm = (s) =>
  " " + String(s ?? "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim() + " ";
const general = new Set(
  "a an of at by from to the for and in on or with use using care policy procedure guideline management services service hospital health patient patients clinical medical safety update alerts report national program review treatment general adult adults children child during before after system information practice public quality new products product device devices local staff"
    .split(" "),
);
const informative = (w) => w.length >= 3 && !general.has(w) && /[a-z]/.test(w);
const phrases = (s) => {
  const words = norm(s).trim().split(" ");
  return [2, 3].flatMap((n) =>
    Array.from({ length: Math.max(0, words.length - n + 1) }).map((_, i) =>
      words.slice(i, i + n)
    ).filter((part) => part.filter(informative).length >= 2).map((part) =>
      part.join(" ")
    )
  );
};
const index = new Map();
for (const p of policies) {
  for (const phrase of new Set(phrases(p.sourceTitle))) {
    const a = index.get(phrase) ?? [];
    a.push(p);
    index.set(phrase, a);
  }
}
const relationships = await c.all(
  "lists/getbytitle('PPG Document Relationships')/items?$select=FromDocumentUID,ToDocumentUID,RelationshipType,ReviewState&$top=500",
);
const byUid = new Map(policies.map((p) => [p.DocumentUID, p]));
const policyUrl = (p) =>
  new URL(cat.DefaultDisplayFormUrl + "?ID=" + p.Id, c.c.siteUrl).href;
function project(r) {
  const title = norm(r.Title);
  let hits = policies.filter((p) =>
    [p.DocumentUID, p.sourceDocumentId].some((id) =>
      id && String(id).length >= 6 && title.includes(norm(id))
    )
  );
  let basis = "Identifier in lead title";
  if (!hits.length) {
    hits = policies.filter((p) =>
      p.sourceTitle && norm(p.sourceTitle) === title
    );
    basis = "Exact catalogue title";
  }
  if (!hits.length) {
    const matches = new Map();
    for (const phrase of phrases(r.Title)) {
      const ps = index.get(phrase);
      if (ps?.length === 1) matches.set(ps[0], phrase);
    }
    hits = [...matches.keys()];
    basis = "Shared catalogue phrase: " +
      [...new Set(matches.values())].join("; ");
  }
  const p = hits.length === 1 ? hits[0] : null;
  const indirect = relationships.filter((rel) =>
    hits.some((hit) => hit.DocumentUID === rel.ToDocumentUID) &&
    byUid.has(rel.FromDocumentUID) &&
    ["Proposed", "Accepted"].includes(rel.ReviewState)
  );
  const describe = (v) =>
    [
      v.DocumentUID,
      v.sourceTitle,
      v.sourceCustodian || "Custodian unresolved",
      policyUrl(v),
    ].join(" — ");
  const linked = indirect.map((rel) =>
    rel.ReviewState + " " + rel.RelationshipType + " (review only): " +
    describe(byUid.get(rel.FromDocumentUID))
  );

  return {
    CurrencyMatch: !hits.length
      ? "Unresolved"
      : p
      ? "Candidate — review"
      : "Multiple candidates",
    CurrencyEvidence: hits.length
      ? basis + " | " +
        hits.map(describe).concat(linked).join("\n")
      : "No identifier, exact title or distinctive shared title phrase",
    CurrencyPolicy: p
      ? {
        Url:
          new URL(cat.DefaultDisplayFormUrl + "?ID=" + p.Id, c.c.siteUrl).href,
        Description: "Open candidate policy",
      }
      : null,
    CurrencyOwner: p?.sourceCustodian || null,
  };
}
const fields = {
  CurrencyMatch: "Text",
  CurrencyEvidence: "Note",
  CurrencyPolicy: "URL",
  CurrencyOwner: "Text",
  CurrencyDisposition: "Text",
  CurrencyNoticeText: "Note",
  CurrencyNoticeProvenance: "Note",
  CurrencyReviewEvidence: "Note",
};
const schema = await c.all(base + "/fields?$select=InternalName,TypeAsString");
for (const [k, t] of Object.entries(fields)) {
  const v = schema.find((f) => f.InternalName === k);
  if (v && v.TypeAsString !== t) throw Error("Field conflict " + k);
  if (!v) {
    await send(k.toLowerCase(), base + "/fields/CreateFieldAsXml", {
      parameters: {
        SchemaXml: '<Field Name="' + k + '" StaticName="' + k +
          '" DisplayName="' + k + '" Type="' + t + '" RichText="FALSE"/>',
        Options: 8,
      },
    });
  }
}
const viewFields = [
  "LinkTitle",
  "SourceLink",
  "ObservedAt",
  "CurrencyMatch",
  "CurrencyPolicy",
  "CurrencyOwner",
  "CurrencyEvidence",
  "CurrencyDisposition",
  "CurrencyReviewEvidence",
  "CurrencyNoticeProvenance",
];
const title = "Policy currency review";
if (!(await c.all(base + "/views")).some((v) => v.Title === title)) {
  await send("view", base + "/views/add", {
    parameters: {
      Title: title,
      ViewFields: viewFields,
      Query:
        '<OrderBy><FieldRef Name="ObservedAt" Ascending="FALSE"/></OrderBy>',
      PersonalView: false,
      SetAsDefaultView: false,
      Paged: true,
      RowLimit: 100,
    },
  });
}
const reviewFieldsRoute = base +
  "/views/getbytitle('Policy currency review')/ViewFields";
const existingReviewColumns = await c.get(reviewFieldsRoute);
for (const k of ["CurrencyReviewEvidence", "CurrencyNoticeProvenance"]) {
  if (
    !(existingReviewColumns.Items ?? existingReviewColumns.value ?? [])
      .includes(k)
  ) {
    await send(
      "review-evidence-column-" + k.toLowerCase(),
      reviewFieldsRoute + "/addviewfield('" + k + "')",
      {},
    );
  }
}
const view = base + "/views/getbytitle('Policy currency review')",
  cols = await c.get(view + "/ViewFields");
if (!viewFields.every((k) => (cols.Items ?? cols.value).includes(k))) {
  throw Error("View columns changed");
}
if (mode && (mode !== "--new-only" || !previous)) {
  throw Error("Unsupported refresh mode");
}
const reportTitle = "Policy currency dispositions";
const reportFields = [
  "LinkTitle",
  "ObservedAt",
  "CurrencyMatch",
  "CurrencyOwner",
  "CurrencyDisposition",
  "CurrencyPolicy",
];
const reportQuery =
  '<GroupBy Collapse="TRUE" GroupLimit="100"><FieldRef Name="CurrencyDisposition"/></GroupBy><OrderBy><FieldRef Name="ObservedAt" Ascending="FALSE"/></OrderBy>';
if (!(await c.all(base + "/views")).some((v) => v.Title === reportTitle)) {
  await send("disposition-report", base + "/views/add", {
    parameters: {
      Title: reportTitle,
      ViewFields: reportFields,
      Query: reportQuery,
      PersonalView: false,
      SetAsDefaultView: false,
      Paged: true,
      RowLimit: 100,
    },
  });
}
const report = await c.get(
  base + "/views/getbytitle('Policy currency dispositions')",
);
const reportColumns = await c.get(
  base + "/views/getbytitle('Policy currency dispositions')/ViewFields",
);
if (
  !reportFields.every((k) =>
    (reportColumns.Items ?? reportColumns.value ?? []).includes(k)
  )
) throw Error("Disposition report columns changed");
if (!report.ViewQuery?.includes('Name="CurrencyDisposition"')) {
  throw Error("Disposition grouping missing");
}
const prior = previous ? JSON.parse(fs.readFileSync(previous)) : null;
if (prior && (prior.list !== list.Id || prior.site !== c.c.siteUrl)) {
  throw Error("Wrong prior receipt");
}
const read = async () => {
  let route = base +
    "/items?$select=Id,Title,GUID,CurrencyDisposition,CurrencyMatch,CurrencyPolicy,CurrencyOwner,CurrencyEvidence&$top=500";
  const rows = [];
  const seen = new Set();
  while (route) {
    if (seen.has(route)) throw Error("Repeated lead inventory page");
    seen.add(route);
    const page = await c.item(route);
    const records = page.results ?? page.value;
    if (!Array.isArray(records)) throw Error("Invalid lead inventory page");
    rows.push(...records);
    route = page.__next ?? page["@odata.nextLink"] ?? page["odata.nextLink"];
  }
  return rows;
};
const comparable = (v) =>
  v?.Url ? JSON.stringify([v.Url, v.Description]) : v ?? null;
const initial = await read(), desired = {}, changes = [], held = {};
const currentIds = new Set(initial.map((r) => r.GUID));
if (Object.keys(prior?.rows ?? {}).some((id) => !currentIds.has(id))) {
  throw Error("Previously recorded lead missing; reconcile before refresh");
}
for (const r of initial) {
  if (
    !r.GUID || Object.hasOwn(desired, r.GUID) || Object.hasOwn(held, r.GUID)
  ) {
    throw Error("Missing or duplicate lead identity");
  }
  if (mode === "--new-only" && prior?.rows[r.GUID]) {
    desired[r.GUID] = prior.rows[r.GUID];
    continue;
  }
  const want = project(r);
  desired[r.GUID] = want;
  const patch = {};
  for (const k of Object.keys(want)) {
    if (comparable(want[k]) === comparable(r[k])) continue;
    if (comparable(r[k]) !== comparable(prior?.rows[r.GUID]?.[k])) {
      if (mode === "--new-only") {
        held[r.GUID] = "Owner edit requires review";
        break;
      }
      throw Error("Reconcile owner edit on lead " + r.Id);
    }
    patch[k] = want[k];
  }
  if (
    mode === "--new-only" && Object.keys(patch).length && r.CurrencyDisposition
  ) held[r.GUID] = "Existing disposition requires review";
  if (Object.hasOwn(held, r.GUID)) {
    delete desired[r.GUID];
    continue;
  }
  if (Object.keys(patch).length && r.CurrencyDisposition) {
    throw Error("Review disposition before changing lead " + r.Id);
  }
  if (Object.keys(patch).length) changes.push({ r, patch });
}
for (let i = 0; i < changes.length; i += 20) {
  const parts = [], group = changes.slice(i, i + 20);
  const boundary = "batch_" + hash(JSON.stringify(group)).slice(0, 24);
  for (const { r, patch } of group) {
    const tag = r.__metadata?.etag ?? r["@odata.etag"] ?? r["odata.etag"];
    if (!/^"\d+"$/.test(tag)) throw Error("Missing row version " + r.Id);
    const cs = "changeset_" + r.Id;
    parts.push(
      "--" + boundary,
      "Content-Type: multipart/mixed; boundary=" + cs,
      "",
      "--" + cs,
      "Content-Type: application/http",
      "Content-Transfer-Encoding: binary",
      "",
      "PATCH " + c.c.siteUrl + "/_api/web/" + base + "/items(" + r.Id +
        ") HTTP/1.1",
      "If-Match: " + tag,
      "Content-Type: application/json;odata=nometadata",
      "",
      JSON.stringify(patch),
      "--" + cs + "--",
    );
  }
  parts.push("--" + boundary + "--", "");
  const bytes = Buffer.from(parts.join("\r\n"));
  const result = await send(
    hash(bytes).slice(0, 24),
    c.c.siteUrl + "/_api/$batch",
    bytes,
    { contentType: "multipart/mixed; boundary=" + boundary },
  );
  const codes = [...String(result).matchAll(/HTTP\/1\.[01] (\d{3})/g)].map(
    (m) => m[1],
  );
  if (codes.length !== group.length || codes.some((v) => v !== "204")) {
    throw Error("Reconcile batch results " + codes.join(","));
  }
  if (i + 20 < changes.length) await new Promise((r) => setTimeout(r, 4000));
}
const rows = await read();
const titles = new Map(initial.map((r) => [r.GUID, r.Title]));
if (
  rows.length !== titles.size ||
  new Set(rows.map((r) => r.GUID)).size !== titles.size ||
  rows.some((r) => !titles.has(r.GUID) || titles.get(r.GUID) !== r.Title)
) throw Error("Lead inventory changed during refresh");
for (const r of rows) {
  if (mode === "--new-only" && prior?.rows[r.GUID]) continue;
  if (Object.hasOwn(held, r.GUID)) continue;
  const expected = desired[r.GUID];
  if (
    !expected ||
    Object.entries(expected).some(([k, v]) =>
      comparable(v) !== comparable(r[k])
    )
  ) throw Error("Readback mismatch " + r.Id);
}
const url = (await c.get(view)).ServerRelativeUrl;
const coverage = await coveragePage(
  c,
  send,
  report.ServerRelativeUrl,
  rows,
  prior?.coverage,
);
fs.writeFileSync(
  receipt,
  JSON.stringify({
    site: c.c.siteUrl,
    list: list.Id,
    rows: desired,
    held,
    verified: rows.length,
    evaluated: mode === "--new-only"
      ? initial.filter((r) => !prior.rows[r.GUID]).length
      : initial.length,
    coverage,
    report: report.ServerRelativeUrl,
    dispositioned: rows.filter((r) =>
      String(r.CurrencyDisposition ?? "").trim()
    ).length,
    changed: changes.length,
    view: url,
  }),
  { mode: 0o600, flag: "wx" },
);
console.log(rows.length, "verified;", changes.length, "changed");
