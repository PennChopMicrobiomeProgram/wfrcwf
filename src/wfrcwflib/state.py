from dataclasses import dataclass
from typing import Optional, Callable

class State:
    pass

@dataclass
class KeywordState(State):
    name: str
    transitions: list[State]
    terminal: bool = False
    
    def check(self, tok):
        tok == self.name

@dataclass
class RegexState(State):
    name: str
    pattern: str
    transitions: list[State]
    terminal: bool = False

    def check(self, tok):
        re.match(self.pattern, tok)


s_step_option_value = RegexState("value", ".+", [s_step_option_value, s_step_argument_sep])
s_step_option_flag = RegexState("flag", "-", [s_step_option_value, s_step_argument_sep])
s_step_argument_sep = KeywordState("\n", [s_step_option_flag], terminal = True)
s_step_resource = RegexState("resource", ".+", [s_step_argument_sep])
s_step_name_sep = KeywordState("\n", [s_step_resource])
s_step_name = RegexState("name", "[a-z][a-z_]", [s_step_name_sep]) 
s_step = KeywordState("step", [s_step_name])
s_init = KeywordState("init", [s_step])

class WFSM:
    def __init__(self):
        state = s_init

    def consume(self, tok):
        next = self.next_state(tok)
        
    def next_state(self, tok):
        for s in self.state.transitions:
            if s.check(tok):
                return s
        return None
            
