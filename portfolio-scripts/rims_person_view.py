"""Tenant-free bounded person view for approved directory snapshots.

Never calls Microsoft Graph, sends data or infers HR employment. Explicit
reviewed mappings only; unfounded directory/author collisions remain unresolved.
Run only in an approved private environment for real records.
"""
class PersonViewError(ValueError):
    pass

def _id(v,label):
    if not isinstance(v,str) or not v.strip():
        raise PersonViewError("missing "+label)
    return v.strip()

def build_person_view(directory_accounts, author_mentions, crosswalk, *, verify_link=None):
    """Create minimal identity relationships without automatic employee claims."""
    if not all(isinstance(v,list) for v in (directory_accounts,author_mentions,crosswalk)):
        raise PersonViewError("input arrays required")
    by_account={}; by_mention={}
    for row in directory_accounts:
        key=_id(row.get("directory_account_id"),"directory account ID")
        if key in by_account:
            raise PersonViewError("duplicate directory account")
        by_account[key]=row
    for row in author_mentions:
        key=_id(row.get("author_mention_id"),"author mention ID")
        if key in by_mention:
            raise PersonViewError("duplicate author mention")
        by_mention[key]=row
    if verify_link is not None and not callable(verify_link):
        raise PersonViewError("invalid verifier")
    seen=set(); linked=[]; unresolved=[]
    for row in crosswalk:
        person=_id(row.get("person_id"),"person ID")
        account=row.get("directory_account_id")
        mention=row.get("author_mention_id")
        if account is None and mention is None:
            raise PersonViewError("unanchored link")
        key=(person,account,mention)
        if key in seen:
            raise PersonViewError("duplicate crosswalk")
        seen.add(key)
        if account is not None and account not in by_account:
            raise PersonViewError("missing directory account")
        if mention is not None and mention not in by_mention:
            raise PersonViewError("missing author mention")
        if row.get("link_evidence_hash") is None:
            raise PersonViewError("link evidence required")
        if verify_link is None or verify_link(row) is not True:
            unresolved.append({"person_id":person,"status":"NeedsHumanReview"})
            continue
        linked.append({"person_id":person,
                       "directory_account_id":account,
                       "author_mention_id":mention,
                       "orcid":by_mention[mention].get("orcid") if mention else None,
                       "affiliation_source_id":by_mention[mention].get("affiliation_source_id") if mention else None,
                       "employment_status":"Unverified",
                       "identity_link_verified":True})
    return {"schema":"careops-rims.person-view/1","links":linked,"unresolved":unresolved,
            "employment_authorised":False,"private_local_only":True}
