from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import graphlib
import subprocess


@dataclass
class Connector:
    ext: str

class InputConnector(Connector):
    pass

class OutputConnector(Connector):
    pass

class OutputPrefixConnector(OutputConnector):
    pass

class InputPrefixConnector(InputConnector):
    pass

class StdoutConnector(OutputConnector):
    pass

class OutputStdoutConnector(OutputConnector):
    pass

@dataclass
class PositionalArgument:
    value: str | Connector

    @property
    def inputs(self):
        if isinstance(self.value, InputConnector):
            yield self.value

    @property
    def outputs(self):
        if isinstance(self.value, OutputConnector):
            yield self.value

    def itervals(self):
        yield self.value


@dataclass
class OptionalArgument:
    flag: str
    values: list[str | Connector] = field(default_factory=list)

    @property
    def inputs(self):
        for value in self.values:
            if isinstance(value, InputConnector):
                yield value

    @property
    def outputs(self):
        for value in self.values:
            if isinstance(value, OutputConnector):
                yield value

    def itervals(self):
        yield self.flag
        for value in self.values:
            yield value


@dataclass
class Step:
    name: str
    prog: str
    args: list[PositionalArgument | OptionalArgument] = field(default_factory=list)
    stdout: StdoutConnector | None = None

    @property
    def inputs(self):
        for arg in self.args:
            for input in arg.inputs:
                yield input

    @property
    def outputs(self):
        for arg in self.args:
            for output in arg.outputs:
                yield output
        if self.stdout is not None:
            yield self.stdout

    def iterargs(self):
        yield self.prog
        for arg in self.args:
            for value in arg.itervals():
                yield value


@dataclass
class UnresolvedWorkflow:
    name: str
    connections: list[tuple[str, str, str, str]] = field(default_factory=list)

    def resolve(self, registry):
        w = Workflow(self.name, registry)
        for args in self.connections:
            w.connect(*args)
        return w


class Workflow:
    def __init__(self, name, registry):
        self.name = name
        self.registry = registry
        self._active_steps = set()
        # Reverse directed graph
        # (step2, input) => (step1, output)
        self.connections_in = {}

    def connect(self, from_step, from_output, to_step, to_input):
        self._add_step(from_step)
        self._add_step(to_step)
        self.connections_in[(to_step, to_input)] = (from_step, from_output)

    def _add_step(self, step_name):
        if step_name not in self._active_steps:
            step = self.registry[step_name]
            for input in step.inputs:
                self.connections_in[(step.name, input.ext)] = None
            self._active_steps.add(step.name)

    @property
    def connections_out(self):
        res = {}
        for step_name in self._active_steps:
            step = self.registry[step_name]
            for output in step.outputs:
                res[(step.name, output.ext)] = []
        for k, v in self.connections_in.items():
            if v is not None:
                res[v].append(k)
        return res

    @property
    def inputs(self):
        for k, v in self.connections_in.items():
            if v is None:
                yield k

    @property
    def outputs(self):
        for k, vs in self.connections_out.items():
            if not vs:
                yield k

    @property
    def dag(self):
        graph = {step: set() for step in self._active_steps}
        for dest, src in self.connections_in.items():
            print("Making DAG:", dest, src)
            if src is not None:
                src_step, _ = src
                dest_step, _ = dest
                graph[dest_step].add(src_step)
        return graph

    @property
    def order(self):
        ts = graphlib.TopologicalSorter(self.dag)
        return list(ts.static_order())

    @property
    def edges(self):
        for k, v in self.connections_in.items():
            if v is not None:
                dest_step, _ = k
                src_step, _ = v
                yield src_step, dest_step


@dataclass
class FileCollector:
    dir: Path


@dataclass
class WorkflowFile:
    dir: Path
    basename: str
    ext: str

    @property
    def filename(self):
        return self.basename + self.ext

    @property
    def path(self):
        return self.dir / self.filename

    @property
    def open(self, mode):
        return open(self.filepath, mode)


def unique_inorder(xs):
    return list(dict.fromkeys(xs))

@dataclass
class RunnableCommand:
    step: Step
    output_dir: Path
    input_files: dict[str, WorkflowFile] = field(default_factory=dict)
    conda_env: str | None = None

    def command_args(self):
        if self.conda_env is not None:
            yield "conda"
            yield "run"
            yield "-n"
            yield self.conda_env
        output_files = dict(self.output_files)
        for x in self.step.iterargs():
            if isinstance(x, InputConnector):
                infile = self.input_files[x.ext]
                val = str(infile.path)
            elif isinstance(x, OutputConnector):
                outfile = output_files[x.ext]
                val = str(outfile.path)
            else:
                val = x
            yield val

    def run(self):
        args = list(self.command_args())
        subprocess.run(args, stdout=self.stdout_fileobj)

    @property
    def output_basename(self):
        input_files = [self.input_files[x.ext] for x in self.step.inputs]
        basenames = [x.basename for x in input_files]
        unique_basenames = unique_inorder(basenames)
        return "__".join(unique_basenames)

    @property
    def output_files(self):
        for output in self.step.outputs:
            yield output.ext, WorkflowFile(self.output_dir, self.output_basename, output.ext)

    @property
    def stdout_fileobj(self):
        if self.step.stdout is not None:
            wf = WorkflowFile(self.output_dir, self.output_basename, self.step.stdout.ext)
            return open(wf, "w")
        return None


@dataclass
class FileSpace:
    workflow: Workflow
    intermediate_dir: Path
    output_dir: Path
    # Reverse directed graph
    # (step, input) => source
    sources: dict[tuple[str, str], WorkflowFile] = field(default_factory=dict)


class CommandSpace:
    pass
