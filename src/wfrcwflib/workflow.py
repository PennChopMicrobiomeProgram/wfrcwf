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
                yield input.name

    @property
    def outputs(self):
        for arg in self.args:
            for output in arg.outputs:
                yield output.name

class Workflow:
    def __init__(self, step):
        self.steps = {}
        self.connections_in = {}
        # The first step in the workflow has no connections
        self.add_step(step, {})

    def add_step(self, step, connections):
        """Add a step to the workflow

        Inputs of the step to be added are connected to outputs of a
        previous step.  The input of a step can only be connected to
        one output. As a result, the data model for `connections` is a
        dict: input => (prev_step, output).
        """
        self.steps[step.name] = step
        for input in step.inputs:
            self.connections_in[(step.name, input)] = None
        for input, (prev_step, output) in connections.items():
            self.connections_in[(step.name, input)] = (prev_step, output)

    @property
    def connections_out(self):
        res = {}
        for step in self.steps.values():
            for output in step.outputs:
                res[(step.name, output)] = []
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
        graph = {step: set() for step in self.steps.keys()}
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
