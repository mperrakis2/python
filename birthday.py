"""This program calculates the probability that a single birthday occurs a certain number of times
within a set of birthdays that make a sample. The number of birthdays in a sample make up one
iteration.

To get statistically accurate results many iterations are executed.

When a birthday occurs a certain number of times within an iteration the total number of matches is
incremented. Thus, the probability that a birthday occurs a certain number of times is
(total number of matches / iterations).
"""
import sys
import random
import argparse

import utility

# Inherit class that provides functionality for adding two instances of the derived class and
# reference counting as well.
class Birthday(utility.AdderWithRefCount):
    """Provide functionality to generate random birthdays within a year range specified by the
    user. Calculate if a single birthday occurs more than once within the generated random
    birthdays and save the number of matches.
    """
    ITERATIONS = 10_000
    SAMPLES = 23
    BEGIN_YEAR = 1941
    END_YEAR = 2001
    OCCUR = 2

    def __init__(self):
        """ctor"""
        super().__init__()
        self.__iterations = Birthday.ITERATIONS # number of iterations to execute
        self.__samples = Birthday.SAMPLES # number of samples per iteration
        self.__begin_year = Birthday.BEGIN_YEAR # earliest birth year to generate
        self.__end_year = Birthday.END_YEAR # oldest birth year to generate
        self.__occur = Birthday.OCCUR # expected number of same birthdays per iteration
        self.__hits = 0 # number of same birthdays per iteration

    def generate(self,
                 iterations = ITERATIONS,
                 samples = SAMPLES,
                 begin_year = BEGIN_YEAR,
                 end_year = END_YEAR,
                 occur = OCCUR,
                 append = False):
        """Calculate the probability that a birthday occurs certain times within a sample.

        'samples' is the maximun number of birthdays generated in a single iteration. To get
        statistically accurate results, the iteration is repeated a number of times equal to
        'iterations'. Thus, the maximum number of birthdays that can be generated is
        'samples' * 'iterations'.

        When a birthday occurs certain times within an iteration the total number of matches is
        incremented.

        iterations: int, the number of times to iterate in order to generate a number of birthdays
                    per iteration.
        samples   : int, the maximum number of birthdays generated in a single iteration
        begin_year: int, the gererated random years should not be earlier than this year
        end_year  : int, the gererated random years should not be later than this year
        occur     : int, the number of times a single birthday should occur within a sample
        append    : bool, if True append to current matches else just generate new ones
        """
        _param_error(iterations, samples, begin_year, end_year, occur, append)

        self.__reset(iterations, samples, begin_year, end_year, occur, append)

        for i in range(iterations):
            # Generate a maximum number of birthdays equal to 'samples'. If the number of birthdays
            # that are the same is equal to 'occur' then a match (the number one) is returned.
            self.__hits += self.__generate()

    @property
    def matches(self):
        """return: int, the number of matches"""
        return self.__hits

    @property
    def iterations(self):
        """return: int number of iterations"""
        return self.__iterations

    @property
    def samples(self):
        """return: int, number of samples"""
        return self.__samples

    @property
    def begin_year(self):
        """Return the begin year."""
        return self.__begin_year

    @property
    def end_year(self):
        """return: int, the end year"""
        return self.__end_year

    @property
    def occur(self):
        """return: int, the number of times of a birthday within a sample"""
        return self.__occur

    def clear(self):
        """Clear all birthday data."""
        self.__reset(Birthday.ITERATIONS,
                     Birthday.SAMPLES,
                     Birthday.BEGIN_YEAR,
                     Birthday.END_YEAR,
                     Birthday.OCCUR,
                     False)
        super().clear()

    def __str__(self):
        """Called when printing a bday object.

        return: str, a formatted string of bday data
        """
        probability = self.__hits / self.__iterations

        bday_data  = f"samples   : {self.__samples}\n"
        bday_data += f"begin year: {self.__begin_year}\n"
        bday_data += f"end year  : {self.__end_year}\n"
        bday_data += f"occurences: {self.__occur}\n\n"
        bday_data += f"matches   : {self.__hits}\n"
        bday_data += f"iterations: {self.__iterations}\n\n"
        bday_data += f"(matches / iterations) = ({self.__hits} / {self.__iterations}) = " \
                     f"{probability} = {probability:.3%}"

        return bday_data

    def __repr__(self):
        """Called when calling the representation (repr(birthday_obj)) of a birthday object.

        return: str, the representation which allows a birthday object to be identified
        """
        return f"<type: {self.__class__.__module__}.{self.__class__.__name__},"\
               f" id: {id(self)}>"

    def __call__(self):
        """See doc of returned method."""
        return self.matches

    def __bool__(self):
        """Called when a birthday object is used as a boolean in an expression.

        return: bool
        """
        return bool(self.__hits)

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: Birthday, the birthday object to compare with

        return: bool or NotImplemented
                bool          : True if two birthday objects are equal
                NotImplemented: if there's a parameter error
        """
        if not isinstance(other, Birthday):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        return self.__iterations == other.iterations and \
               self._is_add(other) and \
               self.__hits == other.matches

    def _is_add(self, other):
        """Check if two birthday objects are compatible.

        other: Birthday, the birthday object to compare this one to

        return: bool, True if both birthday objects are compatible
        """
        return self.__samples == other.samples and \
               self.__begin_year == other.begin_year and \
               self.__end_year == other.end_year and \
               self.__occur == other.occur

    def _op_add(self, other):
        """ Add a birthday object to this one.

            other: Birthday
        """
        self.__iterations += other.iterations
        self.__hits += other.matches

    def __reset(self, iterations, samples, begin_year, end_year, occur, append):
        """Reset attributes.

        iterations: int, the number of times to iterate in order to generate a number of birthdays
                    ('samples') per iteration.
        samples   : int, the maximum number of birthdays generated in a single iteration
        begin_year: int, the gererated random years should not be earlier than this year
        end_year  : int, the gererated random years should not be later than this year
        occur     : int, the number of times a single birthday should occur within a sample
        append    : bool, if True append to current matches else just generate new ones
        """
        if append and \
           (self.__samples != samples or \
            self.__begin_year != begin_year or \
            self.__end_year != end_year or \
            self.__occur != occur):
            raise ValueError("error: when appending, the current values of "
                             "samples, begin year, end year and occurences "
                             "must be the same as the new ones")

        if append:
            self.__iterations += iterations
        elif self.__iterations != iterations:
            self.__iterations = iterations
        if self.__samples != samples:
            self.__samples = samples
        if self.__begin_year != begin_year:
            self.__begin_year = begin_year
        if self.__end_year != end_year:
            self.__end_year = end_year
        if self.__occur != occur:
            self.__occur = occur
        if not append:
            self.__hits = 0

    def __generate(self):
        """Generate birthday samples.

        Generate birthday samples until a sample appears a certain number of times or the maximum
        number of samples is generated.

        A birthday is a tuple in the form (year, month, day) where 'year', 'month' and 'day' are
        ints.

        return: int, 1 if a single birthday has occured a number of times, 0 otherwise
        """
        bdays = set()
        occur = self.__occur
        for i in range(self.__samples):
            year = random.randint(self.__begin_year, self.__end_year)
            month = random.randint(1, 12)
            if month in (1, 3, 5, 7, 8, 10, 12):
                day = random.randint(1, 31) # day up to 31 days
            elif month in (4, 6, 9, 11):
                day = random.randint(1, 30) # day up to 30 days
            elif _leap_year(year):
                day = random.randint(1, 29) # february and leap, day up to 29 days
            else:
                day = random.randint(1, 28) # february and not leap, day up to 28 days

            bday = (year, month, day)
            if bday in bdays:
                occur -= 1
                if occur == 1:
                    return 1
            else:
                bdays.add(bday)

        return 0

_DESC = """\
Generate random birthdays based on user input and calculate the probability of a single birthday
being generated more than once.
"""

def main():
    """Main entry point.

    return: int, success or failure
    """
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = _DESC,
                                     epilog = 'usage example: '
                                              f'python {sys.argv[0]}'
                                              ' -i 20000 -s 25 -b 1941 -e 2001 -o 3')
    parser.add_argument('-i', '--iterations', type = int,
                        default = 10000,
                        help = "the number of iterations to run, must be > 0 (default: 10000)")
    parser.add_argument('-s', '--samples', type = int,
                        default = 23,
                        help = "the number of random birthdays to generate per iteration"
                               ", must be > 1 (default: 23)")
    parser.add_argument('-b', '--begin-year', type = int, dest = "begin_year",
                        required = True,
                        help = "the smallest year for a birthday, must be > 0")
    parser.add_argument('-e', '--end-year', type = int, dest = "end_year",
                        required = True,
                        help = "the largest year for a birthday, must be > 0")
    parser.add_argument('-o', '--occur', type = int,
                        default = 2,
                        help = "the number of times a birthday should be repeated in the samples"
                               " of an iteration, must be < samples (default: 2)")
    args  = parser.parse_args()

    birthday = Birthday()
    birthday.generate(args.iterations, args.samples, args.begin_year, args.end_year, args.occur)
    print(birthday)

    return 0

def _param_error(iterations, samples, begin_year, end_year, occur, append):
    """Validate parameters.

    iterations: int, the number of times to iterate in order to generate a number of birthdays
                ('samples') per iteration.
    samples   : int, the maximum number of birthdays generated in a single iteration
    begin_year: int, the gererated random years should not be earlier than this year
    end_year  : int, the gererated random years should not be later than this year
    occur     : int, the number of times a single birthday should occur within a sample
    append    : bool, if True append to current matches else just generate new ones

    exceptions: ValueError
    """
    if not isinstance(iterations, int) or \
       not isinstance(samples, int) or \
       not isinstance(begin_year, int) or \
       not isinstance(end_year, int) or \
       not isinstance(occur, int) or \
       not isinstance(append, bool):
        raise ValueError("error: all parameters must be of type 'int' "
                         "except for 'append' which is 'bool'")

    if iterations < 1 or \
       samples < 2 or \
       begin_year < 1 or \
       end_year < 1 or \
       occur < 2 or \
       begin_year > end_year or \
       occur >= samples:
        raise ValueError("error: all parameters must be > 0\n"
                         "and 'occur' > 1\nand 'samples' > 1\nand 'occur' < 'samples'\n"
                         "and 'begin_year' <= 'end_year'")

def _leap_year(year):
    """Calculate if a year is leap.

    year: int

    return: bool, True if leap
    """
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
        else:
            return True

    return False

if __name__ == '__main__':
    sys.exit(main())
