import sys
import glob
import os
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
import argparse
import pkg_resources
__version__ = pkg_resources.get_distribution('norminette').version
from lexer import Lexer, TokenError
from exceptions import CParsingError
from registry import Registry
from context import Context
from tools.colors import colors
# import sentry_sdk

# sentry_sdk.init("https://e67d9ba802fe430bab932d7b11c9b028@sentry.42.fr/72")


has_err = False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="File(s) or folder(s) you wanna run the parser on. If no file provided, runs on current folder.", default=[], action='append', nargs='*')
    parser.add_argument("-d", "--debug", action="count", help="Debug output (multiple values available)", default=0)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('--cfile', action='store', help="Store C file content directly instead of filename")
    parser.add_argument('--hfile', action='store', help="Store header file content directly instead of filename")
    args = parser.parse_args()
    registry = Registry()
    targets = []
    has_err = None

    debug = args.debug
    print (args)
    if args.cfile != None or args.hfile != None:
        from_content = True
        targets = ['file.c'] if args.cfile else ['file.h']
        content = args.cfile if args.cfile else args.hfile
    else:
        from_content = False
        args.file = args.file[0]
        if args.file == [[]] or args.file == []:
            targets = glob.glob("**/*.[ch]", recursive=True)
            target = targets.sort()
        else:
            for arg in args.file:
                if os.path.exists(arg) is False:
                    print(f"'{arg}' no such file or directory")
                elif os.path.isdir(arg):
                    if arg[-1] != '/':
                        arg = arg + '/'
                    targets.extend(glob.glob(arg + '**/*.[ch]', recursive=True))
                elif os.path.isfile(arg):
                    targets.append(arg)

    for target in targets:
        if target[-2:] not in [".c", ".h"]:
            print(f"{arg} is not valid C or C header file")
        else:
            try:
                if from_content == False:
                    with open(target) as f:
                        #print ("Running on", target)
                        source = f.read()
                else:
                    source = content
                lexer = Lexer(source)
                tokens = lexer.get_tokens()
                context = Context(target, tokens, debug)
                registry.run(context, source)
                if context.errors is not []:
                    has_err = True
            # except (TokenError, CParsingError) as e:
            except TokenError as e:
                has_err = True
                print(target + f": KO!\n\t{colors(e.msg, 'red')}")
            except CParsingError as e:
                has_err = True
                print(target + f": KO!\n\t{colors(e.msg, 'red')}")

    sys.exit(1 if has_err else 0)

if __name__ == "__main__":
    main()