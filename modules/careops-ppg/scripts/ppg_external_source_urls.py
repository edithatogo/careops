"""Apache-2.0. Exact official metadata origins; no retrieval or identity decision."""
from urllib.parse import urlsplit

OFFICIAL_HOSTS = frozenset({'www.safetyandquality.gov.au', 'meteor.aihw.gov.au'})


def official_source_url(value, allowed_hosts=OFFICIAL_HOSTS):
    if not isinstance(allowed_hosts, (list, tuple, set, frozenset)):
        raise TypeError('Explicit exact publisher host collection required')
    if (not isinstance(value, str) or '\\' in value
            or any(ord(c) <= 32 or ord(c) == 127 for c in value)):
        raise ValueError('Official HTTPS source URL required')
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or parsed.hostname not in allowed_hosts
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.fragment or value != value.strip()):
        raise ValueError('Official HTTPS source URL required')
    return value
