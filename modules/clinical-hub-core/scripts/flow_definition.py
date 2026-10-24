"""Pure flow-definition comparison; no client, authentication or tenant calls."""
import copy

AUTH = {'type': 'Raw', 'value': "@json(decodeBase64(triggerOutputs().headers['X-MS-APIM-Tokens']))['$ConnectionKey']"}

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def definition(value):
    """Ignore only known service auth expressions and root graph metadata."""
    value = copy.deepcopy(value)
    value.pop('metadata', None)

    def visit(node):
        if isinstance(node, dict):
            if node.get('type') == 'OpenApiConnection':
                auth = node.get('inputs', {}).pop('authentication', None)
                require(auth in (None, "@parameters('$authentication')", AUTH),
                        'Unknown authentication shape; inspect before continuing')
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)
    visit(value)
    return value
