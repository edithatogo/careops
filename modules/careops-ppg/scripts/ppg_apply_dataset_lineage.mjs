// Apply the private export-derived manifest through the installation's qualified adapter.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
const [adapter, manifest, receipt, previous] = process.argv.slice(2);
if (
  ![adapter, manifest, receipt, ...(previous ? [previous] : [])].every((v) =>
    v && path.resolve(v).split(path.sep).includes(".local")
  ) || fs.existsSync(receipt)
) throw Error("Require private inputs and new receipt");
const c = await (await import(pathToFileURL(path.resolve(adapter)))).connect();
const plan = JSON.parse(fs.readFileSync(manifest));
const prior = previous ? JSON.parse(fs.readFileSync(previous)).rows : {};
const hash = (v) => createHash("sha256").update(v).digest("hex");
async function send(key, route, payload, extra = {}) {
  return c.send({
    key: "lineage-" + key,
    route,
    payload,
    payloadSHA256: hash(
      Buffer.isBuffer(payload) ? payload : JSON.stringify(payload),
    ),
    ...extra,
  });
}
const list = await c.get(
  "lists/getbytitle('PPG Dataset Catalogue')?$select=Id,EnableVersioning",
);
if (!list.EnableVersioning) throw Error("Versioning required");
const base = "lists(guid'" + list.Id + "')";
const fields = {
  DataRole: "Choice",
  DatasetSource: "Note",
  ReadFlows: "Note",
  WriteFlows: "Note",
  BindingStatus: "Text",
};
const schema = await c.all(base + "/fields?$select=InternalName,TypeAsString");
if (
  plan.fictionalRunReads?.length ||
  schema.some((f) => f.InternalName === "ObservedReadFlows") ||
  Object.values(prior).some((row) => Object.hasOwn(row, "ObservedReadFlows"))
) fields.ObservedReadFlows = "Note";
for (const [name, type] of Object.entries(fields)) {
  const existing = schema.find((f) => f.InternalName === name);
  if (existing && existing.TypeAsString !== type) {
    throw Error("Field conflict " + name);
  }
  if (!existing) {
    const choices = name === "DataRole"
      ? "<CHOICES>" +
        ["Primary", "Secondary", "Aggregate", "Unresolved"].map((s) =>
          "<CHOICE>" + s + "</CHOICE>"
        ).join("") + "</CHOICES>"
      : "";
    await send(name.toLowerCase(), base + "/fields/CreateFieldAsXml", {
      parameters: {
        SchemaXml: '<Field Name="' + name + '" StaticName="' + name +
          '" DisplayName="' + name + '" Type="' + type + '" RichText="FALSE">' +
          choices + "</Field>",
        Options: 8,
      },
    });
  }
}
const viewFields = [
  "Title",
  "DataRole",
  "DatasetSource",
  "ReadFlows",
  "WriteFlows",
  "BindingStatus",
  "DatasetScope",
  "DatasetUrl",
];
if (fields.ObservedReadFlows) viewFields.push("ObservedReadFlows");
const views = await c.all(base + "/views");
if (!views.some((v) => v.Title === "Used by")) {
  await send("view", base + "/views/add", {
    parameters: {
      Title: "Used by",
      ViewFields: viewFields,
      Query:
        '<OrderBy><FieldRef Name="DatasetScope"/><FieldRef Name="Title"/></OrderBy>',
      PersonalView: false,
      SetAsDefaultView: false,
      Paged: true,
      RowLimit: 100,
    },
  });
}
const view = await c.get(base + "/views/getbytitle('Used by')");
const viewRoute = base + "/views/getbytitle('Used by')/ViewFields";
let columns = await c.get(viewRoute);
if (
  fields.ObservedReadFlows &&
  !(columns.Items ?? columns.value ?? []).includes("ObservedReadFlows")
) {
  await send(
    "observed-reads-view-field",
    viewRoute + "/addviewfield('ObservedReadFlows')",
    {},
  );
  columns = await c.get(viewRoute);
}
const missing = viewFields.filter((k) =>
  !(columns.Items ?? columns.value ?? []).includes(k)
);
if (missing.length) throw Error("Missing view fields: " + missing.join(", "));
async function read() {
  const rows = [];
  let route = base + "/items?$select=Id,DatasetId," +
    Object.keys(fields).join(",") + "&$top=500";
  const seen = new Set();
  while (route) {
    if (seen.has(route)) throw Error("Repeated inventory page");
    seen.add(route);
    const page = await c.item(route);
    const records = page.results ?? page.value;
    if (!Array.isArray(records)) throw Error("Invalid inventory page");
    rows.push(...records);
    route = page.__next ?? page["@odata.nextLink"] ?? page["odata.nextLink"];
  }
  return rows;
}
function compare(rows, phase = "preflight") {
  if (
    rows.length !== Object.keys(plan.rows).length ||
    new Set(rows.map((r) => r.DatasetId.toLowerCase())).size !== rows.length
  ) throw Error("Inventory changed during " + phase);
  const changes = [];
  for (const r of rows) {
    const want = plan.rows[r.DatasetId.toLowerCase()];
    if (!want) throw Error("Dataset absent from manifest");
    const patch = {};
    for (const k of Object.keys(fields)) {
      if ((r[k] ?? null) === (want[k] ?? null)) continue;
      if ((r[k] ?? null) !== (prior[r.DatasetId.toLowerCase()]?.[k] ?? null)) {
        throw Error(
          "Existing catalogue value requires reconciliation " + r.Id + " " + k,
        );
      }
      patch[k] = want[k] ?? null;
    }
    if (Object.keys(patch).length) changes.push({ r, patch });
  }
  return changes;
}
const changes = compare(await read());
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
if (compare(rows, "readback").length) throw Error("Row readback mismatch");
fs.writeFileSync(
  receipt,
  JSON.stringify({
    verified: rows.length,
    changed: changes.length,
    view: view.ServerRelativeUrl,
    flows: plan.flowCount,
    unresolvedActions: plan.unresolvedActions.length,
  }),
  { flag: "wx", mode: 0o600 },
);
console.log(
  "Verified",
  rows.length,
  "catalogue entries;",
  changes.length,
  "changed",
);
