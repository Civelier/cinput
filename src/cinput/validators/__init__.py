from dataclasses import dataclass
from enum import Enum
from typing import Generic, Callable, Optional, TypeVar, Union, TypeAlias

_TValue1 = TypeVar('_TValue1', int, float, bool, str)


class _ValidateError(Exception): ...

class ValidateEmptyError(_ValidateError): ...
class ValidateNoneError(_ValidateError): ...
class ValidateTypeError(_ValidateError): ...
class ValidateError(_ValidateError): ...

class ValidateStatus(Enum):
    SUCCESS = 0
    FAILED = 1
    SKIPPED = 2

@dataclass
class ValidateResult:
    status:ValidateStatus = ValidateStatus.SUCCESS
    error:_ValidateError = None

Validator:TypeAlias = Callable[[_TValue1], ValidateResult]

def intValidator(minVal:Optional[int]=None, maxVal:Optional[int]=None) -> Validator[int]:
	def pred(value:int) -> ValidateResult:
		if value is None:
			return ValidateResult(ValidateStatus.FAILED, ValidateNoneError("Value was None"))
		if not isinstance(value, int):
			return ValidateResult(ValidateStatus.FAILED, ValidateTypeError("Invalid type"))
		if (minVal is not None and minVal > value) or (maxVal is not None and maxVal <= value):
			msg = "Value must be " + (f"greater than '{minVal}' inclusively" if minVal is not None else "") +\
       			(" and " if minVal is not None and  maxVal is not None else "") +\
              	(f" lower than '{maxVal}' exclusively" if maxVal is not None else ".")
			return ValidateResult(ValidateStatus.FAILED, ValidateError(msg))
		return ValidateResult()
	return pred


def floatValidator(minVal:Optional[float]=None, maxVal:Optional[float]=None) -> Validator[float]:
	def pred(value:float) -> ValidateResult:
		if value is None:
			return ValidateResult(ValidateStatus.FAILED, ValidateNoneError("Value was None"))
		if not isinstance(value, float):
			return ValidateResult(ValidateStatus.FAILED, ValidateTypeError("Invalid type"))
		if (minVal is not None and minVal > value) or (maxVal is not None and maxVal <= value):
			msg = "Value must be " + (f"greater than '{minVal}' inclusively" if minVal is not None else "") +\
       			(" and " if minVal is not None and  maxVal is not None else "") +\
              	(f" lower than '{maxVal}' exclusively" if maxVal is not None else ".")
			return ValidateResult(ValidateStatus.FAILED, ValidateError(msg))
		return ValidateResult()
	return pred

