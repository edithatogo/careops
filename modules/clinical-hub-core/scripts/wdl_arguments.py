"""Argument splitting for the bounded offline expression-test interpreter."""
def _split_args(source: str) -> list[str]:
    args: list[str] = []
    depth = 0
    quoted = False
    escaped = False
    start = 0
    for i, char in enumerate(source):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "'":
                quoted = False
        elif char == "'":
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            args.append(source[start:i].strip())
            start = i + 1
    args.append(source[start:].strip())
    return args
