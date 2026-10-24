/* Clinical F06 Standard Office Script: no workbook reads/writes or network.
 * PPG v14's qualified UTF-8/SHA-256/base64/ZIP32 helpers are retained below.
 * Maintained template compilation is one-time; all per-run population is here.
 */
interface ZipEntry { name: string; bytes: number[]; }
interface TemplatePart { path: string; base64: string; sha256: string; }
interface AgendaTemplate { kind: string; templateSHA256: string; manifestPin: string; mainXml: string; sections: string[]; parts: TemplatePart[]; }
interface Hold { record_id:string;status:string;source_text:string;history:string[];owner_claim:string|null;due_date:string|null;due_label:string|null;review_date:string|null;response_ref:string|null;source_link?:AgendaLink; }
interface Snapshot { synthetic_only:boolean;meeting_id:string;source_id:string;source_revision:string;records:Hold[]; }
interface AgendaRequest { kind:string;snapshotJson:string;meetingDate:string;occurrence:string;outputRevision:number;sourceVersion:string;sourceModified:string;flowId:string;runId:string;createdAt:string;templateUniqueId:string;templateVersion:string; }
interface AgendaResult { schemaVersion:number;docxBase64:string;sha256:string;bytes:number;sourceSHA256:string;templateSHA256:string;manifestPin:string;outputRevision:number;includedRecordIDs:string[];wordGenerationPerformed:boolean;sourceWrites:boolean;sent:boolean; }
const EXPECTED_MANIFEST_PIN='3f6f6523035aca6c942d48ac230af2883d1db1eb113e521c1aeca963c6e0a1ea';
const MAX_RAW_BYTES=2000000, MAX_WIRE_BYTES=4000000;
interface AgendaLink { label:string;url:string;id:string;version:string; }
interface SelectedAgenda {
  schemaVersion:number;meeting_id:string;meeting_date:string;timezone:string;
  calendar:AgendaLink;calendarStart:string;calendarEnd:string;
  source:AgendaLink;source_revision:string;source_modified:string;
  sections:string[];records:Hold[];papers:AgendaLink[];minutes:AgendaLink[];
  history:string[];scope:string;synthetic_only:boolean;
}
interface SelectedAgendaRequest extends AgendaRequest { selectionJson:string; }
function main(workbook: ExcelScript.Workbook, jobJson:string, membersJson:string):AgendaResult {
  if(utf8(JSON.stringify({jobJson,membersJson})).length>MAX_WIRE_BYTES)throw Error('request_limit');
  const kind:string=JSON.parse(jobJson).kind;
  return kind==='clinical-agenda-selected-word-v2'
    ? selectedAgenda(jobJson,membersJson) : legacyAgenda(workbook,jobJson,membersJson);
}
function legacyAgenda(workbook: ExcelScript.Workbook, jobJson:string, membersJson:string):AgendaResult {
  if(utf8(JSON.stringify({jobJson,membersJson})).length>MAX_WIRE_BYTES)throw Error('request_limit');
  const job:AgendaRequest=JSON.parse(jobJson),t:AgendaTemplate=JSON.parse(membersJson),s:Snapshot=JSON.parse(job.snapshotJson);
  if(job.kind!=='clinical-agenda-word-v1'||job.meetingDate!=='2030-02-18'||job.occurrence!=='SYN-CYCLE-01-NEXT-2030-02-18'||!Number.isInteger(job.outputRevision)||job.outputRevision<1||!job.runId||!job.flowId||!job.templateUniqueId||!job.templateVersion)throw Error('request_identity_invalid');
  const ids=['SYN-A01','SYN-A02','SYN-OLD07'];
  if(!s.synthetic_only||s.meeting_id!==job.occurrence||s.source_revision!=='syn-cycle-next-20300218-r1'||s.records.length!==3||s.records.some((r,i)=>r.record_id!==ids[i]||r.status!=='unknown'||!r.source_text||!Array.isArray(r.history)))throw Error('source_contract_changed');
  if(t.kind!=='F06-word-template-v1'||t.parts.length>100||t.sections.length!==7)throw Error('template_shape_invalid');
  const pin=t.parts.map(p=>p.path+':'+p.sha256).join('\n')+'\n'+sha256(utf8(t.mainXml))+'\n'+sha256(utf8(JSON.stringify(t.sections)))+'\n'+t.templateSHA256;
  if(sha256(utf8(pin))!==EXPECTED_MANIFEST_PIN||t.manifestPin!==EXPECTED_MANIFEST_PIN)throw Error('template_contract_changed');
  const values:{[key:string]:string}={MeetingID:job.occurrence,MeetingDateTime:'18 February 2030 — Australia/Brisbane; date only, no booked time',DraftRevision:'WORD R'+job.outputRevision+' — unissued fictional draft',OccurrenceScope:'WHOLLY FICTIONAL TECHNICAL REHEARSAL. No meeting booking, participant, approval or new outcome.',PaperIdentity:'Native paper ID 00000000-0000-4000-8000-000000000104; observed native version 1.0. Review input only; no approved outcome.',SourceHistory:'Prior 4 February 2030 minutes/single register and R01–R04 remain SYN-CYCLE-01 history. Local history references (not cloud hyperlinks): docs/rehearsal-2026-09-12/run/02-fictional-minutes-and-register.docx and docs/rehearsal-2026-09-12/source.json. Existing current-pack links remain the access route.',SourceProvenance:'Source ID '+s.source_id+'; revision '+s.source_revision+'; cutoff 15 February 2030; native version '+job.sourceVersion+'; modified '+job.sourceModified+'. Included '+ids.join(', ')+'. Original history R01–R04 retained.',TemplateProvenance:'F06-word-agenda-seven-section-v1; template SHA256 '+t.templateSHA256+'; native template '+job.templateUniqueId+' version '+job.templateVersion+'.',RunProvenance:'Standard Excel Office Script fresh DOCX; flow '+job.flowId+'; run '+job.runId+'; generated '+job.createdAt+'; output revision '+job.outputRevision+'. Source and template unchanged; no approval or circulation.',OptionalContent:''};
  for(let i=0;i<7;i++)values['AgendaSection'+(i+1)]=t.sections[i];
  s.records.forEach((r,i)=>{values['ReviewHold'+(i+1)]=r.record_id+' — unresolved review hold\nRecorded status: '+r.status+'. No new issue, assignment or closure.\nOriginal narrative: '+r.source_text+'\nHistory: '+JSON.stringify(r.history)+'\nOriginal owner claim: '+(r.owner_claim||'not established')+'; original due: '+(r.due_date||r.due_label||'not established')+'; original review: '+(r.review_date||'not established')+'\nResponse reference: '+(r.response_ref||'none recorded')+'. Unknown remains unknown; source claims are not current authority.';});
  const links:{[key:string]:{label:string;url:string}}={PaperLink:{label:'Selected fictional paper',url:'https://fictional-example.sharepoint.com/teams/Fictional/_layouts/15/Doc.aspx?sourcedoc=%7B00000000-0000-4000-8000-000000000104%7D&action=view'},SourceLink:{label:'Existing fictional source snapshot — row 4',url:'https://fictional-example.sharepoint.com/teams/Fictional/_layouts/15/listform.aspx?PageType=4&ListId=00000000-0000-4000-8000-000000000105&ID=4'}};
  let found=0;
  let xml=t.mainXml.replace(/<!--F06_VALUE:([A-Za-z0-9_]+)-->/g,(_,key:string)=>{found++;if(links[key])return '<w:p><w:hyperlink r:id="rIdF06'+key+'"><w:r><w:rPr><w:color w:val="0563C1"/><w:u w:val="single"/></w:rPr><w:t>'+xmlText(links[key].label)+'</w:t></w:r></w:hyperlink></w:p>';if(!(key in values))throw Error('unknown_control');return values[key].replace(/\r\n?/g,'\n').split('\n').map(line=>'<w:p><w:r><w:t xml:space="preserve">'+xmlText(line)+'</w:t></w:r></w:p>').join('');});
  // Match PPG's qualified Word-web behaviour for generated multiline content.
  // Only the new output changes; maintained blank template controls stay intact.
  xml=xml.replace(/<w:text(?:\s[^<>]*)?\/>/g,'<w:richText/>');
  xml=xml.replace(/<w:sdtPr>([\s\S]*?)<\/w:sdtPr>/g,(_,props:string)=>'<w:sdtPr>'+props+(props.includes('<w:richText')?'':'<w:richText/>')+'</w:sdtPr>');
  if(found!==22||xml.includes('<!--F06_')||xml.includes('<w:dataBinding')||xml.includes('<!DOCTYPE'))throw Error('output_controls_invalid');
  const entries:ZipEntry[]=[],names=new Set<string>();let total=0,main=0,relationships=0;
  for(const part of t.parts){safePath(part.path);if(names.has(part.path.toLowerCase()))throw Error('part_collision');names.add(part.path.toLowerCase());let bytes=decodeMember(part.base64);total+=bytes.length;if(total>MAX_RAW_BYTES||sha256(bytes)!==part.sha256)throw Error('template_part_changed');
    if(part.path==='word/document.xml'){bytes=utf8(xml);main++;}
    if(part.path==='word/_rels/document.xml.rels'){let rel=textFromUtf8(bytes);for(const key of Object.keys(links)){if(rel.includes('rIdF06'+key))throw Error('relationship_collision');rel=rel.replace('</Relationships>','<Relationship Id="rIdF06'+key+'" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="'+xmlText(links[key].url)+'" TargetMode="External"/></Relationships>');}bytes=utf8(rel);relationships++;}
    if(/word\/(header|footer)\d+\.xml/.test(part.path))bytes=utf8(textFromUtf8(bytes).replace(/Unissued template/g,'Unissued fictional draft'));
    entries.push({name:part.path,bytes});
  }
  if(main!==1||relationships!==1||!names.has('[content_types].xml'))throw Error('package_shape_invalid');
  const out=storeZip(entries);if(out.length>MAX_RAW_BYTES)throw Error('document_limit');
  return {schemaVersion:1,docxBase64:encodeBase64(out),sha256:sha256(out),bytes:out.length,sourceSHA256:sha256(utf8(job.snapshotJson)),templateSHA256:t.templateSHA256,manifestPin:t.manifestPin,outputRevision:job.outputRevision,includedRecordIDs:ids,wordGenerationPerformed:true,sourceWrites:false,sent:false};
}
// The orchestration must retrieve/recheck these native identities and versions.
// This contract preserves supplied content; it does not certify source authority,
// select records, make business decisions, read workbook cells or call a network.
function selectedAgenda(jobJson:string,membersJson:string):AgendaResult {
  if(utf8(JSON.stringify({jobJson,membersJson})).length>MAX_WIRE_BYTES)throw Error('request_limit');
  const job:SelectedAgendaRequest=JSON.parse(jobJson),t:AgendaTemplate=JSON.parse(membersJson);
  const s:SelectedAgenda=JSON.parse(job.selectionJson);
  const required=(v:string):boolean=>typeof v==='string'&&v.trim().length>0;
  if(job.kind!=='clinical-agenda-selected-word-v2'||s.schemaVersion!==2||
     !required(job.occurrence)||s.meeting_id!==job.occurrence||s.meeting_date!==job.meetingDate||
     !/^\d{4}-\d{2}-\d{2}$/.test(s.meeting_date)||s.timezone!=='Australia/Brisbane'||
     !Number.isInteger(job.outputRevision)||job.outputRevision<1||job.outputRevision>999||
     !required(job.runId)||!required(job.flowId)||!required(job.createdAt)||
     !required(job.templateUniqueId)||!required(job.templateVersion)||
     typeof s.synthetic_only!=='boolean'||!required(s.scope)||!required(s.source_revision)||
     !required(s.source_modified)||s.source.version!==job.sourceVersion||s.source_modified!==job.sourceModified)
    throw Error('selected_identity_invalid');
  const day=new Date(s.meeting_date+'T00:00:00+10:00');
  if(!Number.isFinite(day.getTime())||new Date(day.getTime()+36000000).toISOString().slice(0,10)!==s.meeting_date)
    throw Error('selected_date_invalid');
  const instant=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
  if(!required(s.calendarStart)||!required(s.calendarEnd)||!instant.test(s.calendarStart)||!instant.test(s.calendarEnd)||
     !Number.isFinite(Date.parse(s.calendarStart))||!Number.isFinite(Date.parse(s.calendarEnd))||
     Date.parse(s.calendarEnd)<=Date.parse(s.calendarStart)||
     new Date(Date.parse(s.calendarStart)+36000000).toISOString().slice(0,10)!==s.meeting_date)
    throw Error('selected_calendar_mismatch');
  if(!Array.isArray(s.sections)||s.sections.length!==7||s.sections.some(x=>!required(x))||
     !Array.isArray(s.history)||s.history.some(x=>!required(x))||
     !Array.isArray(s.records)||s.records.length>100||!Array.isArray(s.papers)||s.papers.length>100||
     !Array.isArray(s.minutes)||s.minutes.length>20)throw Error('selected_shape_invalid');
  const nativeLink=(r:AgendaLink):void=>{
    if(!r||!required(r.label)||!required(r.id)||!required(r.version)||typeof r.url!=='string'||
       r.url.length>2048||/[\s\\]/.test(r.url)||
       !/^https:\/\/(fictional-example\.sharepoint\.com|outlook\.office365\.com|outlook\.office\.com|outlook\.cloud\.microsoft)\//i.test(r.url))
      throw Error('selected_native_link_invalid');
  };
  [s.calendar,s.source,...s.papers,...s.minutes].forEach(nativeLink);
  if(!/^https:\/\/(outlook\.office365\.com|outlook\.office\.com|outlook\.cloud\.microsoft)\//i.test(s.calendar.url)||
     !/^https:\/\/fictional-example\.sharepoint\.com\//i.test(s.source.url))throw Error('selected_native_link_role');
  const ids:string[]=[];
  for(const r of s.records){
    if(!r||!required(r.record_id)||!required(r.status)||!required(r.source_text)||
       !Array.isArray(r.history)||r.history.some(x=>!required(x))||ids.includes(r.record_id))
      throw Error('selected_record_invalid');
    for(const v of [r.owner_claim,r.due_date,r.due_label,r.review_date,r.response_ref])
      if(v!==null&&typeof v!=='string')throw Error('selected_record_field_invalid');
    if(r.source_link)nativeLink(r.source_link);
    ids.push(r.record_id);
  }
  if(t.kind!=='F06-word-template-v1'||t.parts.length>100||t.sections.length!==7)throw Error('template_shape_invalid');
  const pin=t.parts.map(p=>p.path+':'+p.sha256).join('\n')+'\n'+sha256(utf8(t.mainXml))+'\n'+sha256(utf8(JSON.stringify(t.sections)))+'\n'+t.templateSHA256;
  if(sha256(utf8(pin))!==EXPECTED_MANIFEST_PIN||t.manifestPin!==EXPECTED_MANIFEST_PIN)throw Error('template_contract_changed');
  const paragraph=(v:string):string=>v.replace(/\r\n?/g,'\n').split('\n').map(line=>'<w:p><w:r><w:t xml:space="preserve">'+xmlText(line)+'</w:t></w:r></w:p>').join('');
  // Expand selected records in the maintained review region. Remove the two
  // fixed specimen slots rather than leaving empty headings or dropping records.
  let xml=t.mainXml;
  const paragraphs=xml.match(/<w:p(?:\s[^>]*)?>[\s\S]*?<\/w:p>/g)||[];
  const controls=xml.match(/<w:sdt>[\s\S]*?<\/w:sdt>/g)||[];
  for(let i=1;i<=3;i++){
    const heading=paragraphs.filter(p=>p.includes('>Review hold '+i+'<'));
    if(heading.length!==1)throw Error('selected_template_region_changed');
    xml=xml.replace(heading[0],i===1?heading[0].replace('>Review hold 1<','>Selected source records<'):'');
    if(i>1){const region=controls.filter(p=>p.includes('<w:tag w:val="ReviewHold'+i+'"'));
      if(region.length!==1)throw Error('selected_template_region_changed');xml=xml.replace(region[0],'');}
  }
  const values:{[key:string]:string}={MeetingID:s.meeting_id,
    MeetingDateTime:s.meeting_date+' — '+s.timezone+'; calendar '+s.calendarStart+' to '+s.calendarEnd,
    DraftRevision:'WORD R'+job.outputRevision+' — unissued '+(s.synthetic_only?'fictional ':'')+'draft',
    OccurrenceScope:s.scope,PaperIdentity:s.papers.length?'Selected papers and native versions are linked above. Content remains for review; generation is not approval.':'No paper selected. A concern does not require a paper.',
    SourceHistory:s.history.length?s.history.join('\n'):'No prior history supplied; no confirmation inferred.',
    SourceProvenance:'Source '+s.source.id+'; revision '+s.source_revision+'; native version '+s.source.version+'; modified '+s.source_modified+'. Included '+JSON.stringify(ids)+'.',
    TemplateProvenance:'F06-selected-agenda-v2; maintained template SHA256 '+t.templateSHA256+'; native '+job.templateUniqueId+' version '+job.templateVersion+'.',
    RunProvenance:'Standard Excel Office Script fresh DOCX; flow '+job.flowId+'; run '+job.runId+'; generated '+job.createdAt+'; output revision '+job.outputRevision+'. No approval or circulation.',OptionalContent:''};
  s.sections.forEach((v,i)=>values['AgendaSection'+(i+1)]=v);
  const links:{[key:string]:AgendaLink}={};let linkIndex=0;
  const linkBlocks=(items:AgendaLink[]):string=>items.map(r=>{
    const key='rIdF06Selected'+(++linkIndex);links[key]=r;
    return '<w:p><w:hyperlink r:id="'+key+'"><w:r><w:rPr><w:color w:val="0563C1"/><w:u w:val="single"/></w:rPr><w:t>'+xmlText(r.label)+'</w:t></w:r></w:hyperlink><w:r><w:t xml:space="preserve"> — '+xmlText(r.id+'; native version '+r.version)+'</w:t></w:r></w:p>';
  }).join('');
  const blocks:{[key:string]:string}={PaperLink:linkBlocks(s.papers),SourceLink:linkBlocks([s.source,s.calendar,...s.minutes]),
    ReviewHold1:s.records.length?s.records.map(r=>paragraph(r.record_id+' — source record; status unchanged')+
      paragraph('Recorded status: '+r.status)+paragraph('Original narrative: '+r.source_text)+paragraph('Original history:')+
      (r.history.length?r.history.map(h=>paragraph(h)).join(''):paragraph('No source history supplied.'))+
      paragraph('Original owner claim: '+(r.owner_claim||'not established')+'; original due: '+(r.due_date||'not established')+'; original due label: '+(r.due_label||'not supplied')+'; original review: '+(r.review_date||'not established'))+
      paragraph('Response reference: '+(r.response_ref||'none recorded')+'. No new issue, assignment or closure.')+
      (r.source_link?linkBlocks([r.source_link]):'')).join(''):paragraph('No source records selected; no actions inferred.')};
  let found=0;xml=xml.replace(/<!--F06_VALUE:([A-Za-z0-9_]+)-->/g,(_,key:string)=>{found++;if(key in blocks)return blocks[key];if(!(key in values))throw Error('unknown_control');return paragraph(values[key]);});
  xml=xml.replace(/<w:text(?:\s[^<>]*)?\/>/g,'<w:richText/>').replace(/<w:sdtPr>([\s\S]*?)<\/w:sdtPr>/g,(_,props:string)=>'<w:sdtPr>'+props+(props.includes('<w:richText')?'':'<w:richText/>')+'</w:sdtPr>');
  if(found!==20||xml.includes('<!--F06_')||xml.includes('<w:dataBinding')||xml.includes('<!DOCTYPE'))throw Error('output_controls_invalid');
  const entries:ZipEntry[]=[],names=new Set<string>();let total=0,main=0,relationships=0;
  for(const part of t.parts){safePath(part.path);if(names.has(part.path.toLowerCase()))throw Error('part_collision');names.add(part.path.toLowerCase());let bytes=decodeMember(part.base64);total+=bytes.length;if(total>MAX_RAW_BYTES||sha256(bytes)!==part.sha256)throw Error('template_part_changed');
    if(part.path==='word/document.xml'){bytes=utf8(xml);main++;}
    if(part.path==='word/_rels/document.xml.rels'){let rel=textFromUtf8(bytes);for(const key of Object.keys(links)){if(rel.includes(key))throw Error('relationship_collision');rel=rel.replace('</Relationships>','<Relationship Id="'+key+'" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="'+xmlText(links[key].url)+'" TargetMode="External"/></Relationships>');}bytes=utf8(rel);relationships++;}
    if(/word\/(header|footer)\d+\.xml/.test(part.path))bytes=utf8(textFromUtf8(bytes).replace(/Unissued template/g,'Unissued '+(s.synthetic_only?'fictional ':'')+'draft'));
    entries.push({name:part.path,bytes});
  }
  if(main!==1||relationships!==1||!names.has('[content_types].xml'))throw Error('package_shape_invalid');
  const out=storeZip(entries);if(out.length>MAX_RAW_BYTES)throw Error('document_limit');
  return {schemaVersion:2,docxBase64:encodeBase64(out),sha256:sha256(out),bytes:out.length,sourceSHA256:sha256(utf8(job.selectionJson)),templateSHA256:t.templateSHA256,manifestPin:t.manifestPin,outputRevision:job.outputRevision,includedRecordIDs:ids,wordGenerationPerformed:true,sourceWrites:false,sent:false};
}
function xmlText(value:string):string {if(typeof value!=='string'||value.length>16000||/[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]/.test(value))throw Error('text_invalid');return value.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function textFromUtf8(bytes:number[]):string {let escaped='';for(const b of bytes)escaped+='%'+b.toString(16).padStart(2,'0');const value=decodeURIComponent(escaped);if(sha256(utf8(value))!==sha256(bytes))throw Error('utf8_invalid');return value;}

function safePath(value: string): void {
  if (typeof value !== "string" || value.length > 240 || /[\\:\x00-\x1f\x7f]/.test(value) ||
      value.split("/").some(x => !x || x === "." || x === ".." || /[. ]$/.test(x))) throw Error("unsafe_member_path");
}
function decodeMember(value: string): number[] {
  if (typeof value !== "string" || value.length % 4 || !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(value)) throw Error("invalid_base64");
  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/", bytes: number[] = [];
  for (let i = 0; i < value.length; i += 4) {
    const a = alphabet.indexOf(value[i]), b = alphabet.indexOf(value[i+1]);
    const c = value[i+2] === "=" ? 0 : alphabet.indexOf(value[i+2]), d = value[i+3] === "=" ? 0 : alphabet.indexOf(value[i+3]);
    if ((value[i+2] === "=" && (b & 15)) || (value[i+3] === "=" && (c & 3))) throw Error("noncanonical_base64");
    bytes.push((a << 2) | (b >>> 4));
    if (value[i+2] !== "=") bytes.push(((b & 15) << 4) | (c >>> 2));
    if (value[i+3] !== "=") bytes.push(((c & 3) << 6) | d);
  }
  return bytes;
}
function encodeBase64(bytes: number[]): string {
  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  const chunks: string[] = [];
  for (let i = 0; i < bytes.length; i += 3) {
    const a = bytes[i], b = bytes[i+1] || 0, c = bytes[i+2] || 0;
    chunks.push(alphabet[a >>> 2] + alphabet[((a & 3) << 4) | (b >>> 4)] +
      (i+1 < bytes.length ? alphabet[((b & 15) << 2) | (c >>> 6)] : "=") +
      (i+2 < bytes.length ? alphabet[c & 63] : "="));
  }
  return chunks.join("");
}
function storeZip(entries: ZipEntry[]): number[] {
  // ZIP32 STORE, UTF-8 names, fixed DOS timestamp 1980-01-01; deterministic bytes.
  const crcTable = Array.from({ length: 256 }, (_, index) => {
    let c = index; for (let k = 0; k < 8; k++) c = (c & 1) ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    return c >>> 0;
  });
  const chunks: number[][] = [], directory: number[][] = [];
  let offset = 0;
  const put = (bytes: number[], at: number, value: number, size: number) => {
    for (let i = 0; i < size; i++) bytes[at+i] = (value >>> (i*8)) & 255;
  };
  for (const entry of entries) {
    const name = utf8(entry.name), bytes = entry.bytes;
    let crc = 0xffffffff; for (const b of bytes) crc = crcTable[(crc ^ b) & 255] ^ (crc >>> 8);
    crc = (crc ^ 0xffffffff) >>> 0;
    const local = new Array<number>(30 + name.length).fill(0);
    put(local,0,0x04034b50,4); put(local,4,20,2); put(local,6,0x800,2); put(local,12,0x21,2);
    put(local,14,crc,4); put(local,18,bytes.length,4); put(local,22,bytes.length,4); put(local,26,name.length,2);
    name.forEach((b,i) => { local[30+i] = b; });
    const central = new Array<number>(46 + name.length).fill(0);
    put(central,0,0x02014b50,4); put(central,4,20,2); put(central,6,20,2); put(central,8,0x800,2); put(central,14,0x21,2);
    put(central,16,crc,4); put(central,20,bytes.length,4); put(central,24,bytes.length,4); put(central,28,name.length,2); put(central,42,offset,4);
    name.forEach((b,i) => { central[46+i] = b; });
    chunks.push(local,bytes); directory.push(central); offset += local.length + bytes.length;
  }
  const size = directory.reduce((n,b) => n + b.length,0), end = new Array<number>(22).fill(0);
  put(end,0,0x06054b50,4); put(end,8,entries.length,2); put(end,10,entries.length,2); put(end,12,size,4); put(end,16,offset,4);
  const result: number[] = [];
  for (const chunk of [...chunks,...directory,end]) for (const b of chunk) result.push(b);
  return result;
}

function utf8(text: string): number[] {
  const bytes: number[] = [];
  for (let i = 0; i < text.length; i++) {
    let cp = text.charCodeAt(i);
    if (cp >= 0xd800 && cp <= 0xdbff) {
      const lo = text.charCodeAt(++i);
      if (!(lo >= 0xdc00 && lo <= 0xdfff)) throw new Error("invalid_unicode");
      cp = 0x10000 + ((cp - 0xd800) << 10) + lo - 0xdc00;
    } else if (cp >= 0xdc00 && cp <= 0xdfff) throw new Error("invalid_unicode");
    if (cp < 0x80) bytes.push(cp);
    else if (cp < 0x800) bytes.push(0xc0 | (cp >>> 6), 0x80 | (cp & 63));
    else if (cp < 0x10000) bytes.push(0xe0 | (cp >>> 12), 0x80 | ((cp >>> 6) & 63), 0x80 | (cp & 63));
    else bytes.push(0xf0 | (cp >>> 18), 0x80 | ((cp >>> 12) & 63), 0x80 | ((cp >>> 6) & 63), 0x80 | (cp & 63));
  }
  return bytes;
}
function sha256(input: number[]): string {
  const k = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  const h = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  const data = input.slice(); const bits = input.length * 8;
  data.push(0x80); while (data.length % 64 !== 56) data.push(0);
  const high = Math.floor(bits / 0x100000000), low = bits >>> 0;
  for (const word of [high, low]) for (let j = 3; j >= 0; j--) data.push((word >>> (j * 8)) & 255);
  const rr = (v: number, n: number) => (v >>> n) | (v << (32 - n));
  for (let offset = 0; offset < data.length; offset += 64) {
    const w: number[] = [];
    for (let i = 0; i < 16; i++) w[i] = ((data[offset + 4*i] << 24) | (data[offset + 4*i+1] << 16) | (data[offset + 4*i+2] << 8) | data[offset + 4*i+3]) >>> 0;
    for (let i = 16; i < 64; i++) {
      const s0 = rr(w[i-15],7) ^ rr(w[i-15],18) ^ (w[i-15] >>> 3);
      const s1 = rr(w[i-2],17) ^ rr(w[i-2],19) ^ (w[i-2] >>> 10);
      w[i] = (w[i-16] + s0 + w[i-7] + s1) >>> 0;
    }
    let [a,b,c,d,e,f,g,j] = h;
    for (let i = 0; i < 64; i++) {
      const t1 = (j + (rr(e,6)^rr(e,11)^rr(e,25)) + ((e&f)^((~e)&g)) + k[i] + w[i]) >>> 0;
      const t2 = ((rr(a,2)^rr(a,13)^rr(a,22)) + ((a&b)^(a&c)^(b&c))) >>> 0;
      j=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;
    }
    [a,b,c,d,e,f,g,j].forEach((v,i) => { h[i]=(h[i]+v)>>>0; });
  }
  return h.map(v => v.toString(16).padStart(8,"0")).join("");
}

// The maintained DOCX is compiled once into pinned parts. Both the retained
// specimen and selected-source population run in Standard Office Script.
