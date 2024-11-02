import unittest

# try:
from cinput.validators import floatValidator, intValidator
# except ModuleNotFoundError:
#     from ..src.cinput.validators import floatValidator, intValidator
    

class TestValidators(unittest.TestCase):
    def test_int_validator(self):
        v1 = intValidator()
        v1_true = [-100, -1, 0, 1, 100]
        v1_invalid_type = [0.0, -0.01, 0.1, 'hi', True]
        for v in v1_true:
            self.assertTrue(v1(v), f"Expected true for '{v}'")
            
        for v in v1_invalid_type:
            self.assertRaises(TypeError, lambda: v1(v), f"Expected TypeError for '{v}'")


if __name__ == "__main__":
    unittest.main()