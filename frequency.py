"""This program takes as input a string and it returns a list of
frequencies per character in the string. The list is sorted in
descending order of frequency. The list consists of tuples in the form
(frequency, characters). 'frequency' is the number that each character
occurs and 'characters' is a string of chars or a list of chars that
have the same frequency. Thus, more than one character may have have the
same frequency. Also, all chars in 'characters' are sorted in ascending
order.
"""
import sys
import argparse

import utility

# Inherit class that provides functionality for adding two instances of
# the derived class and reference counting as well.
class CharFreq(utility.AdderWithRefCount):
    """Calculate the frequency of each character in a string."""
    def __init__(self):
        """ctor"""
        super().__init__()
        self.__reset()

    def calc(self, string, str_rep = True, reset = False):
        """Calculate the frequency of each character in a string.

        string : str, the string for which to calculate the frequency of
                 characters
        str_rep: bool, if True then all characters that have the same
                 frequency are concatenated in a string in ascending
                 order else they are elements of a list (also in
                 ascending order).
        reset  : bool, if True clear existing string

        return: bool, True if no errors
        """
        _param_error(string, str_rep, reset)

        if self.__string == string:
            print("error: can't add the same string")
            return False

        self.__str_rep = str_rep
        if reset:
            self.__string = string
        else:
            self.__string += string

        for char in self.__string:
            freq = self.__chars.get(char, 0) # get freq for given char
            if freq:
                # if the character exists already, delete it
                self.__del_char(freq, char)

            # add new char or increment frequency of existing one
            self.__add_char(freq+1, char)

        # convert characters from a list to a string
        if self.__str_rep:
            for freq, chars in self.__freqs.items():
                self.__freqs[freq] = ''.join(chars)

        return True

    @property
    def freqs(self):
        """Return the frequencies of characters.

        return: list of tuple(int, str) or
                list of tuple(int, list of str)

                int        : frequency of a character in the string
                str        : chars that have the same frequency
                list of str: --------------ditto---------------

                The list of tuple is sorted in descending order of freq.
        """
        # convert the dictionary to a list and sort the list in reverse
        # order so that higher frequencies appear first
        return sorted(self.__freqs.items(), reverse = True)

    @property
    def string(self):
        """return: str"""
        return self.__string

    @property
    def str_rep(self):
        """return: bool, True if char freqs represented as strings"""
        return self.__str_rep

    def clear(self):
        """Clear the object."""
        self.__reset()
        super().clear()

    def __str__(self):
        """Called when printing a char freq object.

        return: str, a formatted string of character frequencies
        """
        return self.__string + " -> " + str(self.freqs)

    def __repr__(self):
        """Called when calling repr(obj) on a char freq object.

        return: str, repr to allow obj equal to this one to be created
        """
        return f"{self.__class__.__module__}.{self.__class__.__name__}" \
               f"({self.__string, self.__str_rep})"

    def __call__(self):
        """See doc of returned method."""
        return self.freqs

    def __bool__(self):
        """Called when a char freq obj is used as a bool in expression.

        return: bool, see __len__()
        """
        return bool(self.__len__())

    def __len__(self):
        """Called when calling len(obj) on a char freq object.

        return: int, the number of char freq for a given string
        """
        return len(self.freqs)

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: CharFreq, the char freq object to compare with

        return: bool or NotImplemented
                bool          :True if two char freq objects are equal
                NotImplemented: if there's a parameter error
        """
        if not isinstance(other, CharFreq):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        return self.__str_rep == other.str_rep and self.__string == other.string

    def __iter__(self):
        """Called whenever an iterator of a char freq obj is requested.

        return: iterator object, a char freq object iterator
        """
        return iter(self.freqs)

    def __getitem__(self, key):
        """Called when implementing evaluation of self[key].

        key: int or slice

        return: tuple, see return value of method in class

        exceptions: TypeError, if key is of an inappropriate type
                    IndexError, if key is of a value outside the set of
                    indexes for the sequence
        """
        return self.freqs[key]

    def _is_add(self, other):
        """Check if two char freq objects can be added.

        other: CharFreq, the char freq object to compare this one to

        return: bool, True if both char freq objects can be added
        """
        return self.__str_rep == other.str_rep and self.__string != other.string

    def _add(self, other):
        """Add a char freq object to this one.

        other: CharFreq
        """
        self.calc(other.string)

    def __reset(self):
        """Called when initializing or resetting this object."""
        self.__string = ""
        self.__str_rep = True
        self.__freqs = {} # key is freq, val is all chars of that freq
        self.__chars = {} # key is char, val is the freq for that char

    def __add_char(self, freq, char):
        """Add a char for the given freq to the dict of frequencies.

        freq: int, the frequency for character 'char'
        char: str, a single char to be added to the dict of frequencies
        """
        # get chars for given freq or add the freq if it doesn't exist
        chars = self.__freqs.setdefault(freq, [])

        # find the position to insert the char
        pos = utility.in_bisection(chars, char, True)

        chars.insert(pos, char)   # insert the char at the pos found
        self.__chars[char] = freq # update the freq for the given char

    def __del_char(self, freq, char):
        """Del character for given freq in the dict of frequencies.

        freq: int, the frequency for character 'char'
        char: str, a single char to be deleted from the frequency dict
        """
        chars = self.__freqs[freq] # get the chars for the given freq
        pos = utility.in_bisection(chars, char, True) # find char pos
        chars.pop(pos) # del the char
        if not chars: # del frequency item if no char has that frequency
            del self.__freqs[freq]

def main():
    """Main entry point.

    return: int, success or failure
    """
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = "Print the frequency of characters in a string "
                                                   "entered by the user.",
                                     epilog = 'usage example: '
                                              f'python {sys.argv[0]} "abra cadabra"')
    parser.add_argument('string', help = "the string entered by the user")
    args  = parser.parse_args()

    print(args.string, "->", frequency(args.string))

    return 0

def frequency(string, str_rep = True, reset = False):
    """Wrapper for class that calculates the freq of each char in str.

    params: see corresponding method in class
    return: ditto
    """
    char_freq = CharFreq()

    char_freq.calc(string, str_rep, reset)

    return char_freq()

def _param_error(string, str_rep, reset):
    """Validate parameters.

    string : str, string for which to calculate frequency for each char
    str_rep: bool, if True convert a list of chars to a string
    reset  : bool, if True clear existing string

    exceptions: ValueError

    return: bool, False if no error is found, True othewise
    """
    if not isinstance(string, str):
        raise ValueError('error: "string" must be of type "str"')
    if not isinstance(str_rep, bool):
        raise ValueError('error: "str_rep" must be of type "bool"')
    if not isinstance(reset, bool):
        raise ValueError('error: "reset" must be of type "bool"')

if __name__ == '__main__':
    sys.exit(main())
