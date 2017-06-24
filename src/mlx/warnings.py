import argparse
import re
import sys

DOXYGEN_WARNING_REGEX = r"(?:(?:((?:[/.]|[A-Za-z]:).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): (.+(?:\n(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*([Nn]otice|[Ww]arning|[Ee]rror): (.+))$"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"^(.+?:(?:\d+|None)): (DEBUG|INFO|WARNING|ERROR|SEVERE): (.+)\n?$"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

JUNIT_WARNING_REGEX = r"\<\s*failure\s+message"
junit_pattern = re.compile(JUNIT_WARNING_REGEX)

class WarningsPlugin:

    def __init__(self, sphinx, doxygen, junit):
        # type: (boolean, boolean, boolean) -> None
        '''
        Function for initializing the parsers

        Args:
            sphinx          enable sphinx parser
            doxygen         enable doxygen parser
            junit           enable junit parser
        '''
        if sphinx:
            self.sphinx = SphinxWarnings()
        if doxygen:
            self.doxygen = DoxygenWarnings()
        if junit:
            self.junit = JUnitWarnings()

    def check(self, line):
        # type: (string) -> None
        '''
        Function for running checks with each initalized parser
        '''
        try:
            self.sphinx.check(line)
        except AttributeError as e:
            pass

        try:
            self.doxygen.check(line)
        except AttributeError as e:
            pass

        try:
            self.junit.check(line)
        except AttributeError as e:
            pass

    def return_count(self):
        count = 0
        try:
            count += self.sphinx.return_count()
        except AttributeError as e:
            pass

        try:
            count += self.doxygen.return_count()
        except AttributeError as e:
            pass

        try:
            count += self.junit.return_count()
        except AttributeError as e:
            pass

        return count

class SphinxWarnings:

    def __init__(self):
        self.counter = 0

    def check(self, line):
        '''
        Function for counting the number of sphinx warnings in a logfile.
        The function returns the number of warnings found
        '''
        if re.search(sphinx_pattern, line):
            self.counter += 1

    def return_count(self):
        print("{count} sphinx warnings found".format(count=self.counter))
        return self.counter

class DoxygenWarnings:
    def __init__(self):
        self.counter = 0

    def check(self, line):
        '''
        Function for counting the number of doxygen warnings in a logfile.
        The function returns the number of warnings found
        '''
        if re.search(doxy_pattern, line):
            self.counter += 1

    def return_count(self):
        print("{count} doxygen warnings found".format(count=self.counter))
        return self.counter

class JUnitWarnings:
    def __init__(self):
        self.counter = 0

    def check(self, line):
        '''
        Function for counting the number of JUnit warnings in a xmlfile.
        The function returns the number of failing test cases found
        '''
        self.counter += len(re.findall(junit_pattern, line))

    def return_count(self):
        print("{count} junit failures found".format(count=self.counter))
        return self.counter


def main():
    parser = argparse.ArgumentParser(prog='mlx-warnings')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--doxygen', dest='doxygen', action='store_true')
    group.add_argument('-s', '--sphinx', dest='sphinx', action='store_true')
    group.add_argument('-j', '--junit', dest='junit', action='store_true')
    parser.add_argument('-m', '--maxwarnings', type=int, required=False, default=0,
                        help='Maximum amount of warnings accepted')
    parser.add_argument('--minwarnings', type=int, required=False, default=0,
                        help='Minimum amount of warnings accepted')

    parser.add_argument('logfile', help='Logfile that might contain warnings')
    args = parser.parse_args()

    warn_count = 0
    warn_max = args.maxwarnings
    warn_min = args.minwarnings

    warnings = WarningsPlugin(args.sphinx, args.doxygen, args.junit)

    for line in open(args.logfile, 'r'):
        warnings.check(line)

    warn_count = warnings.return_count()
    if warn_min > warn_max:
        print("Invalid argument: mininum limit ({min}) is higher than maximum limit ({max}). Returning error code 1.". format(min=warn_min, max=warn_max))
        sys.exit(1)
    elif warn_count > warn_max:
        print("Number of warnings ({count}) is higher than the maximum limit ({max}). Returning error code 1.".format(count=warn_count, max=warn_max))
        sys.exit(1)
    elif warn_count < warn_min:
        print("Number of warnings ({count}) is lower than the minimum limit ({min}). Returning error code 1.".format(count=warn_count, min=warn_min))
        sys.exit(1)
    else:
        print("Number of warnings ({count}) is between limits {min} and {max}. Well done.".format(count=warn_count, min=warn_min, max=warn_max))
        sys.exit(0)

