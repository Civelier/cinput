from pprint import pprint
import sys
sys.path.append('./src')
from cinput import intChoice, parsers, validators, cinput, SkippedError

if __name__ == '__main__':
    try:
        # val = cinput('Enter an integer: ', int, 'Example',
        #        inputValidator=validators.intValidator())
        opts = [
            'Main menu',
            'Option 1',
            'Option 2',
            'Config',
        ]
        val = intChoice(opts, 'Menu selection')
    except SkippedError:
        pprint('Skipped')