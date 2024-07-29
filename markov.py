"""Tnis program produces random text based on one or more text files read from the command line. A
dictionary of prefix-suffix pairs is created based on the text files read. A prefix consists of one
or more consequtive words from a file and the suffix is the word that immediately follows the
prefix.

A prefix may repeat itself many times in a file and each time it could be followed by a different
suffix. Thus, each prefix has a list of suffixes.
"""
import sys
import string
import random
import fileinput
import copy
import argparse
import collections.abc

import utility

# Inherit class that provides functionality for adding two instances of the derived class and
# reference counting as well.
class RandomText(utility.AdderWithRefCount):
    """Read text files and create a dictionary of prefix/suffix pairs. The prefix is a number of
    consecutive words from a file and the suffix is the word that immediately follows the suffix.

    The prefix length is the number of words in the prefix.

    A method exists that returns a random number of entries in the dictionary.
    """
    def __init__(self):
        """ctor"""
        super().__init__()
        self.__reset()

    def create(self, length, /, *filenames, strip = True, reset = False):
        """Create a dictionary of prefix-suffix pairs based on the files read.

        A prefix consists of one or more consequtive words in a file and the suffix is the word that
        immediately follows the prefix.

        A prefix may repeat itself many times in a file each time being followed (possibly) by a
        different suffix. Thus, each prefix may correspond to a list of suffixes.

        length   : int, the number of words that make a prefix
        filenames: tuple of str, files to read in order to produce random text
        strip    : bool, if True the words that are read from the files are stripped of punctuation
                   chars
        reset    : bool, True if existing random text is to be deleted

        return: bool, True if successful
        """
        if _param_error(length, strip, reset, *filenames): # check parameters
            return False

        if self.__length != length or self.__strip != strip or reset:
            self.__length = length
            self.__strip = strip
            self.__filenames.clear()
            self.__random_text.clear()

        # get filenames based on old ones
        filenames = utility.get_filenames(filenames, self.__filenames)
        if filenames:
            try:
                # read the contents of the text files and create dictionary of prefix/suffix pairs
                with fileinput.input(filenames, encoding="utf-8") as file:
                    # create string of chars to be stripped from words read from the files
                    chars = self.__strip_chars()
                    prefix = ()

                    for line in file:
                        line = line.replace('-', ' ')
                        for word in line.split(): # loop through the words of a single line
                            word = word.strip(chars)
                            if word:
                                # add the word to the prefix and to the suffix if the prefix is of
                                # full length
                                prefix = self.__add_word(prefix, word.lower())
                    self.__filenames.add(fileinput.filename())
            except OSError as exc:
                print(exc)
                return False

        return True

    def sample(self, samples):
        """Return a list of random prefix-suffix pairs from the random text dictionary.

        samples: int > 0, number of random samples to read from the dictionary of
                 prefix-suffix pairs

        return: list, the randomly retrieved samples
        """
        rand_samples = []

        if not isinstance(samples, int) or samples < 1:
            print("error: 'samples' has to be of type 'int' > 0")
            return rand_samples

        # if no param error proceed
        if self.__random_text:
            # convert random text dictionary to a list as the 'choice' function of the random
            # module requires a sequence to iterate over
            rand_text = list(self.__random_text.items())
            for i in range(samples):
                # choose a random prefix-suffix pair from the list
                rand_sample = random.choice(rand_text)
                rand_samples.append(rand_sample[0]) # the prefix

                # choose a random suffix from the list of suffixes
                rand_samples.append(random.choice(rand_sample[1]))

        return rand_samples

    @property
    def length(self):
        """return: int, the length of the prefix, i.e. the number of words"""
        return self.__length

    @property
    def strip(self):
        """return: bool, True if words are stripped of punctuation chars"""
        return self.__strip

    @property
    def filenames(self):
        """return: set of str, the files read so far"""
        return self.__filenames

    @property
    def random_text(self):
        """return: dict of random text, key  : prefix (a number of words)
                                        value: suffix (a single word)
        """
        return self.__random_text

    def clear(self):
        """Clear all random text data."""
        self.__reset()
        super().clear()

    def __str__(self):
        """Called when printing a random text object.

        return: str, a formatted string of random text
        """
        return str(self.__random_text)

    def __repr__(self):
        """Called when calling the representation (repr(random_text_obj)) of a random text object.

        return: str, the representation which allows an object equal to this one to be created
        """
        random_text = f"random_text = {self.__class__.__module__}.{self.__class__.__name__}()"
        if self.__random_text:
            random_text += f"\nrandom_text.read({self.__length}, {self.__strip}, True, "
            for filename in self.__filenames:
                random_text += f"{filename}, "
            random_text += ")"

        return random_text

    def __call__(self, samples):
        """See doc of returned method."""
        return self.sample(samples)

    def __bool__(self):
        """Called when a random text object is used as a boolean in an expression.

        return: bool, see __len__()
        """
        return bool(self.__len__())

    def __len__(self):
        """Called when calling the length (len(random_text_obj)) of a random text object.

        return: int, the number of prefix-suffix pairs
        """
        return len(self.__random_text)

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: RandomText, the random text object to compare with

        return: bool or NotImplemented
                bool          :True if random text objects are equal
                NotImplemented: if there's a parameter error
        """
        if not isinstance(other, RandomText):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        return self.__length == other.length and \
               self.__strip == other.strip and \
               self.__filenames == other.filenames

    def __iter__(self):
        """Called whenever an iterator of a random text object is requested.

        return: iterator object, a random text object iterator
        """
        return iter(self.__random_text)

    def __getitem__(self, key):
        """Called when implementing evaluation of self[key].

        key: tuple of str, a prefix

        return: str, a suffix

        exceptions: TypeError, if key is of an inappropriate type
                    KeyError, if key is not in the container
        """
        return self.__random_text[key]

    def _is_add(self, other):
        """Check if two random text objects can be added.

        other: RandomText, the random text object to compare this one to

        return: bool, True if both random text objects can be added
        """
        for filename in self.__filenames:
            if filename in other.filenames:
                return False

        return self.__length == other.length and self.__strip == other.strip

    def _op_add(self, other):
        """Add a random text object to this one.

        other: RandomText
        """
        self.__filenames |= other.filenames
        if not self.__random_text: # if self is empty just do a deep copy of random text
            self.__random_text = copy.deepcopy(other.random_text)
            return

        # add dictionary of other to dictionary of self
        for prefix, suffixes_o in other.random_text.items():
            suffixes = self.__random_text.setdefault(prefix, [])
            for suffix in suffixes_o:
                suffixes.append(suffix)

    def __reset(self):
        """Called when initializing or resetting this object."""
        self.__length = 0
        self.__strip = False
        self.__filenames = set() # files read
        self.__random_text = {}  # dict(tuple(str), str)
                                 #      tuple(str): prefix, more than one word
                                 #      str       : suffix, just one word

    def __strip_chars(self):
        """Make a small string of chars that are to be stripped from a word.

        return: str, string of chars to be stripped from a word
        """
        chars = string.whitespace
        if self.__strip:
            chars += string.punctuation

        return chars

    def __add_word(self, prefix, word):
        """Create a new prefix or add to the existing one.

        prefix: tuple(str), the current prefix in use
        word  : str, the word to be added to the prefix and possibly suffix

        return: str, the updated prefix
        """
        # as long as the prefix does not have the required length keep adding words to it
        if len(prefix) < self.__length:
            prefix += (word, )
        else:
            # the prefix has the required length so add the word as a suffix
            suffixes = self.__random_text.setdefault(prefix, [])
            suffixes.append(word)
            prefix = prefix[1:] + (word, ) # create new prefix by adding the new word

        return prefix

_DESC = """\
Print random samples of text created by reading one or more text files. Every sample has a prefix
and suffix. The prefix is a concatenation of words read in sequence from a text file. The suffix is
the word immediately following the prefix in the text file.
"""

_EPILOG = f'usage example: python {sys.argv[0]} -s 10 -l 4 -p 1 -f emma.txt sample.txt sample2.txt'

def main():
    """Main entry point.

    return: int, success or failure
    """
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = _DESC, epilog = _EPILOG)
    parser.add_argument('-s', '--samples', type = int, required = True,
                        help = "the number of random samples to print")
    parser.add_argument('-l', '--length', type = int, required = True,
                        help = "the number of words that make up the prefix")
    parser.add_argument('-p', '--strip', type = int, choices = [0, 1], default = 1,
                        help = "strip words in samples of punctuation, "
                               "valid values: 1 (strip), 0 (don't strip) (default: 1)")
    parser.add_argument('-f', '--files', nargs='+', required = True,
                        help = "the text file(s) to read")
    args  = parser.parse_args()

    rand_text = RandomText()

    # check integer command line parameters
    if args.samples > 0:
        if rand_text.create(args.length, *args.files, strip = bool(args.strip), reset = True):
            print(rand_text(args.samples))
    else:
        rand_text(args.samples)

    return 0

def _param_error(length, strip, reset, /, *filenames):
    """Validate parameters.

    length   : int > 0
    strip    : bool
    reset    : bool
    filenames: sequence of str

    return: bool, True if a parameter is in error
    """
    if not isinstance(length, int):
        print("error: 'length' has to be of type 'int'")
        return True
    if length < 1:
        print("error: 'length' has to be > 0")
        return True
    if not isinstance(strip, bool) or not isinstance(reset, bool):
        print("error: 'strip' and 'reset' have to be of type 'bool'")
        return True
    if not isinstance(filenames, collections.abc.Sequence):
        print("error: 'filenames' has to be a sequence")
        return True
    for filename in filenames:
        if not isinstance(filename, str):
            print(f"error: '{filename}' has to be of type 'str'")
            return True

    return False

if __name__ == '__main__':
    sys.exit(main())
