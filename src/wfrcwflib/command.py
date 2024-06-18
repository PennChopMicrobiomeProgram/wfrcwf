import argparse
from typing import Optional, TextIO
from dataclasses import dataclass, field
import subprocess
import collections
from pathlib import Path
from wfrcwflib.config import Config
from wfrcwflib.workflow import Workflow

        
class Project:
    def __init__(self, workflow: Workflow, config: Config, sources, output_dir: Path):
        self.workflow = workflow
        self.config = config
        # What is sources?
        self.sources = sources
        self.output_dir = output_dir

    def is_complete(self):
        return all(s is not None for s in self.workflow.inputs.values())

    def set(self, input, source):
        self.sources[input] = source

        
@dataclass
class LocalRunner:
    intermediate_dir: Path

    def step_output_dir(self, step):
        
        return self.intermediate_dir / step.name

    def run(self, workflow, sources, output_dir):
        for step in workflow.steps:
            configured_step = step.configure(config)
            job = configured_step.make_job(self)
            job.run()

    # @property
    # def argv(self):
    #     res = [self.prog]
    #     for arg in self._args:
    #         res.extend(list(arg.resolve()))
    #     return res

    # def set_input(self, name, value):
    #     input = self._inputs[name]
    #     input.value = value
                
    # def run(self):
    #     subprocess.run(self.argv)

    

class Job:
    def __init__(self, step, input_fps, output_fps):
        self.step = step
        self.input_fps = input_fps
        self.output_fps = output_fps

    
    
def main(argv = None):
    p = argparse.ArgumentParser()
    p.add_argument("-w", "--workflow", required=True, type=argparse.FileType("r"), help="Workflow file")
    p.add_argument("-c", "--config", required=True, type=argparse.FileType("r"), help="Config file")
    p.add_argument("-o", "--output-dir", default=".", type=Path, help="Output directory")

    args = p.parse_args(argv)

    args.output_dir.mkdir(parents = True, exist_ok = True)

    project = Project(args.workflow, args.config, {}, args.output_dir)