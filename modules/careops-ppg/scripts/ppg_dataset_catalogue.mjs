// Inventory physical SharePoint datasets independently of Power Platform component IDs.
import { createHash, randomUUID } from "node:crypto";
export const title = "PPG Dataset Catalogue";
const fields = {
  DatasetId: "Text",
  ProductKey: "Text",
  DatasetScope: "Text",
  DatasetKind: "Text",
  DatasetUrl: "URL",
  VersionHistory: "Boolean",
};
const digest = (bytes) => createHash("sha256").update(bytes).digest("hex");
async function send(client, key, route, payload, extra = {}) {
  const bytes = Buffer.isBuffer(payload)
    ? payload
    : Buffer.from(JSON.stringify(payload));
  return client.send({
    key,
    route,
    payload,
    payloadSHA256: digest(bytes),
    ...extra,
  });
}
export function classify(list, bindings) {
  const match = Object.entries(bindings).find(([, v]) =>
    v.id.toLowerCase() === list.Id.toLowerCase()
  );
  if (match || list.Title === title) {
    return [match?.[0] ?? "dataset-catalogue", "Product"];
  }
  if (/install/i.test(list.Title)) return ["", "Installation"];
  if (/restore|recovery/i.test(list.Title)) return ["", "Recovery"];
  if (/qualification|fictional|pilot|fixture|sample/i.test(list.Title)) {
    return ["", "Qualification"];
  }
  return ["", "Supporting"];
}
export async function catalogue(client, bindings) {
  const query =
    "lists?$select=Id,Title,BaseTemplate,Hidden,EnableVersioning,HasUniqueRoleAssignments,RootFolder/ServerRelativeUrl&$expand=RootFolder&$top=5000";
  let inventory = await client.all(query);
  let list = inventory.find((v) => v.Title === title);
  if (!list) {
    await send(client, "dataset-catalogue-list", "lists", {
      Title: title,
      Description:
        "Directory of PPG lists and libraries. Open the dataset for current records.",
      BaseTemplate: 100,
      EnableVersioning: true,
      EnableAttachments: false,
    });
    inventory = await client.all(query);
    list = inventory.find((v) => v.Title === title);
  }
  if (!list?.EnableVersioning || list.BaseTemplate !== 100) {
    throw Error("Dataset catalogue schema conflict");
  }
  const base = "lists(guid'" + list.Id + "')";
  const existing = await client.all(
    base +
      "/fields?$select=InternalName,TypeAsString,Indexed,EnforceUniqueValues",
  );
  for (const [name, type] of Object.entries(fields)) {
    const f = existing.find((v) => v.InternalName === name);
    if (f) {
      if (
        f.TypeAsString !== type ||
        (name === "DatasetId" && !f.EnforceUniqueValues)
      ) throw Error("Dataset field conflict " + name);
      continue;
    }
    const xml = '<Field Name="' + name + '" StaticName="' + name +
      '" DisplayName="' + name + '" Type="' + type + '" ' +
      (name === "DatasetId"
        ? 'Indexed="TRUE" EnforceUniqueValues="TRUE" Required="TRUE"'
        : "") +
      "/>";
    await send(
      client,
      "catalogue-field-" + name.toLowerCase(),
      base + "/fields/CreateFieldAsXml",
      { parameters: { SchemaXml: xml, Options: 8 } },
    );
  }
  const viewName = "Dataset directory";
  if (!(await client.all(base + "/views")).some((v) => v.Title === viewName)) {
    await send(client, "catalogue-view", base + "/views/add", {
      parameters: {
        Title: viewName,
        ViewFields: [
          "Title",
          "DatasetScope",
          "DatasetKind",
          "DatasetUrl",
          "ProductKey",
          "VersionHistory",
        ],
        Query:
          '<OrderBy><FieldRef Name="DatasetScope"/><FieldRef Name="Title"/></OrderBy>',
        PersonalView: false,
        SetAsDefaultView: true,
        Paged: true,
        RowLimit: 100,
      },
    });
  }
  const ids = new Set(Object.values(bindings).map((b) => b.id.toLowerCase()));
  const targets = inventory.filter((v) =>
    !v.Hidden && [100, 101].includes(v.BaseTemplate) &&
    (/^PPG\b/i.test(v.Title) || ids.has(v.Id.toLowerCase()))
  );
  const site = client.c.siteUrl, origin = new URL(site).origin;
  const desired = targets.map((v) => {
    const [key, scope] = classify(v, bindings);
    const path = v.RootFolder.ServerRelativeUrl.split("/").map(
      encodeURIComponent,
    ).join("/");
    return {
      Title: v.Title,
      DatasetId: v.Id,
      ProductKey: key || null,
      DatasetScope: scope,
      DatasetKind: v.BaseTemplate === 101 ? "Library" : "List",
      DatasetUrl: { Url: origin + path, Description: "Open dataset" },
      VersionHistory: v.EnableVersioning,
    };
  });
  const compatible = (a, b) =>
    Object.keys(b).every((k) =>
      k === "DatasetUrl"
        ? decodeURI(a[k]?.Url ?? "") === decodeURI(b[k].Url)
        : a[k] === b[k] || (!a[k] && !b[k])
    );
  const before = await client.all(base + "/items?$top=5000");
  const missing = [];
  for (const row of desired) {
    const matches = before.filter((v) => v.DatasetId === row.DatasetId);
    if (matches.length > 1 || matches.length && !compatible(matches[0], row)) {
      throw Error("Existing dataset row needs review: " + row.Title);
    }
    if (!matches.length) missing.push(row);
  }
  // Bounded create-only batches. Uncertain replies require a fresh inventory before resumption.
  for (let i = 0; i < missing.length; i += 20) {
    const group = missing.slice(i, i + 20),
      boundary = "batch_" + digest(JSON.stringify(group)).slice(0, 24),
      parts = [];
    for (const row of group) {
      const cs = "changeset_" + row.DatasetId;
      parts.push(
        "--" + boundary,
        "Content-Type: multipart/mixed; boundary=" + cs,
        "",
        "--" + cs,
        "Content-Type: application/http",
        "Content-Transfer-Encoding: binary",
        "",
        "POST " + site + "/_api/web/" + base + "/items HTTP/1.1",
        "Content-Type: application/json;odata=nometadata",
        "Accept: application/json;odata=nometadata",
        "",
        JSON.stringify(row),
        "--" + cs + "--",
      );
    }
    parts.push("--" + boundary + "--", "");
    const response = await send(
      client,
      boundary.replace("_", "-"),
      site + "/_api/$batch",
      Buffer.from(parts.join("\r\n")),
      { contentType: "multipart/mixed; boundary=" + boundary },
    );
    const statuses = [...String(response).matchAll(/HTTP\/1\.[01] (\d{3})/g)]
      .map((m) => m[1]);
    if (statuses.length !== group.length || statuses.some((s) => s !== "201")) {
      throw Error("Reconcile dataset batch outcomes");
    }
    if (i + 20 < missing.length) await new Promise((r) => setTimeout(r, 10000));
  }
  const after = await client.all(base + "/items?$top=5000");
  for (const row of desired) {
    const m = after.filter((v) => v.DatasetId === row.DatasetId);
    if (m.length !== 1 || !compatible(m[0], row)) {
      throw Error("Dataset readback: " + row.Title);
    }
  }
  return { list, desired, created: missing.length, verified: desired.length };
}

export function directoryHtml(records, viewUrl) {
  const esc = (s) =>
    String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(
      ">",
      "&gt;",
    ).replaceAll('"', "&quot;");
  const groups = [
    "Product",
    "Supporting",
    "Installation",
    "Recovery",
    "Qualification",
  ];
  const parts = [
    '<h2>PPG dataset directory</h2><p><a href="' + esc(viewUrl) +
    '">Browse the live catalogue in Microsoft Lists</a>. Each link opens the original dataset with its existing SharePoint permissions.</p>',
  ];
  for (const scope of groups) {
    const rows = records.filter((r) => r.DatasetScope === scope).sort((a, b) =>
      a.Title.localeCompare(b.Title)
    );
    parts.push("<h3>" + scope + " (" + rows.length + ")</h3><ul>");
    for (const r of rows) {
      parts.push(
        '<li><a href="' + esc(r.DatasetUrl.Url) + '">' + esc(r.Title) +
          "</a> — " + esc(r.DatasetKind) + "</li>",
      );
    }
    parts.push("</ul>");
  }
  return parts.join("");
}

export async function ensureDirectoryPage(
  client,
  result,
  { publish = false } = {},
) {
  const name = "PPG-Dataset-Catalogue.aspx",
    site = client.c.siteUrl,
    origin = new URL(site).origin;
  const pages = await client.get(
    "lists/getbytitle('Site Pages')?$select=Id,RootFolder/ServerRelativeUrl&$expand=RootFolder",
  );
  const path = pages.RootFolder.ServerRelativeUrl + "/" + name;
  const file = "GetFileByServerRelativePath(decodedurl='" +
    path.replaceAll("'", "''") + "')";
  const view = await client.get(
    "lists(guid'" + result.list.Id +
      "')/DefaultView?$select=ServerRelativeUrl,Title",
  );
  const viewUrl = origin + view.ServerRelativeUrl;
  let page, created = false;
  try {
    page = await client.get(file + "/ListItemAllFields");
  } catch (error) {
    if (error.message !== "HTTP_404") throw error;
    await send(client, "directory-page", site + "/_api/sitepages/pages", {
      PageLayoutType: "Article",
      Name: name,
      Title: title,
      PromotedState: 0,
    });
    page = await client.get(file + "/ListItemAllFields");
    created = true;
  }
  if (page.Title !== title) throw Error("Directory page name already in use");
  const route = "lists(guid'" + pages.Id + "')/items(" + page.Id + ")";
  const item = await client.item(route);
  if (created) {
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
        layoutIndex: 1,
      },
    }).replaceAll('"', "&quot;");
    const html = directoryHtml(result.desired, viewUrl);
    await send(client, "directory-page-body", route, {
      CanvasContent1:
        '<div><div data-sp-canvascontrol="" data-sp-canvasdataversion="1.0" data-sp-controldata="' +
        control + '"><div data-sp-rte="">' + html + "</div></div></div>",
    }, { etag: item.__metadata.etag });
  }
  const saved = await client.get(route);
  const decoded = saved.CanvasContent1.replace(
    /&#(\d+);/g,
    (_, n) => String.fromCharCode(Number(n)),
  ).replaceAll("&quot;", '"').replaceAll("&lt;", "<").replaceAll("&gt;", ">").replaceAll("&amp;", "&");
  for (const r of result.desired) {
    if (
      !decoded.includes(r.Title) ||
      ![r.DatasetUrl.Url, new URL(r.DatasetUrl.Url).pathname].some((url) =>
        decodeURI(decoded).includes(decodeURI(url))
      )
    ) {
      throw Error(
        "Directory page differs; preserve existing edits and reconcile " +
          r.Title,
      );
    }
  }
  let pin = await client.get(
    file + "?$select=UIVersionLabel,Level,CheckOutType",
  );
  if (publish && pin.Level !== 1) {
    if (!created) {
      throw Error("Existing draft requires explicit revision review");
    }
    const method = pin.CheckOutType === 2
      ? "/Publish(comment='Dataset directory')"
      : "/CheckIn(comment='Dataset directory',checkintype=1)";
    await send(client, "directory-publish", file + method, {});
    pin = await client.get(file + "?$select=UIVersionLabel,Level,CheckOutType");
    if (pin.Level !== 1) throw Error("Directory publication pending");
  }
  return {
    page: origin + encodeURI(path),
    list: viewUrl,
    published: pin.Level === 1,
    version: pin.UIVersionLabel,
    count: result.verified,
  };
}
