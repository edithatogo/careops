/* Apache-2.0. Exact metadata origins, never retrieval or publication authority. */
const defaults=['www.safetyandquality.gov.au','meteor.aihw.gov.au'];
export function officialSourceURL(value,officialHosts=defaults) {
 if(!Array.isArray(officialHosts))throw Error('EXACT_PUBLISHER_HOST_COLLECTION_REQUIRED');
 if(typeof value!=='string'||/[\\\u0000-\u0020\u007f]/.test(value)||value!==value.trim())throw Error('OFFICIAL_SOURCE_URL_REQUIRED');
 const url=new URL(value);
 if(url.protocol!=='https:'||!officialHosts.includes(url.hostname)||url.username||url.password||(url.port!==''&&url.port!=='443')||url.hash)throw Error('OFFICIAL_SOURCE_URL_REQUIRED');
 return value;
}
