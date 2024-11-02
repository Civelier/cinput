from enum import Enum
from typing import AnyStr, Any, List, Callable, TypeVar, Union, Type, Dict, Tuple, get_type_hints, Optional, overload, get_args
import cinput.validators as validators
import cinput.parsers as parsers
from rich.console import Console
from rich.panel import Panel
from rich.bar import Bar
from rich.table import Table
from rich.pretty import pprint

_TPreParseOut = TypeVar('_TPreParseOut', str, int, float, bool)
_TPostParseOut = TypeVar('_TPostParseOut', str, int, float, bool)

class SkipStep(Enum):
    INPUT = 0
    PRE_PARSING = 1
    VALIDATING = 2
    POST_PARSING = 3

class SkippedError(Exception):
    def __init__(self, step:SkipStep):
        super().__init__(f"Skipped at step {step.name}.")
        self.step = step

def _infer_parser_input_type(parser: parsers.PreParser[_TPreParseOut]) -> Type:
    """Infers the input type from a pre-parser function based on type hints."""
    type_hints = get_type_hints(parser)
    input_type = type_hints.get('value')  # Assume the parser takes a string input
    if not input_type or input_type not in (int, float, bool, str):
        raise parsers.TypeInputError("Unsupported input type detected in preParser.")
    return input_type

def _infer_parser_return_type(parser: parsers.PostParser[_TPreParseOut, _TPostParseOut]) -> Type:
    """Infers the return type from a post-parser function based on type hints."""
    type_hints = get_type_hints(parser)
    return_type = type_hints.get('return')  # Expecting ParseResult as return type
    if not return_type or return_type.__origin__ != parsers.ParseResult:
        raise parsers.TypeInputError("Unsupported return type detected in postParser.")
    
    args = get_args(return_type)
    if not isinstance(args, tuple) or len(args) != 1:
        raise parsers.TypeInputError("Unsupported return type")
    arg = args[0]
    if not arg or arg not in (int, float, bool, str):
        raise parsers.TypeInputError("Unsupported return type detected in postParser.")
    return arg

def _infer_validator_input_type(validator: validators.Validator[_TPreParseOut]) -> Type:
    """Infers the input type from a validator function based on type hints."""
    type_hints = get_type_hints(validator)
    input_type = type_hints.get('value')
    if not input_type or input_type not in (int, float, bool, str):
        raise validators.ValidateTypeError("Unsupported input type detected in inputValidator.")
    return input_type


def cinput(
        prompt:AnyStr,
        returnType:Type[Union[int, float, bool, str, _TPostParseOut, _TPreParseOut]] = ..., 
        title:AnyStr = None, 
        skippable = True,
        inputType:Optional[Type[Union[int, float, bool, str, _TPostParseOut, _TPreParseOut]]] = ..., 
        options:Table = None, 
        inputValidator:validators.Validator[_TPreParseOut] = None, 
        preParser:parsers.PreParser[_TPreParseOut] = None, 
        postParser:parsers.PostParser[_TPreParseOut, _TPostParseOut] = None,
        console:Union[Console, None] = None,
        ) -> Union[_TPreParseOut, _TPostParseOut]:
    # Argument checks
    
    # Infer inputType if it's None or Ellipsis
    if inputType in (None, Ellipsis):
        if preParser is not None:
            inputType = _infer_parser_input_type(preParser)
        elif inputValidator is not None:
            inputType = _infer_validator_input_type(inputValidator)
        elif postParser is not None:
            inputType = _infer_parser_input_type(postParser)
    
    # Infer returnType if it's None or Ellipsis
    if returnType in (None, Ellipsis):
        if postParser is not None:
            returnType = _infer_parser_return_type(postParserParser)
        elif preParser is not None:
            returnType = _infer_parser_return_type(preParser) 
        elif inputValidator is not None:
            returnType = inputType  # Default to inputType if nothing else is inferred
            
    if inputType in (None, Ellipsis) and (returnType not in (None, Ellipsis)):
        inputType = returnType
    
    if returnType in (None, Ellipsis) and (inputType not in (None, Ellipsis)):
        returnType = inputType

    # Final check if both types could not be inferred
    if inputType is None or returnType is None:
        raise ValueError("Unable to infer required inputType or returnType.")

    # Additional argument validation logic
    if preParser is None and postParser is None and inputType is None and returnType is None:
        raise ValueError("Must specify at least one of inputType, returnType, preParser, or postParser.")

    # Check if required arguments are present
    if returnType is None and preParser is None and postParser is None:
        raise ValueError("Need at least a least one of these parameter: inputType, returnType, preParser, postParser.")
        
    # If no console is given, create one
    if console is None:
        console = Console(force_interactive=True)
        
    # Prompt user and convert result
    while True:
        
        # Generate renderable
        if options is not None:
            panel = Panel(options, title=title)
        else:
            panel = Panel("", title=title)
        
        # Capture input
        console.print(panel)
        try:
            v = console.input(prompt)
        except EOFError:
            if skippable:
                raise SkippedError(SkipStep.INPUT)
            else:
                console.print("[red]Cannot skip.[/red]")
                continue
        
        # Convert input type
        if inputType != str:
            try:
                v = inputType(v)
            except ValueError as e:
                console.print("[red]Invalid input conversion.[/red]")
                continue
                
        # Pre parse
        if preParser is not None:
            r = preParser(v)
            if r.status == parsers.ParseStatus.FAILED:
                console.print(f"[red]{str(r.error)}[/red]")
                continue
            if r.status == parsers.ParseStatus.SKIPPED:
                if skippable: 
                    raise SkippedError(SkipStep.PRE_PARSING)
                else:
                    console.print("[red]Cannot skip.[/red]")
                    continue
            v = r.value
            
        # Validate data
        if inputValidator is not None:
            r = inputValidator(v)
            if r.status == validators.ValidateStatus.FAILED:
                console.print(f"[red]{str(r.error)}[/red]")
                continue
            if r.status == validators.ValidateStatus.SKIPPED:
                if skippable:
                    raise SkippedError(SkipStep.VALIDATING)
                else:
                    console.print("[red]Cannot skip.[/red]")
                    continue
            
        # Post parse
        if postParser is not None:
            r = postParser(v)
            if r.status == parsers.ParseStatus.FAILED:
                console.print(f"[red]{str(r.error)}[/red]")
                continue
            if r.status == parsers.ParseStatus.SKIPPED:
                if skippable: 
                    raise SkippedError(SkipStep.POST_PARSING)
                else:
                    console.print("[red]Cannot skip.[/red]")
                    continue
        
        # Convert output
        if returnType != str:
            try:
                v = returnType(v)
            except ValueError as e:
                console.print("[red]Invalid output conversion.[/red]")
        
        return v

def intChoice(options:List[str], title:AnyStr=None, includeBack=True, skippable=True, console:Console=None) -> Tuple[int, Union[None, str]]:
    """Displays a list of the options with a number to select them
    prompt: Prompt to display before the list of options
    options: List of str to display
    returns: (res, option)
    res: -1 if 'Back' was selected. (0 to len(options) - 1) if a value was selected.
    option: None if 'Back' was selected. Name of the option 'option[res]'"""
    t = Table('Index', 'Option')
    if includeBack:
        t.add_row('-1', 'Back')
        
    for i, o in enumerate(options):
        t.add_row(str(i), o)
    validator = validators.intValidator(-1 if includeBack else 0, len(options))
    res = cinput(f"Input number (0-{len(options)}): ", int, title=title, inputType=int, inputValidator=validator, skippable=skippable, options=t, console=console)
    if res == -1:
        return res, None
    return res, options[res]

def engNotationInput(prompt:str, title:AnyStr=None, skippable=True, console:Console=None):
    return cinput(prompt, float, title=title, skippable=skippable, console=console, inputType=str, preParser=parsers.engNotationParser)

Menu = Union[Callable, Dict[str, Union[Callable,Dict[str,Any]]]]

def menuInput(menu:Menu, name:str):
    stk = []
    while True:
        if callable(menu):
            print(name)
            menu()
            menu = stk.pop()
        if isinstance(menu, dict):
            r, opt = intChoice(f"{name}>", list(menu.keys()))
            if r == 0:
                if len(stk) == 0:
                    return
                menu = stk.pop()
                continue
            stk.append(menu)
            menu = menu[opt]

