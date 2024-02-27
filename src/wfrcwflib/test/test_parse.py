import pytest

from wfrcwflib.parse import (
    ParseError,
    split_paragraphs, next_token,
    parse_connector, parse_argument_value,
    parse_positional_argument, parse_optional_argument,
    parse_step, parse_paragraph, parse,
    strip_comment, preprocess,
)
from wfrcwflib.workflow import (
    InputConnector, OutputConnector,
    PositionalArgument, OptionalArgument,
    Step,
)

def test_next_token():
    # We assume that leading and trailing whitespace is removed
    assert next_token("a bc d") == ("a", "bc d")
    assert next_token("abc") == ("abc", "")
    assert next_token("ab   cd") == ("ab", "cd")
    assert next_token("") == ("", "")

def test_parse_connector():
    assert parse_connector("{ input a b }") == \
        (InputConnector("a", "b"), "")
    assert parse_connector("{ output 1 . } g-- -f") == \
        (OutputConnector("1", "."), "g-- -f")
    with pytest.raises(ParseError):
        parse_connector("{input a b}")

def test_parse_argument_value():
    assert parse_argument_value("great.txt { input a b }") == \
        ("great.txt", "{ input a b }")
    assert parse_argument_value("{ input a b } great.txt") == \
        (InputConnector("a", "b"), "great.txt")

def test_parse_positional_argument():
    assert parse_positional_argument("myfile.txt") == \
        PositionalArgument("myfile.txt")
    assert parse_positional_argument("{ input a b }") == \
        PositionalArgument(InputConnector("a", "b"))
    with pytest.raises(ParseError):
        parse_positional_argument("myfile.txt b")

def test_parse_optional_argument():
    assert parse_optional_argument("-b") == OptionalArgument("-b")
    assert parse_optional_argument("--hello there c") == \
        OptionalArgument("--hello", ["there", "c"])

blast_step = Step("blastn-mydb", "blastn", [
    OptionalArgument("-query", [InputConnector("seqs", "fasta")]),
    OptionalArgument("-db", ["myblastdb"]),
    OptionalArgument("-out", [OutputConnector("result", "tsv")]),
])

def test_parse_step():
    p = [
        "blastn-mydb",
        "blastn",
        "-query { input seqs fasta }",
        "-db myblastdb",
        "-out { output result tsv }",
    ]
    assert parse_step(p) == blast_step

def test_parse_paragraph():
    p = [
        "step blastn-mydb",
        "blastn",
        "-query { input seqs fasta }",
        "-db myblastdb",
        "-out { output result tsv }",
    ]
    assert parse_paragraph(p) == blast_step

def test_split_paragraphs():
    assert list(split_paragraphs(["a", "b", "", "c", "d"])) == \
        [["a", "b"], ["c", "d"]]
    assert list(split_paragraphs(["a", "", "c", "", ""])) == \
        [["a"], ["c"]]
    assert list(split_paragraphs(["a", "", "", "", "c", "d"])) == \
        [["a"], ["c", "d"]]

def test_parse():
    input = [
        "step a",
        "b",
        "--c d ef",
        "g",
        "",
        "step h",
        "ijk.py",
        "{ input m n }",
        ]
    assert list(parse(input)) == [
        Step("a", "b", [
            OptionalArgument("--c", ["d", "ef"]),
            PositionalArgument("g"),
        ]),
        Step("h", "ijk.py", [
            PositionalArgument(InputConnector("m", "n")),
        ]),
    ]

def test_strip_comment():
    assert strip_comment("  code and  # comment") == "  code and  "

code_with_extras = """\
step a # very important
  blastn
  -query seqs.fasta
  -db mydb.fasta
  -out blastres.tsv

# next step
step b
  myscript.R
  blastres.tsv
""".splitlines()

def test_preprocess():
    assert list(preprocess(code_with_extras)) == [
        "step a",
        "blastn",
        "-query seqs.fasta",
        "-db mydb.fasta",
        "-out blastres.tsv",
        "",
        "",
        "step b",
        "myscript.R",
        "blastres.tsv",
    ]
