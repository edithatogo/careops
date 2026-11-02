// Usage: node scripts/ppg_commission_dataset_directory.mjs ADAPTER BINDINGS RECEIPT [--publish]
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { catalogue, ensureDirectoryPage } from "./ppg_dataset_catalogue.mjs";
const [adapter, bindings, receipt, option] = process.argv.slice(2);
if (
  ![adapter, bindings, receipt].every((v) =>
    v && path.resolve(v).split(path.sep).includes(".local")
  ) || fs.existsSync(receipt) || option && option !== "--publish"
) throw Error("Supply private adapter, bindings and new receipt paths");
const client = await (await import(pathToFileURL(path.resolve(adapter))))
  .connect();
const result = await catalogue(client, JSON.parse(fs.readFileSync(bindings)));
const page = await ensureDirectoryPage(client, result, {
  publish: option === "--publish",
});
fs.writeFileSync(
  receipt,
  JSON.stringify(
    { page, created: result.created, verified: result.verified },
    null,
    2,
  ),
  { flag: "wx", mode: 0o600 },
);
console.log(
  JSON.stringify({
    datasets: result.verified,
    created: result.created,
    pageVersion: page.version,
  }),
);
