from collections.abc import Iterator
from wfrcwflib.workflow import (
    Connector, Step, PositionalArgument, OptionalArgument,
    InputConnector, OutputConnector,
    UnresolvedWorkflow, WfrObject,
)

class ParseError(Exception):
    pass

def next_token(line: str) -> tuple[str, ...]:
    toks = line.split(maxsplit=1)
    match len(toks):
        case 0:
            return ("", "")
        case 1:
            return (toks[0], "")
        case _:
            return tuple(toks)

connectors = {
    "input": InputConnector,
    "output": OutputConnector,
}

start_connector_string = "{"
end_connector_string = "}"

def parse_connector(line: str) -> tuple[Connector, str]:
    connector_open, rest = next_token(line)
    if not connector_open == start_connector_string:
        raise ParseError(f"connector must start with '{start_connector_string} ': {connector_open}")

    cmd, rest = next_token(rest)
    if not cmd in connectors:
        raise ParseError(f"invalid connector type: {cmd}")
    cls = connectors[cmd]

    name, rest = next_token(rest)
    if not name:
        raise ParseError("connector name cannot be empty")

    ext, rest = next_token(rest)
    if not ext:
        raise ParseError("connector ext cannot be empty")

    connector_close, rest = next_token(rest)
    if not connector_close == end_connector_string:
        raise ParseError(f"connector must end with ' {end_connector_string}': {connector_close}")

    return cls(name, ext), rest

def parse_argument_value(line: str) -> tuple[str | Connector, ...]:
    if line.startswith("{"):
        return parse_connector(line)
    else:
        return next_token(line)

def parse_positional_argument(line: str) -> PositionalArgument:
    value, rest = parse_argument_value(line)
    if rest:
        raise ParseError(f"only one positional argument per line: {rest}")
    return PositionalArgument(value)

def parse_optional_argument(line: str) -> OptionalArgument:
    flag, rest = next_token(line)
    if not flag.startswith("-"):
        raise ParseError(f"optional argument flags must start with '-': {flag}")
    obj = OptionalArgument(flag)
    while rest:
        value, rest = parse_argument_value(rest)
        obj.values.append(value)
    return obj

def parse_step(lines: Iterator[str]) -> Step:
    lines = iter(lines)

    name, name_rest = next_token(next(lines))
    if name_rest:
        raise ParseError(f"name must appear by itself: {name_rest}")
    
    prog, prog_rest = next_token(next(lines))
    if prog_rest:
        raise ParseError(f"prog must appear by itself: {prog_rest}")

    obj = Step(name, prog)
    for line in lines:
        if line.startswith("-"):
            arg = parse_optional_argument(line)
        else:
            arg = parse_positional_argument(line)
        obj.args.append(arg)
    return obj

def parse_workflow(lines: Iterator[str]) -> UnresolvedWorkflow:
    lines = iter(lines)

    name, name_rest = next_token(next(lines))
    if name_rest:
        raise ParseError(f"name must appear by itself: {name_rest}")

    obj = UnresolvedWorkflow(name)
    for line in lines:
        from_step, rest = next_token(line)
        from_output, rest = next_token(rest)
        arrow, rest = next_token(rest)
        to_step, rest = next_token(rest)
        to_input, rest = next_token(rest)
        if rest:
            raise ParseError(f"too many tokens in connection: {rest}")
        obj.connections.append((from_step, from_output, to_step, to_input))
    return obj

subparsers = {
    "step": parse_step,
    "workflow": parse_workflow,
}

def parse_paragraph(lines: Iterator[str]) -> WfrObject:
    lines = list(lines)
    cmd, rest = next_token(lines[0])
    if not cmd in subparsers:
        raise ParseError(f"invalid keyword: {cmd}")
    subparser = subparsers[cmd]
    # Remove the keyword from the first line to avoid dealing with it later
    lines[0] = rest
    obj = subparser(lines)
    return obj

def split_paragraphs(lines: Iterator[str]) -> Iterator[list[str]]:
    paragraph = []
    for line in lines:
        if line.strip():
            paragraph.append(line)
        elif paragraph:
            yield paragraph
            paragraph = []
    if paragraph:
        yield paragraph

def parse(lines: Iterator[str]) -> Iterator[WfrObject]:
    paragraphs = split_paragraphs(lines)
    for p in paragraphs:
        obj = parse_paragraph(preprocess(p))
        yield obj

def strip_comment(line: str) -> str:
    code, _, comment = line.partition("#")
    return code

def strip_whitespace(line: str) -> str:
    return line.strip()

def preprocess(lines: Iterator[str]) -> Iterator[str]:
    # Do we want to verify proper indentation before removing it all?
    for line in lines:
        line = strip_comment(line)
        line = strip_whitespace(line)
        yield line
