"""Generate source-only per-flow documentation, contracts and diagrams from a ZIP."""
import argparse, hashlib, json, re, zipfile
from pathlib import Path
from xml.sax.saxutils import quoteattr
N="http://www.omg.org/spec/BPMN/20100524/MODEL"

TASKS=[
"Verify exported flow source identity SHA and active owner",
"Inspect nested actions conditions runAfter retries and standard connectors",
"List all source field paths types array cardinalities and data rights",
"Implement Bronze full rights-compliant archived source and pagination evidence",
"Implement Silver typed canonical mapping and field provenance",
"Implement Gold review-gated reconciled views and label dictionary",
"Implement Platinum traceable intelligence and uncertainty",
"Reconcile semantic model dashboard scorecard and paginated report bindings",
"Test null many duplicate stale partial denied replay rollback and privacy",
"Run source gates then seek separately authorised native readback"]
def slug(filename):
    name=re.sub(r"-[0-9a-f]{8}-[0-9a-f-]{27,}","",Path(filename).stem.lower())
    return re.sub(r"[^a-z0-9]+","-",name).strip("-")
def paths(node,prefix=""):
    if isinstance(node,dict):
        for k,v in node.items():
            if k.startswith("item/") or re.fullmatch(r"field_\d+",k): yield prefix+"/"+k
            if k=="select" and isinstance(v,dict):
                for f in v:yield prefix+"/select:"+f
            yield from paths(v,prefix+"/"+k)
    elif isinstance(node,list):
        for i,v in enumerate(node):yield from paths(v,prefix+"/"+str(i))
def mermaid(actions):
    lines=["flowchart TD","  S[Trigger]"]
    for i,a in enumerate(actions,1):
        label=re.sub(r"[^a-zA-Z0-9 _/:-]","",a)[:70]
        lines.extend((f'  N{i}["{label}"]',f'  {"S" if i==1 else "N"+str(i-1)} --> N{i}'))
    lines.append("  E[End]")
    lines.append(f'  {"N"+str(len(actions)) if actions else "S"} --> E')
    return "\n".join(lines)+"\n"
def bpmn(actions,key):
    """Emit BPMN XML with safely quoted attributes, without parsing XML."""
    q = quoteattr
    prefix = '<bpmn:'
    nodes = [("Start", "startEvent", "Trigger")] + [
        (f"Task{i}", "task", x[:80]) for i, x in enumerate(actions, 1)
    ] + [("End", "endEvent", "End")]
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<bpmn:definitions xmlns:bpmn=' + q(N) + ' id=' + q("Defs_" + key)
        + ' targetNamespace=' + q("https://github.com/edithatogo/careops/rims") + '>',
        '<bpmn:process id=' + q("Process_" + key) + ' isExecutable="false">',
    ]
    for i, (ident, kind, name) in enumerate(nodes):
        lines.append(prefix + kind + ' id=' + q(ident) + ' name=' + q(name) + '>')
        if i:
            lines.append('<bpmn:incoming>Seq' + str(i) + '</bpmn:incoming>')
        if i < len(nodes) - 1:
            lines.append('<bpmn:outgoing>Seq' + str(i + 1) + '</bpmn:outgoing>')
        lines.append('</bpmn:' + kind + '>')
    for i in range(len(nodes) - 1):
        lines.append('<bpmn:sequenceFlow id=' + q(f"Seq{i + 1}")
                     + ' sourceRef=' + q(nodes[i][0])
                     + ' targetRef=' + q(nodes[i + 1][0]) + '/>')
    lines.extend(['</bpmn:process>', '</bpmn:definitions>'])
    return "\n".join(lines) + "\n"

def generate(zip_path,outdir):
    target=Path(outdir);target.mkdir(parents=True,exist_ok=True)
    seen=set();manifest=[]
    with zipfile.ZipFile(zip_path) as z:
        names=sorted(n for n in z.namelist() if n.startswith("Workflows/") and n.endswith(".json"))
        if not names or len(set(names))!=len(names):raise ValueError("invalid workflow archive")
        for name in names:
            if z.getinfo(name).file_size>10_000_000:raise ValueError("oversize flow")
            raw=z.read(name);data=json.loads(raw)
            definition=data["properties"]["definition"]
            key=slug(name)
            if key in seen:raise ValueError("duplicate flow key")
            seen.add(key)
            out=target/key;out.mkdir(parents=True,exist_ok=True)
            actions=list(definition.get("actions",{}));sha=hashlib.sha256(raw).hexdigest()
            dictionary={"schema":"careops-rims.flow-dictionary/1","flow_key":key,"source_sha256":sha,
                "fields":[{"path":p,"type":"unverified","nullable":"unknown","bronze":"retain","silver":"pending","gold":"pending","platinum":"pending"} for p in sorted(set(paths(definition)))],
                "trigger_names":list(definition.get("triggers",{}))}
            moscow={"Must":["Complete permitted source payload","Provenance and rights","No premium core","Human decision safety"],"Should":["Display dictionary","Coverage and quality metrics"],"Could":["Cross-vertical intelligence"],"Wont_now":["Unapproved extra sources","Native writes without authorised readback"]}
            tasks=[{"id":key+"-"+str(i).zfill(2),"status":"pending","instruction":t,"evidence":"input SHA, output SHA, command, exit status, acceptance level"} for i,t in enumerate(TASKS,1)]
            for filename,document in (("dictionary.json",dictionary),("moscow.json",moscow),("tasks.json",tasks)):
                (out/filename).write_text(json.dumps(document,indent=2)+"\n",encoding="utf-8")
            (out/"design.md").write_text("# "+key+"\n\nExport SHA: "+sha+"\n\nStatic top-level source actions, not confirmed execution order:\n\n"+"\n".join("- "+a for a in actions)+"\n\nBronze: complete rights-permitted source; Silver: typed identity and field lineage; Gold: reviewed business views; Platinum: evidenced intelligence with uncertainty. Native operation separately gated.\n",encoding="utf-8")
            overview=actions[:24]+(["Remaining actions: inspect original"] if len(actions)>24 else [])
            (out/"process.mmd").write_text(mermaid(overview),encoding="utf-8")
            (out/"process.bpmn").write_text(bpmn(overview,re.sub(r"[^A-Za-z0-9_]","_",key)),encoding="utf-8")
            manifest.append({"key":key,"source_file":name,"sha256":sha,"top_level_actions":len(actions)})
    (target/"manifest.json").write_text(json.dumps({"schema":"careops-rims.generated-flow-pack/1","flow_count":len(manifest),"flows":manifest,"runtime_parity":False},indent=2)+"\n")
    return len(manifest)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("export_zip");p.add_argument("output")
    a=p.parse_args();print("generated",generate(a.export_zip,a.output))
