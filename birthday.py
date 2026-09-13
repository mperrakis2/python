"""This program calculates the probability that a single birthday occurs
a certain number of times within a set of birthdays that make a sample.
The number of birthdays in a sample make up one iteration.

To get statistically accurate results many iterations are executed.

When a birthday occurs a certain number of times within an iteration the
total number of matches is incremented. Thus, the probability that a
birthday occurs a certain number of times is
(total number of matches / iterations).
"""
import sys
import random
import argparse

import utility

# Inherit class that provides functionality for adding two instances of
# the derived class and reference counting as well.
class Birthday(utility.AdderWithRefCount):
    """Provide functionality to generate random birthdays within a year
    range specified by the user. Calculate if a single birthday occurs
    more than once within the generated random birthdays and save the
    number of matches.
    """
    ITERATIONS = 10_000
    SAMPLES = 23
    BEGIN_YEAR = 1941
    END_YEAR = 2001
    COUNT = 2

    def __init__(self):
        """ctor"""
        super().__init__()
        self.__iterations = Birthday.ITERATIONS # iterations to execute
        self.__samples = Birthday.SAMPLES # samples per iteration
        self.__begin_year = Birthday.BEGIN_YEAR # earliest birth year
        self.__end_year = Birthday.END_YEAR # oldest birth yea
        self.__count = Birthday.COUNT # same birthdays per iteration
        self.__hits = 0 # num of same birthdays per iteration

    def generate(self,
                 iterations = ITERATIONS,
                 samples = SAMPLES,
                 begin_year = BEGIN_YEAR,
                 end_year = END_YEAR,
                 count = COUNT,
                 append = False):
        """Calculate the probability of birthday occuring within sample.

        'samples' is the maximun number of birthdays generated in a 
        single iteration. To get statistically accurate results, the
        iteration is repeated a number of times equal to 'iterations'.
        Thus, the maximum number of birthdays that can be generated is
        'samples' * 'iterations'.

        When a birthday occurs certain times within an iteration the
        total number of matches is incremented.

        iterations: int, the number of times to iterate in order to 
                    generate a number of birthdays per iteration.
        samples   : int, the maximum number of birthdays generated in a
                    single iteration
        begin_year: int, gererated random years should not be earlier
                    than this year
        end_year  : int, the gererated random years should not be later
                    than this year
        count     : int, the number of times a single birthday should
                    occur within a sample
        append    : bool, if True append to current matches else just
                    generate new ones
        """
        _param_error(iterations, samples, begin_year, end_year, count, append)

        self.__reset(iterations, samples, begin_year, end_year, count, append)

        for i in range(iterations):
            # Generate a maximum number of birthdays equal to 'samples'.
            # If the number of birthdays that are the same is equal to 
            # 'count' then a match (the number one) is returned.
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
    def count(self):
        """return: int, num of times of a birthday within a sample"""
        return self.__count

    def clear(self):
        """Clear all birthday data."""
        self.__reset(Birthday.ITERATIONS,
                     Birthday.SAMPLES,
                     Birthday.BEGIN_YEAR,
                     Birthday.END_YEAR,
                     Birthday.COUNT,
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
        bday_data += f"occurences: {self.__count}\n\n"
        bday_data += f"matches   : {self.__hits}\n"
        bday_data += f"iterations: {self.__iterations}\n\n"
        bday_data += f"(matches / iterations) = ({self.__hits} / {self.__iterations}) = " \
                     f"{probability} = {probability:.3%}"

        return bday_data

    def __repr__(self):
        """Called when calling repr(obj) on a birthday obj.

        return: str, the repr which identifies a birthday obj
        """
        return f"<type: {self.__class__.__module__}.{self.__class__.__name__},"\
               f" id: {id(self)}>"

    def __call__(self):
        """See doc of returned method."""
        return self.matches

    def __bool__(self):
        """Called when birthday object is used as a bool in expression.

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
               self.__count == other.count

    def _add(self, other):
        """ Add a birthday object to this one.

            other: Birthday
        """
        self.__iterations += other.iterations
        self.__hits += other.matches

    def __reset(self, iterations, samples, begin_year, end_year, count, append):
        """Reset attributes.

        iterations: int, the num of times to iterate to generate a num 
                    of birthdays ('samples') per iteration.
        samples   : int, the maximum number of birthdays generated in a 
                    single iteration
        begin_year: int, gererated random years should not be earlier
                    than this year
        end_year  : int, the gererated random years should not be later
                    than this year
        count     : int, the number of times a single birthday should
                    occur within a sample
        append    : bool, if True append to current matches else just
                    generate new ones
        """
        if append and \
           (self.__samples != samples or \
            self.__begin_year != begin_year or \
            self.__end_year != end_year or \
            self.__count != count):
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
        if self.__count != count:
            self.__count = count
        if not append:
            self.__hits = 0

    def __generate(self):
        """Generate birthday samples.

        Generate birthday samples until a sample appears a certain
        number of times or the maximum number of samples is generated.

        A birthday is a tuple in the form (year, month, day) where 
        'year', 'month' and 'day' are ints.

        return: int, 1 if a birthday has occured a number of times,
                0 otherwise
        """
        bdays = set()
        count = self.__count
        for i in range(self.__samples):
            year = random.randint(self.__begin_year, self.__end_year)
            month = random.randint(1, 12)
            if month in (1, 3, 5, 7, 8, 10, 12): # <= 31 days
                day = random.randint(1, 31)
            elif month in (4, 6, 9, 11):  # <= 30 days
                day = random.randint(1, 30)
            elif _leap_year(year):        # feb and leap, <= 29 days
                day = random.randint(1, 29)
            else:                         # feb and not leap, <= 28 days
                day = random.randint(1, 28) 

            bday = (year, month, day)
            if bday in bdays:
                count -= 1
                if count == 1:
                    return 1
            else:
                bdays.add(bday)

        return 0

_DESC = """\
Generate random birthdays based on user input and calculate the probability of
a single birthday being generated more than once.
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
                        help = "the number of iterations to run, must be > 0 "
                               "(default: 10000)")
    parser.add_argument('-s', '--samples', type = int,
                        default = 23,
                        help = "the number of random birthdays to generate per "
                               "iteration, must be > 1 (default: 23)")
    parser.add_argument('-b', '--begin-year', type = int, dest = "begin_year",
                        required = True,
                        help = "the smallest year for a birthday, must be > 0")
    parser.add_argument('-e', '--end-year', type = int, dest = "end_year",
                        required = True,
                        help = "the largest year for a birthday, must be > 0")
    parser.add_argument('-o', '--occur', type = int,
                        default = 2,
                        help = "the number of times a birthday should be "
                               "repeated in the samples of an iteration, must "
                               "be < samples (default: 2)")
    args  = parser.parse_args()

    birthday = Birthday()
    birthday.generate(args.iterations, args.samples, args.begin_year, 
                      args.end_year, args.occur)
    print(birthday)

    return 0

def _param_error(iterations, samples, begin_year, end_year, count, append):
    """Validate parameters.

    iterations: int, the number of times to iterate in order to generate
                a number of birthdays ('samples') per iteration.
    samples   : int, the maximum number of birthdays generated in a
                single iteration
    begin_year: int, the gererated random years should not be earlier
                than this year
    end_year  : int, the gererated random years should not be later than
                this year
    count     : int, the number of times a single birthday should occur
                within a sample
    append    : bool, if True append to current matches else generate
                new ones

    exceptions: ValueError
    """
    if not isinstance(iterations, int) or \
       not isinstance(samples, int) or \
       not isinstance(begin_year, int) or \
       not isinstance(end_year, int) or \
       not isinstance(count, int) or \
       not isinstance(append, bool):
        raise ValueError("error: all parameters must be of type 'int' "
                         "except for 'append' which is 'bool'")

    if iterations < 1 or \
       samples < 2 or \
       begin_year < 1 or \
       end_year < 1 or \
       count < 2 or \
       begin_year > end_year or \
       count >= samples:
        raise ValueError("error: all parameters must be > 0\n"
                         "and 'occur' > 1\nand 'samples' > 1\n"
                         "and 'occur' < 'samples'\n"
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
