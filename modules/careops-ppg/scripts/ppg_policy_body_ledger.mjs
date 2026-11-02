// Provision the additive catalogue ledger and view through an existing qualified adapter.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
const [adapter, receipt, listId] = process.argv.slice(2);
if (![adapter, receipt].every(p => p && path.resolve(p).split(path.sep).includes(".local")) ||
    fs.existsSync(receipt) || listId && !/^[a-f0-9-]{36}$/i.test(listId)) {
  throw Error("Supply private adapter/new receipt paths and optional exact list ID");
}
const c = await (await import(pathToFileURL(path.resolve(adapter)))).connect();
const base = listId ? `lists(guid'${listId}')` : "lists/getbytitle('PPG Catalogue')";
const definitions = JSON.parse(fs.readFileSync(new URL("../config/whole-product-installation.json", import.meta.url)))
  .objects.find(o => o.key === "catalogue").fields.filter(f => f.name.startsWith("BodyIdentity"));
if (definitions.length !== 3) throw Error("Ledger schema incomplete");
const send = (key, route, payload) => c.send({key, route, payload,
  payloadSHA256: createHash("sha256").update(JSON.stringify(payload)).digest("hex")});
const fields = await c.all(base + "/fields?$select=InternalName,TypeAsString");
for (const f of definitions) {
  const current = fields.find(v => v.InternalName === f.name);
  if (current) {
    if (current.TypeAsString !== f.type) throw Error("Ledger field type conflict");
  } else {
    await send("body-ledger-bootstrap-" + f.name.toLowerCase(), base + "/fields/CreateFieldAsXml",
      {parameters: {SchemaXml: f.xml, Options: 8}});
  }
}
const title = "Policy body identities";
const columns = ["LinkTitle", "DocumentUID", "sourceDocumentId", "BodyIdentityState", "BodyIdentityEvidence", "BodyIdentityJSON"];
const query = '<GroupBy Collapse="TRUE"><FieldRef Name="BodyIdentityState"/></GroupBy><OrderBy><FieldRef Name="Title"/></OrderBy>';
if (!(await c.all(base + "/views?$select=Title")).some(v => v.Title === title)) {
  await send("body-ledger-bootstrap-view", base + "/views/add", {parameters: {
    Title: title, ViewFields: columns, PersonalView: false, SetAsDefaultView: false,
    Paged: true, RowLimit: 100,
    Query: query}});
}
const view = base + "/views/getbytitle('Policy body identities')";
const saved = await c.get(view), actual = (await c.get(view + "/ViewFields")).Items;
const canonicalQuery = value => (value || "").replace(/>\s+</g, "><").replace(/\s+\/>/g, "/>").trim();
if (!columns.every(f => actual.includes(f)) || canonicalQuery(saved.ViewQuery) !== canonicalQuery(query)) {
  throw Error("Ledger view differs; preserve existing view for reconciliation");
}
const finalFields = await c.all(base + "/fields?$select=InternalName,TypeAsString");
if (!definitions.every(f => finalFields.some(v => v.InternalName === f.name && v.TypeAsString === f.type))) {
  throw Error("Ledger schema readback differs");
}
fs.writeFileSync(receipt, JSON.stringify({view: saved.ServerRelativeUrl, columns, fields: definitions.map(f => f.name)}),
  {flag: "wx", mode: 0o600});
console.log("Policy body ledger schema and view verified");
