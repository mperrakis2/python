"""This program creates a sorted list of frequencies of words read from one or more files. The list
is sorted in descending order, i.e the highest frequency is first. Every element of the list also
contains a rank for the word. The highest frequency has the lowest rank. Also, every element in the
list contains a pair of logarithmic values. The first value is the logarithm of the frequency and
the second the logarithm of the rank.
"""
import string
import math
import sys
import copy
import fileinput
import argparse

import utility

# Inherit class that provides functionality for adding two instances of the derived class and
# reference counting as well.
class WordFreq(utility.AdderWithRefCount):
    """Provides functionality to read text files and create data structures of the words read based
    on their frequency.
    """
    def __init__(self):
        """ctor"""
        super().__init__()
        self.__reset()

    def insert(self, *filenames, reset = False):
        """Populate a dictionary of word frequencies based on the files read.

        filenames: tuple of str
        reset    : bool, True if all existing word freqs are to be cleared

        return: bool, True if successful
        """
        _param_error(reset, *filenames)

        if reset:
            self.__reset()

        # get filenames based on old ones
        filenames = utility.get_filenames(filenames, self.__filenames)
        if filenames:
            try:
                # read the contents of the text files and create a dictionary of frequencies of
                # words
                with fileinput.input(filenames, encoding="utf-8") as file:
                    for line in file:
                        self.__increment(line)
                    self.__filenames.add(fileinput.filename())
            except OSError as exc:
                print(exc)
                return False

        return True

    @property
    def freqs(self):
        """Return a list of frequencies of words sorted in descending order.

        return: list(tuple(tuple(str, int, int), tuple(float, float)))

                                (str, int, int): word, frequency, rank
                                (float, float) : log10(frequency), log10(rank)
        """
        self.__sort()

        return self.__sorted_freqs

    @property
    def freqs_internal(self):
        """Return internal representation of word frequencies.

        return: dict(str, int)
                     str: word
                     int: frequency
        """
        return self.__freqs

    @property
    def filenames(self):
        """return: set of str, the files read so far"""
        return self.__filenames

    def clear(self):
        """Clear all word frequencies."""
        self.__reset()
        super().clear()

    def __str__(self):
        """Called when printing a word freq object.

        return: str, the frequencies of the words in descending order
        """
        sorted_freqs = ""
        for sorted_freq in self.freqs:
            sorted_freqs += (str(sorted_freq) + '\n')

        return sorted_freqs

    def __repr__(self):
        """Called when calling the representation (repr(word_freq_obj)) of a word freq object.

        return: str, the representation which allows an object equal to this one to be created
        """
        word_freq = f"word_freq = {self.__class__.__module__}.{self.__class__.__name__}()"
        if self.__filenames:
            word_freq += "\nword_freq.add(True, "
            for filename in self.__filenames:
                word_freq += f"{filename}, "
            word_freq += ")"

        return word_freq

    def __call__(self):
        """See doc of returned property."""
        return self.freqs

    def __bool__(self):
        """Called when a word freq object is used as a boolean in an expression.

        return: bool, see __len__()
        """
        return bool(self.__len__())

    def __len__(self):
        """Called when len() is called on a word freq object.

        return: int, the length of the word frequencies list
        """
        return len(self.freqs)

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: WordFreq, the word freq object to compare with

        return: bool or NotImplemented
                bool          : True if word freq objects are equal
                NotImplemented: if there's a parameter error
        """
        if not isinstance(other, WordFreq):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        return self.__filenames == other.filenames

    def __iter__(self):
        """Implemented to allow iterating over the word frequencies list.

        return: iterator object
        """
        return iter(self.freqs)

    def __reversed__(self):
        """Implemented to allow iterating in reverse order over the word frequencies list.

        return: iterator object
        """
        return reversed(self.freqs)

    def _is_add(self, other):
        """Check if two word freq objects can be added.

        other: WordFreq, the word freq object to compare this one to

        return: bool, True if both word freq objects can be added
        """
        return self.__freqs != other.freqs_internal

    def _op_add(self, other):
        """ Add a word freq object to this one.

            other: WordFreq
        """
        self.__filenames |= other.filenames

        if not self.__freqs: # if self is empty just do a deep copy of word freqs
            self.__freqs = copy.deepcopy(other.freqs_internal)
            return

        # add dictionary of other to dictionary of self
        for word, freq in other.freqs_internal.items():
            self.__freqs[word] = self.__freqs.get(word, 0) + freq

    def __reset(self):
        """Called when initializing or resetting this object."""
        # dict(str, int)
        #      str: a word read from one or more text files
        #      int: the total frequency of the word in all text files
        self.__freqs = {}
        self.__sorted_freqs = [] # pairs of (word, frequency) sorted descendingly by frequency
        self.__filenames = set() # files read

    def __increment(self, line):
        """Increment the frequencies of words.

        line : str
        """
        line = line.replace('-', ' ')
        for word in line.split():
            word = word.strip(string.punctuation + string.whitespace).lower()
            self.__freqs[word] = self.__freqs.get(word, 0) + 1

    def __sort(self):
        """Populate a list of frequencies of words sorted in descending order."""
        if self.__freqs:
            # populate a list of frequencies of words
            while self.__freqs:
                pair = self.__freqs.popitem()
                # if the word already exists, append the frequency else add the word as a new entry
                for sorted_freq in self.__sorted_freqs:
                    if sorted_freq[0][0] == pair[0]:
                        sorted_freq[0][1] += pair[1]
                        break
                else:
                    self.__sorted_freqs.append([[pair[0], pair[1], 0], [0, 0]])

            # sort the list by frequency in descending order
            self.__sorted_freqs.sort(key = lambda sorted_freq: (sorted_freq[0][1],
                                                                sorted_freq[0][0]),
                                     reverse = True)

            # iterate through the sorted list and add the rank in ascending order as well as the
            # logarithms of the frequency and rank
            prev_freq = rank_num = 0
            for i, sorted_freq in enumerate(self.__sorted_freqs):
                if sorted_freq[0][1] != prev_freq:
                    rank_num += 1
                self.__sorted_freqs[i][0][2] = rank_num
                self.__sorted_freqs[i][1][0] = math.log10(sorted_freq[0][1])
                self.__sorted_freqs[i][1][1] = math.log10(rank_num)
                prev_freq = sorted_freq[0][1]

def main():
    """Main entry point.

    return: int, success or failure
    """
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = "Print the frequency of words read from the "
                                                   "text files specified by the user.",
                                     epilog = 'usage example: '
                                              f'python {sys.argv[0]} sample.txt sample2.txt')
    parser.add_argument('files', nargs='+', metavar = 'file', help = "the file(s) to read")
    args  = parser.parse_args()

    result, word_freq = rank(*args.files)
    if result:
        for freq in word_freq(): # get the list sorted by frequency
            print(freq)

    return 0

def rank(*filenames):
    """Create an object of frequencies of words.

    The words are read from text files.

    filenames: str

    return: tuple(bool, WordFreq)
                  bool    : True if successful
                  WordFreq: an object containing the word frequencies
    """
    word_freq = WordFreq()

    # create an object of word frequencies based on the text file(s) read
    result = word_freq.insert(*filenames)

    return result, word_freq

def _param_error(reset, /, *filenames):
    """Check parameters.

    reset    : bool, True if existing word freqs are not to be deleted
    filenames: tuple of str

    exceptions: TypeError

    return: bool, False if no params error
    """
    if not isinstance(reset, bool):
        raise TypeError("error: 'reset' has to be of type 'bool'")
    for filename in filenames:
        if not isinstance(filename, str):
            raise TypeError(f"error: '{filename}' is not a valid filename")

if __name__ == '__main__':
    sys.exit(main())
