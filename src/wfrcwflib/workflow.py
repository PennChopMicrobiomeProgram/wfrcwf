from dataclasses import dataclass, field
from typing import Optional
import graphlib


@dataclass
class Connector:
    name: str
    ext: str

class InputConnector(Connector):
    pass

class OutputConnector(Connector):
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

@dataclass
class Step:
    name: str
    prog: str
    args: list[PositionalArgument | OptionalArgument] = field(default_factory=list)

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
                self.connections_in[(step.name, input.name)] = None
            self._active_steps.add(step.name)

    @property
    def connections_out(self):
        res = {}
        for step_name in self._active_steps:
            step = self.registry[step_name]
            for output in step.outputs:
                res[(step.name, output.name)] = []
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
