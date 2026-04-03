import pytest
from wfrcwflib.workflow import (
    InputConnector, OutputConnector,
    PositionalArgument, OptionalArgument,
    Step, Workflow,
)

# Positional arguments

def test_positional_argument_input():
    c = InputConnector(".txt")
    a = PositionalArgument(value=c)
    assert list(a.inputs) == [c]
    assert list(a.outputs) == []
    assert list(a.itervals()) == [c]

def test_positional_argument_output():
    c = OutputConnector(".log")
    a = PositionalArgument(value=c)
    assert list(a.inputs) == []
    assert list(a.outputs) == [c]
    assert list(a.itervals()) == [c]

def test_positional_argument_static():
    a = PositionalArgument(value="abc")
    assert list(a.inputs) == []
    assert list(a.outputs) == []
    assert list(a.itervals()) == ["abc"]

# Optional arguments
    
def test_optional_argument_input():
    c = InputConnector(".txt")
    a = OptionalArgument(flag="-f", values=[c])
    assert list(a.inputs) == [c]
    assert list(a.outputs) == []
    assert list(a.itervals()) == ["-f", c]

def test_optional_argument_output():
    c = OutputConnector(".tsv")
    a = OptionalArgument(flag="-o", values=[c])
    assert list(a.inputs) == []
    assert list(a.outputs) == [c]
    assert list(a.itervals()) == ["-o", c]

def test_optional_argument_static():
    a = OptionalArgument(flag="-k", values=["3"])
    assert list(a.inputs) == []
    assert list(a.outputs) == []
    assert list(a.itervals()) == ["-k", "3"]

# Step

def test_step_cp():
    input_fasta = InputConnector(".fasta")
    output_fasta = OutputConnector(".fasta")
    args = [
        PositionalArgument(input_fasta),
        PositionalArgument(output_fasta),
    ]
    s = Step(name="copy-fasta", prog="cp", args=args, stdout=None)
    assert list(s.inputs) == [input_fasta]
    assert list(s.outputs) == [output_fasta]
    assert list(s.iterargs()) == ["cp", input_fasta, output_fasta]

def test_step_blast():
    blast_input = InputConnector(".fasta")
    blast_output = OutputConnector(".txt")
    s = Step(
        name="blast-nt",
        prog="blastn",
        args=[
            OptionalArgument(flag="-query", values=[blast_input]),
            OptionalArgument(flag="-db", values=["nt"]),
            OptionalArgument(flag="-out", values=[blast_output]),
        ],
        stdout=None,
    )
    assert list(s.inputs) == [blast_input]
    assert list(s.outputs) == [blast_output]
    assert list(s.iterargs()) == [
        "blastn", "-query", blast_input, "-db", "nt", "-out", blast_output,
    ]
    
# Workflow

def test_workflow_blast_copy():
    blast_input = InputConnector(".fasta")
    blast_output = OutputConnector(".txt")
    blast_step = Step(
        name="blast-nt",
        prog="blastn",
        args=[
            OptionalArgument(flag="-query", values=[blast_input]),
            OptionalArgument(flag="-db", values=["nt"]),
            OptionalArgument(flag="-out", values=[blast_output]),
        ],
        stdout=None,
    )

    cp_input = InputConnector(".txt")
    cp_output = OutputConnector(".tsv")
    cp_step = Step(
        name="copy-blastout",
        prog="cp",
        args = [
            PositionalArgument(cp_input),
            PositionalArgument(cp_output),
        ],
        stdout=None,
    )

    registry = {
        "blast-nt": blast_step,
        "copy-blastout": cp_step,
    }
    w = Workflow(name="blast-and-copy", registry=registry)
    assert w.connections_in == {}
    assert w.connections_out == {}
    assert list(w.inputs) == []
    assert list(w.outputs) == []
    assert w.order == []

    w.connect("blast-nt", ".txt", "copy-blastout", ".txt")
    assert w.connections_in == {
        ('blast-nt', '.fasta'): None,
        ("copy-blastout", ".txt"): ("blast-nt", ".txt"),
    }
    assert w.connections_out == {
        ("blast-nt", ".txt"): [("copy-blastout", ".txt")],
        ("copy-blastout", ".tsv"): [],
    }
    assert list(w.inputs) == [("blast-nt", ".fasta")]
    assert list(w.outputs) == [("copy-blastout", ".tsv")]
    assert w.order == ["blast-nt", "copy-blastout"]
