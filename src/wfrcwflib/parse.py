from wfrcwflib.workflow import (
    Step, PositionalArgument, OptionalArgument,
    InputConnector, OutputConnector,
    UnresolvedWorkflow,
)

class ParseError(Exception):
    pass

def next_token(line):
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

def parse_connector(line):
    connector_open, rest = next_token(line)
    if not connector_open == "{":
        raise ParseError("connector must start with '{ '")

    cmd, rest = next_token(rest)
    if not cmd in connectors:
        raise ParseError("invalid connector type")
    cls = connectors[cmd]

    name, rest = next_token(rest)
    if not name:
        raise ParseError("connector name cannot be empty")

    ext, rest = next_token(rest)
    if not ext:
        raise ParseError("connector ext cannot be empty")

    connector_close, rest = next_token(rest)
    if not connector_close == "}":
        raise ParseError("connector must end with ' }'")

    return cls(name, ext), rest

def parse_argument_value(line):
    if line.startswith("{"):
        return parse_connector(line)
    else:
        return next_token(line)

def parse_positional_argument(line):
    value, rest = parse_argument_value(line)
    if rest:
        raise ParseError("only one positional argument per line")
    return PositionalArgument(value)

def parse_optional_argument(line):
    flag, rest = next_token(line)
    if not flag.startswith("-"):
        raise ParseError("optional argument flags must start with '-'")
    obj = OptionalArgument(flag)
    while rest:
        value, rest = parse_argument_value(rest)
        obj.values.append(value)
    return obj

def parse_step(lines):
    lines = iter(lines)

    name, name_rest = next_token(next(lines))
    if name_rest:
        raise ParseError("name must appear by itself")

    prog, prog_rest = next_token(next(lines))
    if prog_rest:
        raise ParseError("prog must appear by itself")

    obj = Step(name, prog)
    for line in lines:
        if line.startswith("-"):
            arg = parse_optional_argument(line)
        else:
            arg = parse_positional_argument(line)
        obj.args.append(arg)
    return obj

def parse_workflow(lines):
    lines = iter(lines)

    name, name_rest = next_token(next(lines))
    if name_rest:
        raise ParseError("name must appear by itself")

    obj = UnresolvedWorkflow(name)
    for line in lines:
        from_step, rest = next_token(line)
        from_output, rest = next_token(rest)
        arrow, rest = next_token(rest)
        to_step, rest = next_token(rest)
        to_input, rest = next_token(rest)
        if rest:
            raise ParseError("too many tokens in connection")
        obj.connections.append((from_step, from_output, to_step, to_input))
    return obj

subparsers = {
    "step": parse_step,
    "workflow": parse_workflow,
}

def parse_paragraph(lines):
    lines = list(lines)
    cmd, rest = next_token(lines[0])
    if not cmd in subparsers:
        raise ParseError("invalid keyword")
    subparser = subparsers[cmd]
    # Remove the keyword from the first line to avoid dealing with it later
    lines[0] = rest
    obj = subparser(lines)
    return obj

def split_paragraphs(lines):
    paragraph = []
    for line in lines:
        if line:
            paragraph.append(line)
        elif paragraph:
            yield paragraph
            paragraph = []
    if paragraph:
        yield paragraph

def parse(lines):
    paragraphs = split_paragraphs(lines)
    for p in paragraphs:
        obj = parse_paragraph(p)
        yield obj

def strip_comment(line):
    code, _, comment = line.partition("#")
    return code

def strip_whitespace(line):
    return line.strip()

def preprocess(lines):
    for line in lines:
        line = strip_comment(line)
        line = strip_whitespace(line)
        yield line
