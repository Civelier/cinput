import unittest
import unittest.mock
from cinput import SkipStep, cinput, intChoice, SkippedError
from cinput.parsers import engNotationParser
from cinput.validators import floatValidator, intValidator
from rich.console import Console

class TestConsole(unittest.TestCase):
    EOF_MESSAGE = "Test_STOP"
    def setUp(self):
        super().setUp()
        self.console = Console(no_color=True)
        self.skip = False
        
    def tearDown(self):
        super().tearDown()
        
    def onInput(self, result:str):
        self.console.input = unittest.mock.MagicMock(return_value=result)
        
    def onInputAndSkip(self, result:str):
        def side_effect(*args, **kwargs):
            if not self.skip:
                self.skip = True
                return result
            self.skip = False
            raise EOFError(self.EOF_MESSAGE)
        self.console.input = unittest.mock.MagicMock(side_effect=side_effect)
        
    def skipNextInput(self):
        self.console.input = unittest.mock.MagicMock(side_effect=EOFError(self.EOF_MESSAGE))
        
    def test_input(self):
        self.onInput("10")
        with self.console.capture() as cap:
            self.assertEqual(cinput("", int, console=self.console), 10)
        
    def test_skip(self):
        self.skipNextInput()
        with self.console.capture() as cap:
            self.assertRaises(SkippedError, lambda: cinput('', int, console=self.console))
        
    def test_eng_notation(self):
        def equals(value, expected):
            self.onInput(value)
            res = cinput('', preParser=engNotationParser, console=self.console)
            self.assertAlmostEqual(res, expected, None, f'Expected {expected} but found {res}.', 0.1*expected)
        def raises(value, text):
            self.onInputAndSkip(value)
            with self.console.capture() as cap:
                self.assertRaises(SkippedError, lambda: cinput('', preParser=engNotationParser, console=self.console))
            self.assertIn(text, cap.get().lower())
        tests = {
            equals : [
                ('10', 10),
                ('-58', -58),
                ('0', 0),
                ('10.32', 10.32),
                ('-20.45', -20.45),
                ('10m', 0.01),
                ('-58m', -0.058),
                ('0m', 0.0),
                ('10.32m', 0.01032),
                ('-20.45m', -0.02045),
                ('3u', 0.000003),
                ('3n', 0.000000003),
                ('3p', 0.000000000003),
                ('5K', 5000),
                ('5M', 5000000),
                ('5G', 5000000000),
                ('5T', 5000000000000),
            ],
            raises : [
                ('jlk', 'invalid'),
                ('-10t', 'invalid'),
                ('', 'empty'),
                ('m', 'invalid'),
            ]
        }
        
        for func, cases in tests.items():
            for case in cases:
                if isinstance(case, tuple):
                    func(*case)
                else:
                    func(case)
        
