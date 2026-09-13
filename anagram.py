"""This program prints words that are anagrams based on text files 
input by the user. The anagrams are sorted descendingly by length.

Depending on the user input the anagrams printed are one of three kinds:
- PLAIN     : Plain anagrams
- BINGO     : Anagrams that have the char length required by the game of
              bingo.
- METATHESIS: Anagrams of words that have metathesis, i.e. one word can
              be transformed into the other by swapping two letters, 
              e.g. 'converse' and 'conserve'. Thus, these type of 
              anagrams are always pairs.
"""
import sys
import fileinput
import itertools
import copy
import argparse

import utility

PLAIN = 1
BINGO = PLAIN * 2
METATHESIS = BINGO * 2
_BINGO_LEN = 8
_ANAGRAMS = (PLAIN, BINGO, METATHESIS)

# Inherit class that provides functionality for adding two instances of
# the derived class and reference counting as well.
class Anagram(utility.AdderWithRefCount):
    """Implement functionality to print anagrams from text files."""

    def __init__(self):
        """ctor"""

        # last parameter indicates that object references are not taken
        # into account when adding two instances of this class
        super().__init__(False)
        self.__reset() # init attributes

    def produce(self, *filenames, flag = PLAIN, reset = False):
        """Produce anagrams from list of text files passed in as param.

        filenames: tuple of str, should be valid filenames
        flag     : int, flag that takes the values shown below

                   - PLAIN     : Plain anagrams.
                   - BINGO     : Anagrams that have the char length 
                                 required by the game of bingo.
                   - METATHESIS: Create anagrams of words that have 
                                 metathesis, i.e. one word can be
                                 transformed into the other by swapping
                                 two letters, e.g. 'converse' and 
                                 'conserve'. Thus, these types of 
                                 anagrams are always pairs.

        reset    : bool, True if existing anagrams are to be deleted

        return: bool, True if successful
        """
        _param_error(flag, reset, *filenames)

        if reset:
            self.__reset() # init data structures
            self.__flag = flag

        if not self.agrams:
            self.__flag = flag

        if self.__flag != flag:
            print(f"error: you can't add an anagram of type {flag!r} "
                  f"to a type {self.__flag!r}")
            return False

        result = True

        # get filenames based on old ones
        filenames = utility.get_filenames(filenames, self.filenames)
        if filenames:
            try:
                with fileinput.input(filenames, encoding="utf-8") as file:
                    # store the contents of the text files in dictionary
                    for line in file:
                        self.__insert(line)
                    self.filenames.add(fileinput.filename())
            except OSError as exc:
                print(exc)
                result = False
            finally:
                self.__hash() # hash anagrams

        return result

    @property
    def anagrams(self):
        """Sort the anagrams if necessary and return them.

        return: tuple(list, dict)
                list: list of sorted anagrams, anagrams: set of str
                dict: pairs of (str, set of str)
                                str       : a word sorted ascendingly
                                set of str: set of anagrams for the word
        """
        if self.__update:
            self.__sorted_anagrams = list(self.agrams.values())

            # sort so that words with the most anagrams appear first
            self.__sorted_anagrams.sort(key = len, reverse = True)
            self.__update = False

        return self.__sorted_anagrams, self.agrams

    @property
    def update(self):
        """return: bool, True if new anagrams have been added"""
        return self.__update

    @property
    def flag(self):
        """return: int, the anagram type"""
        return self.__flag

    def clear(self):
        """Clear all attributes."""
        self.__reset()

    def __str__(self):
        """Called when printing an anagram obj.

        return: str, a formatted string containing all anagrams
        """
        return anagram_str(self.anagrams[0])

    def __repr__(self):
        """Called when calling repr(obj) of an anagram obj.

        return: str, the repr of an anagram obj
        """
        return f"<type: {self.__class__.__module__}.{self.__class__.__name__}"\
               f", id: {id(self)}>"

    def __call__(self):
        """See doc of returned method."""
        return self.anagrams

    def __bool__(self):
        """Called when an anagram obj is used in a boolean expression.

        return: bool, see __len__()
        """
        return bool(self.__len__())

    def __len__(self):
        """Called when calling len(obj) of an anagram obj.

        return: int, the length of the anagram obj
        """
        return len(self.anagrams[0])

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: Anagram, the anagrams to compare with

        return: bool or NotImplemented
                bool          : True if the two anagram objs are equal
                NotImplemented: if there's a parameter error
        """
        if not isinstance(other, Anagram):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        return self.__flag == other.flag and self.filenames == other.filenames

    def __iter__(self):
        """Called whenever an iterator of an anagram obj is requested.

        return: iterator obj, an anagram obj iterator
        """
        return iter(self.anagrams[0])

    def __getitem__(self, key):
        """Called when implementing evaluation of self[key].

        key: int or slice

        return: list of str, i.e. the anagrams for key

        exceptions: TypeError, if key is of an inappropriate type
                    IndexError, if key is of a value outside the set of
                                indexes for the sequence
        """
        return self.anagrams[0][key]

    def _is_add(self, other):
        """Check if two anagram objs can be added.

        other: Anagram, the anagram obj to compare this one to

        return: bool, True if both anagram objs can be added
        """
        for filename in self.filenames:
            if filename in other.filenames:
                return False

        return self.__flag == other.flag

    def _add(self, other):
        """Add an anagram obj to this one.

        other: Anagram
        """
        self.filenames |= other.filenames
        if not self.agrams: # if self is empty do a deepcopy of anagrams
            self.agrams = copy.deepcopy(other.agrams)
            self.__update = True
            if self.__flag == METATHESIS:
                self.__pair = True
            return

        # add dictionary of other to dictionary of self
        for sorted_word, anagrams_o in other.agrams.items():
            anagrams = self.agrams.setdefault(sorted_word, set())
            for anagram in anagrams_o:
                anagrams.add(anagram)

        if self.__flag != PLAIN:
            self.__hash()
        else:
            self.__update = True

    def __reset(self):
        """Initialize attributes."""
        self.__sorted_anagrams = [] # sorted list of anagrams
        self.agrams = {}            # key: str, word sorted ascendingly
                                    # value is set of str, a set of
                                    # anagrams for the word (key)
        self.filenames = set()      # a set of files that have been read
        self.__flag = PLAIN         # flag indicating type of anagram
        self.__update = False       # anagrams been updated?
        self.__pair = False         # metathesis anagrams been added?

    def __insert(self, line):
        """Insert words read from string (line) to an anagram dict.

        The pair has a key of a sorted word and a value of a set of
        words of equal length to the key and exactly the same characters
        as the key.

        line: str, a line of words
        """
        for word in line.split():
            word = word.strip()
            if word and (self.__flag != BINGO or len(word) == _BINGO_LEN):
                sorted_word = ''.join(sorted(word))
                words = self.agrams.setdefault(sorted_word, set())
                words.add(word)

    def __hash(self):
        """Hash anagrams based on their flag.
        
        Plain anagrams need not be hashed further except for setting the
        update flag which is set further below. Metathesis anagrams need
        to be hashed as their pairs need to be unpacked for new pairs to
        be created correctly. Bingo anagrams need to be hashed as well
        to keep only the ones with the largest number of anagrams.
        """
        length = 1
        pair = False
        for sorted_word, anagrams in self.agrams.copy().items():
            # at least two anagrams must exist per sorted word
            if len(anagrams) > 1:
                if self.__flag == METATHESIS:
                    # return only pairs that have metathesis
                    anagrams = self.__metathesis(anagrams)
                    if anagrams:
                        self.agrams[sorted_word] = anagrams
                        # at least one pair of metathesis anagrams added
                        pair = True
                        self.__update = True
                    else:
                        del self.agrams[sorted_word]
                elif self.__flag == BINGO:
                    # save anagrams with the largest number of elements
                    if len(anagrams) > length:
                        self.agrams.clear()
                        length = len(anagrams)
                        self.agrams[sorted_word] = anagrams
                        self.__update = True

                    # save all anagrams with the largest num of elements
                    elif len(anagrams) == length:
                        self.agrams[sorted_word] = anagrams
                        self.__update = True
                else:
                    self.__update = True
            else:
                # bingo anagrams are cleared above so pop() is used for
                # safe deletion to avoid raising KeyError
                self.agrams.pop(sorted_word, None)

        if pair:
            self.__pair = True

    def __metathesis(self, anagrams):
        """Iterate over anagrams and save pairs that have metathesis.

        anagrams: set of str, words of equal length and same chars

        return: set of tuple(str, str), anagram pairs with metathesis
        """
        metathesis = set()

        # in case old metathesis anagrams exist, remove them, as they
        # are pairs, and add them again as separate elements to process
        # them effectively
        if self.__pair:
            for anagram in anagrams.copy():
                if isinstance(anagram, tuple):
                    anagrams.remove(anagram)
                    for agram in anagram:
                        anagrams.add(agram)

        # produce pairs of anagrams, e.g. from {a,b,c,d} -> ab, ac, ad,
        # bc, bd, cd and store them if there is metathesis
        for anagram, anagram2 in itertools.combinations(anagrams, 2):
            _pair(anagram, anagram2, metathesis)

        return metathesis

def anagram_str(anagrams):
    """Create a formatted string containing all anagrams.

    anagrams: list of set of str

    return: str, a formatted string containing all anagrams
    """
    agram_str = ''
    for anagram_set in anagrams:
        agram_str += (str(len(anagram_set)) + ' ' + str(anagram_set) + '\n')

    return agram_str

_DESC_COMMON = "Anagram example: the sorted literal 'acer' produces the "\
               "following words: 'acre', 'care', 'race'."

_DESC = f"""\
Read text files specified by the user and display anagrams from the words in 
the text files.
{_DESC_COMMON}
"""

_HELP_ANAGRAM_TYPE = """\
anagram type: 1 | 2 | 4 (1: plain, 2: bingo, 4: metathesis),  (default: 1)
    bingo anagrams have exactly 8 letters
        (only bingo anagrams with most words are stored)
    metathesis anagrams example: 'converse' and 'conserve'
        (metathesis anagrams only come in pairs)
"""

_HELP_INPUT = 'INPUT [INPUT ...]: the text files to read to create the '\
              'anagrams DB file'

def main():
    """Main entry point.

    return: int, success or failure
    """
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = _DESC,
                                     epilog = 'usage example: '
                                              'python '
                                              f'{sys.argv[0]} -t 2 -i words')
    parser.add_argument('-t', '--type', type = int, choices = [1, 2, 4],
                        default = 1, help = _HELP_ANAGRAM_TYPE)
    parser.add_argument('-i', '--input', nargs='+', required = True,
                        help = _HELP_INPUT)
    args  = parser.parse_args()

    anagram = Anagram()
    if anagram.produce(*args.input, flag = args.type):
        print(anagram)

    return 0

def _param_error(flag, reset, /, *filenames):
    """Check parameters.

    flag     : int, the type of anagram
    reset    : bool, True if existing anagrams are not to be deleted
    filenames: tuple of str

    exceptions: TypeError, ValueError

    return: bool, False if no params error
    """
    if not isinstance(flag, int):
        raise TypeError("error: 'flag' has to be of type 'int'")
    if not isinstance(reset, bool):
        raise TypeError("error: 'reset' has to be of type 'bool'")
    for filename in filenames:
        if not isinstance(filename, str):
            raise TypeError(f"error: '{filename}' is not a valid filename")
    if flag not in _ANAGRAMS:
        raise ValueError(f"error: 'flag' has to be one of {_ANAGRAMS}")

def _pair(anagram, anagram2, metathesis):
    """Pair two anagrams if they have metathesis.

    The two anagrams are of equal length.

    anagram   : str or tuple
    anagram2  : str or tuple
    metathesis: set of tuple(str, str)
                holds the pairs of anagrams that have metathesis
    """
    j = 0
    found = False
    for i, char in enumerate(anagram2):
        if char != anagram[i]:
            j += 1
            if j == 1:
                pos1 = i # save pos of first pair of chars that differ
            else:
                found = (j == 2 and anagram[pos1] == anagram2[i] and
                         anagram[i] == anagram2[pos1])
                if not found:
                    break
    if found:
        metathesis.add((anagram, anagram2))

if __name__ == '__main__':
    sys.exit(main())
