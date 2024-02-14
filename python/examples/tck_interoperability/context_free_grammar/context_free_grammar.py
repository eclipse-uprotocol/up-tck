from abc import abstractmethod, ABC
from typing import List

class IContextFreeGrammar(ABC):
    @abstractmethod
    def parse_grammar(self, progress_commands: List[str], step_i: int) -> int:
        """parses and gets the required data from a Programed text file
        Should ALWAYS be ran 1st bc need to parse/understand written code

        Args:
            progress_commands (List[str]): command lines in the running text file
            step_i (int): current line in text file

        Returns:
            int: the new command line in text file
        """
        pass
    
    # @abstractmethod
    # def semantic_check(self):
    #     pass
    
    # @abstractmethod
    # def execute(self):
    #     pass

class Prog(IContextFreeGrammar):
    def __init__(self) -> None:
        self.stmt_seq = None

    def parse_grammar(self, progress_commands: List[str], step_i: int) -> int:
        # <prog> := <stmt-seq> | <just empty or have comments or spaces>
        
        # if theres nothing written
        if step_i >= len(progress_commands):
            return step_i
        
        self.stmt_seq = StmtSeq()
        return self.stmt_seq.parse_grammar(progress_commands, step_i)
            

class StmtSeq(IContextFreeGrammar):
    def __init__(self) -> None:
        self.stmt = None
        self.stmt_seq = None

    def parse_grammar(self, progress_commands: List[str], step_i: int) -> int:
        
        self.stmt = Stmt()
        step_i = self.stmt.parse_grammar(progress_commands, step_i)
        
        if step_i < len(progress_commands):
            self.stmt_seq = StmtSeq()
            return self.stmt_seq.parse_grammar(progress_commands, step_i)
        
        return step_i

class Stmt(IContextFreeGrammar):
    def __init__(self) -> None:
        # commands availabe for a Statement
        self.connect_to = None
        self.register_listener = None
        self.send = None
        self.respond_ustatus = None
        self.unregister_listener = None
    
    def parse_grammar(self, progress_commands: List[str], step_i: int) -> int:
        command_line = progress_commands[step_i]  
        command = command_line.split(" ")
        action = command[1]
        
        if action == "connect_to":
            self.connect_to = ConnectTo()
            step_i = self.connect_to.parse_grammar(progress_commands, step_i)
            
        elif action == "unregister_listener_command":
            self.unregister_listener = UnregisterListener()
            step_i = self.unregister_listener.parse_grammar(progress_commands, step_i)
        
        elif action == "send_command":
            self.send = Send()
            step_i = self.send.parse_grammar(progress_commands, step_i)
        
        elif action == "register_listener_command":
            self.register_listener = RegisterListener()
            step_i = self.register_listener.parse_grammar(progress_commands, step_i)
        
        elif action == "respond_ustatus":
            self.respond_ustatus = RespondUStatus()
            step_i = self.respond_ustatus.parse_grammar(progress_commands, step_i)
        else:
            print("Assuming Statement is in format \"<enactor> <action> <receiver>\" ... ")
            msg = "action " + action + " is not handleable! Only these actions: connect_to, unregister_listener_command, send_command, register_listener_command, and respond_ustatus"
            raise Exception(msg)

        return step_i
    
class ConnectTo(IContextFreeGrammar):
    def __init__(self) -> None:
        self.enactor: str = ""
        self.receiver: str = ""
    
    def parse_grammar(self, progress_commands: List[str], step_i: int) -> int:
        command_line = progress_commands[step_i]  
        tokens = command_line.split(" ")
        
        if len(tokens) != 3:
            raise Exception("Grammar should follow this format: <enactor> connect_to <receiver> ")
        elif tokens[2] != "test_manager":
            raise Exception("Test Agents can only connect to test_manager currently")

        # java_test_agent connect_to test_manager
        self.enactor = tokens[0]
        self.receiver = tokens[2]
        
        # NOTE: can keep enactor type in Memory / Stack of Maps
        
        enactor_tokens: str = self.enactor.split("_")
        if len(enactor_tokens) != 3 or not(enactor_tokens[1] == "test" and enactor_tokens[2] == "agent"):
            raise Exception("Test Agents Entities need to be formated like <sdk>_test_agent (e.g. java_test_agent, c++_test_agent)")

        sdk_name: str = enactor_tokens[0]
        
        return step_i + 1
        
class UnregisterListener(IContextFreeGrammar):
    def __init__(self) -> None:
        self.enactor: str = ""
        self.receiver: str = ""
    
    def parse_grammar(self, progress_commands: List[str], step_i: int) -> int:
        print(self.__class__)
        print(progress_commands[step_i])
        
        return step_i + 1

class Send(IContextFreeGrammar):
    def __init__(self) -> None:
        self.enactor: str = ""
        self.receiver: str = ""
    
    def parse_grammar(self, progress_commands: List[str], step_i: int) -> int:
        print(self.__class__)
        print(progress_commands[step_i])
        
        return step_i + 1
    
class RegisterListener(IContextFreeGrammar):
    def __init__(self) -> None:
        self.enactor: str = ""
        self.receiver: str = ""
    
    def parse_grammar(self, progress_commands: List[str], step_i: int) -> int:
        print(self.__class__)
        print(progress_commands[step_i])
        
        return step_i + 1
    
class RespondUStatus(IContextFreeGrammar):
    def __init__(self) -> None:
        self.enactor: str = ""
        self.receiver: str = ""
    
    def parse_grammar(self, progress_commands: List, step_i: int) -> int:
        print(self.__class__)
        print(progress_commands[step_i])
        
        return step_i + 1
