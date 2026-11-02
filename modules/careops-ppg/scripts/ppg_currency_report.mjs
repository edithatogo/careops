// Maintain a versioned coverage page; the grouped view provides live drill-down.
import { createHash, randomUUID } from "node:crypto";
const hash = (s) => createHash("sha256").update(s).digest("hex");
export async function coveragePage(c, send, reportPath, rows, prior) {
  const title = "Policy currency disposition coverage",
    name = "PPG-Policy-Currency-Coverage.aspx";
  const pages = await c.get(
    "lists/getbytitle('Site Pages')?$select=Id,RootFolder/ServerRelativeUrl&$expand=RootFolder",
  );
  const path = pages.RootFolder.ServerRelativeUrl + "/" + name;
  const file = "GetFileByServerRelativePath(decodedurl='" +
    path.replaceAll("'", "''") + "')";
  let page, created = false;
  try {
    page = await c.get(file + "/ListItemAllFields");
  } catch (e) {
    if (e.message !== "HTTP_404") throw e;
    await send("coverage-page", c.c.siteUrl + "/_api/sitepages/pages", {
      PageLayoutType: "Article",
      Name: name,
      Title: title,
      PromotedState: 0,
    });
    page = await c.get(file + "/ListItemAllFields");
    created = true;
  }
  if (page.Title !== title) throw Error("Coverage page name conflict");
  const route = "lists(guid'" + pages.Id + "')/items(" + page.Id + ")";
  const row = await c.item(route);
  const total = rows.length,
    done =
      rows.filter((r) => String(r.CurrencyDisposition ?? "").trim()).length;
  const summary = done + " of " + total + " leads have a recorded disposition" +
    (total ? " (" + (100 * done / total).toFixed(1) + "%)." : ".");
  if (!created && (!prior || hash(row.CanvasContent1) !== prior.bodyHash)) {
    throw Error("Reconcile existing coverage page before refresh");
  }
  let expectedHash = prior?.bodyHash;
  if (created || prior.summary !== summary) {
    const control = JSON.stringify({
      controlType: 4,
      editorType: "CKEditor",
      id: randomUUID(),
      position: {
        controlIndex: 1,
        sectionFactor: 12,
        sectionIndex: 1,
        zoneIndex: 1,
        zoneId: randomUUID(),
      },
    }).replaceAll('"', "&quot;");
    const href = new URL(reportPath, c.c.siteUrl).pathname.replaceAll(
      "&",
      "&amp;",
    )
      .replaceAll('"', "&quot;");
    const html =
      '<div><div data-sp-canvascontrol="" data-sp-canvasdataversion="1.0" data-sp-controldata="' +
      control + '"><div data-sp-rte=""><h2>Disposition coverage</h2><p>' +
      summary + "</p><p>" + (total - done) +
      ' await triage. All source leads are included, including those without a policy match.</p><p><a href="' +
      href + '">Open leads grouped by disposition</a></p></div></div></div>';
    await send(
      "coverage-body-" + hash(row.__metadata.etag + summary).slice(0, 20),
      route,
      { CanvasContent1: html },
      { etag: row.__metadata.etag },
    );
    const draft = await c.item(route);
    const decoded = draft.CanvasContent1.replaceAll("&#123;", "{").replaceAll(
      "&#125;",
      "}",
    ).replaceAll("&#58;", ":");
    if (
      decoded !== html ||
      Number(draft.__metadata.etag.replaceAll('"', "")) !==
        Number(row.__metadata.etag.replaceAll('"', "")) + 1
    ) {
      throw Error("Coverage readback mismatch");
    }
    expectedHash = hash(draft.CanvasContent1);
    const state = await c.get(file + "?$select=CheckOutType");
    const current = await c.item(route);
    if (
      current.__metadata.etag !== draft.__metadata.etag ||
      hash(current.CanvasContent1) !== expectedHash
    ) throw Error("Coverage draft changed before publication");
    await send(
      "coverage-publish-" + hash(draft.__metadata.etag + summary).slice(0, 20),
      file +
        (state.CheckOutType === 2
          ? "/Publish(comment='Disposition coverage')"
          : "/CheckIn(comment='Disposition coverage',checkintype=1)"),
      {},
    );
  }
  const saved = await c.item(route),
    published = await c.get(file + "?$select=Level,UIVersionLabel");
  if (published.Level !== 1 || hash(saved.CanvasContent1) !== expectedHash) {
    throw Error("Coverage publication incomplete");
  }
  return {
    path,
    summary,
    bodyHash: hash(saved.CanvasContent1),
    version: published.UIVersionLabel,
  };
}
