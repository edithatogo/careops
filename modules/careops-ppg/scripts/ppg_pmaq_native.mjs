// Create-only importer for the bounded, fictional PGY1 package.
import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
const [adapter, packageFile, bindingFile, receipt] = process.argv.slice(2);
if (
  ![adapter, packageFile, bindingFile, receipt].every((f) =>
    f && path.resolve(f).split(path.sep).includes(".local")
  ) || fs.existsSync(receipt)
) throw Error("Explicit private inputs and new receipt required");
const packet = JSON.parse(fs.readFileSync(packageFile)),
  binding = JSON.parse(fs.readFileSync(bindingFile));
if (
  packet.fixtureOnly !== true || packet.schemaVersion !== 1 ||
  packet.briefs.length !== 2
) throw Error("Fictional portability package required");
const plan = packet.rows, side = binding.journalPrefix;
if (!/^[a-z0-9-]+$/.test(side)) throw Error("Explicit journal prefix required");
const hash = (b) => createHash("sha256").update(b).digest("hex");
const c = await (await import(pathToFileURL(path.resolve(adapter)))).connect();
if (binding.site !== c.c.siteUrl) throw Error("Wrong bound SharePoint site");
async function target(kind) {
  const id = binding.targets[kind];
  if (!/^[0-9a-f-]{36}$/i.test(id)) {
    throw Error("Explicit list identity required: " + kind);
  }
  const list = await c.get(
    "lists(guid'" + id +
      "')?$select=Id,BaseTemplate,EnableVersioning,RootFolder/ServerRelativeUrl&$expand=RootFolder",
  );
  if (
    list.Id !== id || !list.EnableVersioning ||
    list.BaseTemplate !== (kind === "library" ? 101 : 100)
  ) throw Error("Destination schema mismatch");
  return list;
}
const keys = {
    framework: "FrameworkKey",
    requirement: "RequirementKey",
    context: "ReviewContextKey",
    evidence: "EvidenceVersionKey",
    mapping: "MappingKey",
    assessment: "AssessmentKey",
    decision: "DecisionKey",
    event: "DecisionEventKey",
  },
  refs = {},
  verified = {};
async function post(key, route, payload, extra = {}) {
  return c.send({
    key: side + "-" + key,
    route,
    payload,
    payloadSHA256: hash(
      Buffer.isBuffer(payload) ? payload : Buffer.from(JSON.stringify(payload)),
    ),
    ...extra,
  });
}
const er = await target("evidence"),
  shared = "fixture:ac19-quality-20261030:evidence:v1";
const found = await c.all(
  "lists(guid'" + er.Id + "')/items?$filter=" +
    encodeURIComponent("EvidenceVersionKey eq '" + shared + "'"),
);
if (found.length !== 1) throw Error("Shared evidence missing");

const lib = await target("library"), folder = lib.RootFolder.ServerRelativeUrl;
for (let i = 1; i <= 2; i++) {
  const bytes = Buffer.from(
      JSON.stringify(packet.briefs[i - 1], null, 2) + "\n",
    ),
    name = "PPG-fictional-PGY1-brief-v" + i + "-20261101.json",
    r = "GetFileByServerRelativePath(decodedurl='" + folder + "/" + name + "')";
  let meta;
  try {
    meta = await c.get(
      r + "?$select=UniqueId,UIVersionLabel,ServerRelativeUrl",
    );
  } catch (e) {
    if (e.message !== "HTTP_404") throw e;
    await post(
      "file-" + i,
      "GetFolderByServerRelativePath(decodedurl='" + folder +
        "')/Files/AddUsingPath(decodedurl='" + name + "',overwrite=false)",
      bytes,
    );
    meta = await c.get(
      r + "?$select=UniqueId,UIVersionLabel,ServerRelativeUrl",
    );
  }
  if (!(await c.get(r + "/$value", true)).equals(bytes)) {
    throw Error("File bytes differ");
  }
  Object.assign(plan.evidence[i - 1], {
    SourceSystem: "SharePoint",
    SourceItemKey: "fileUniqueId:" + meta.UniqueId,
    ExactVersion: meta.UIVersionLabel,
    SourceURI: new URL(c.c.siteUrl).origin + meta.ServerRelativeUrl,
    OData__x0053_HA256: hash(bytes),
    ObservedAt: "2026-11-01T00:00:00Z",
  });
}
const coherent = (actual, r) =>
  Object.entries(r).every(([k, v]) =>
    actual[k] === v || v === null && actual[k] === ""
  );
for (const [kind, rows] of Object.entries(plan)) {
  const list = await target(kind),
    base = "lists(guid'" + list.Id + "')",
    key = keys[kind];
  const rules = (await c.rules(list.Id)).value;
  if (rules.length) throw Error("Unexpected native rule " + kind);
  const fields = await c.all(
    base + "/fields?$select=InternalName,EntityPropertyName,TypeAsString",
  );
  const props = new Set(
    fields.map((f) => f.EntityPropertyName ?? f.InternalName),
  );
  const select = () =>
    c.all(
      base + "/items?$filter=" + encodeURIComponent(
        rows.map((r) => key + " eq '" + r[key] + "'").join(" or "),
      ),
    );
  const before = await select();
  let creates = 0;
  for (const r of rows) {
    if (kind === "decision") {
      r.SourceEvidenceVersionLinkId = refs[r.SourceEvidenceVersionKey];
      r.ReviewContextLinkId = refs[r.ReviewContextKey];
    }
    if (kind === "event") r.DecisionLinkId = refs[r.DecisionKey];
    if (kind === "mapping" && r.EvidenceVersionKey.includes("brief:")) {
      const evidence = plan.evidence.find((e) =>
        e.EvidenceVersionKey === r.EvidenceVersionKey
      );
      if (!evidence) throw Error("Missing evidence version " + r.EvidenceVersionKey);
      r.DocumentVersion = evidence.ExactVersion;
      r.EvidenceRef = evidence.SourceURI;
    }
    for (const k of Object.keys(r)) {
      if (!props.has(k) && !(k.endsWith("Id") && props.has(k.slice(0, -2)))) {
        throw Error("Field unavailable " + kind + " " + k);
      }
    }
    const found = before.filter((a) => a[key] === r[key]);
    if (found.length > 1 || found.length && !coherent(found[0], r)) {
      throw Error("Existing row conflict " + kind + " " + r[key]);
    }
    if (!found.length) {
      await post("row-" + hash(r[key]).slice(0, 20), base + "/items", r);
      creates++;
    }
  }
  const after = await select();
  for (const r of rows) {
    const m = after.filter((a) => a[key] === r[key]);
    if (m.length !== 1 || !coherent(m[0], r)) {
      const a = m[0] ?? {};
      throw Error(
        "Readback " + kind + " " +
          Object.keys(r).filter((k) => a[k] !== r[k]).join(","),
      );
    }
    refs[r[key]] = m[0].Id;
  }
  verified[kind] = { listId: list.Id, rows: after, creates };
  console.log(side, kind, after.length);
}
fs.writeFileSync(
  receipt,
  JSON.stringify({ verified, sharedEvidence: shared }, null, 2),
  { flag: "wx", mode: 0o600 },
);
