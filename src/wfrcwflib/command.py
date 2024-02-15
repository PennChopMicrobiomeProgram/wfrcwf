from typing import Optional
from dataclasses import dataclass, field
import subprocess
import collections
from pathlib import Path

        
class Project:
    def __init__(self, workflow, config, sources, output_dir):
        self.workflow = workflow
        self.config = config
        self.sources = sources
        self.output_dir = output_dir

    def is_complete(self):
        return all(s is not None for s in workflow.inputs.values())

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

    
    
