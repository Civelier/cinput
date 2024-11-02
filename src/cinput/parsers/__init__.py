from dataclasses import dataclass
from enum import Enum
from typing import Callable, Generic, Tuple, TypeVar, Union, TypeAlias

_TValue1 = TypeVar('_TValue1', int, float, bool, str)
_TValue2 = TypeVar('_TValue2', int, float, bool, str)
_TValue3 = TypeVar('_TValue3', int, float, bool, str)
_TNumber = TypeVar('_TNumber', int, float)


class _ParseError(Exception): ...

class EmptyInputError(_ParseError): ...
class NoneInputError(_ParseError): ...
class TypeInputError(_ParseError): ...
class ParseError(_ParseError): ...

class ParseStatus(Enum):
    SUCCESS = 0
    FAILED = 1
    SKIPPED = 2

@dataclass
class ParseResult(Generic[_TValue1]):
    value:Union[_TValue1,None]
    status:ParseStatus = ParseStatus.SUCCESS
    error:_ParseError = None


PreParser:TypeAlias = Callable[[str], ParseResult[_TValue1]]
PostParser:TypeAlias = Callable[[_TValue2], ParseResult[_TValue3]]


def engNotationParser(value:str) -> ParseResult[float]:
    if value is None:
        return ParseResult(None, ParseStatus.FAILED, NoneInputError("Value was None"))
    if not isinstance(value, str):
        return ParseResult(None, ParseStatus.FAILED, TypeInputError(f"Invalid type '{type(value)}'"))
    if len(value) == 0:
        return ParseResult(None, ParseStatus.FAILED, EmptyInputError("Input was empty"))
    n = value[-1]
    try:
        res = float(value.rstrip('munpKMGT'))
    except ValueError:
        return ParseResult(None, ParseStatus.FAILED, ParseError("Invalid input, notations include 'm, u, n, p, K, M, G, T'"))
    
    if n.isalpha():
        if n == 'm':
            res /= 1000
        if n == 'u':
            res /= 1000000
        if n == 'n':
            res /= 1000000000
        if n == 'p':
            res /= 1000000000000
        if n == 'K':
            res *= 1000
        if n == 'M':
            res *= 1000000
        if n == 'G':
            res *= 1000000000
        if n == 'T':
            res *= 1000000000000
    return ParseResult(res)

