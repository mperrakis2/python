"""This program produces a set of reducible words from a set of valid words. The set of valid words
is read from a file. A valid word is reducible if by removing a letter the word that remains is
still a valid word. Continuing this process until only one letter remains all intermediate words
must be valid for the original to be reducible.
"""
import sys
import fileinput
import argparse

import utility

# Inherit class that provides functionality for adding two instances of the derived class and
# reference counting as well.
class Reducible(utility.AdderWithRefCount):
    """Provides functionality to extract reducible words from a set of valid words."""
    def __init__(self):
        """ctor"""
        super().__init__(False) # no reference counting
        self.__reset()

    def extract(self, *filenames):
        """Read a file and extract words that are reducible.

        filenames: sequence of str
        """
        filenames = utility.get_filenames(filenames, self.__filenames)
        if filenames:
            words = set()
            try:
                # read the contents of the text files
                with fileinput.input(filenames, encoding="utf-8") as file:
                    for word in file:
                        words.add(word.strip())
                    self.__filenames.add(fileinput.filename())
            except OSError as exc:
                print(exc)
            for word in words:
                self.__extract(word, words)

    @property
    def all(self):
        """Return the set of reducible words.

        return: set of str
        """
        return self.__reducibles

    @property
    def longest(self):
        """Return the longest reducible words.

        return: list of str
        """
        return self.__longest

    @property
    def filenames(self):
        """return: set of str, files read so far"""
        return self.__filenames

    def clear(self):
        """Clear all reducible data."""
        self.__reset()

    def __str__(self):
        """Called when printing a reducible object.

        return: str, the longest reducible
        """
        return str(self.__longest)

    def __repr__(self):
        """Called when calling the representation (repr(reducible_obj)) of a reducible object.

        return: str, the representation which allows an object equal to this one to be created
        """
        obj = "reducible"
        obj_repr = f"{obj} = {self.__class__.__module__}.{self.__class__.__name__}()"
        for filename in self.__filenames:
            obj_repr += f"\n{obj}.extract('{filename}')"

        return obj_repr

    def __bool__(self):
        """Called when a reducible object is used as a boolean in an expression.

        return: bool, see __len__()
        """
        return bool(self.__len__())

    def __len__(self):
        """Called when calling the length (len(reducible_obj)) of a reducible object.

        return: int, the number of longest reducible words
        """
        return len(self.__longest)

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: Reducible, the reducible object to compare with

        return: bool or NotImplemented
                bool          :True if two poker stats are equal
                NotImplemented: if there's a parameter error
        """
        if not isinstance(other, Reducible):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        return self.__filenames == other.filenames

    def __iter__(self):
        """Called whenever an iterator of a reducible object is requested.

        return: iterator object, a reducible object iterator
        """
        return iter(self.__longest)

    def __getitem__(self, key):
        """Called when self[key] is used.

        key: int or slice

        return: str, a reducible word

        exceptions: TypeError, if key is of an inappropriate type
                    IndexError, if key is of a value outside the set of indexes for the sequence
        """
        return self.__longest[key]

    def _op_add(self, other):
        """Add two objects of type Reducible.

        other: Reducible
        """
        self.__reducibles |= other.all # copy the reducibles from other

        # copy the longest reducibles from other
        for word in other.longest:
            if word not in self.__longest and len(word) >= len(self.__longest[-1]):
                self.__longest.append(word)

        # copy the files that have been read from other
        self.__filenames |= other.filenames

    def __reset(self):
        """Called when initializing or resetting this object."""
        self.__longest = []       # list of longest reducible words
        self.__reducibles = set() # reducible words
        self.__filenames = set()  # files read

    def __extract(self, word, words):
        """If 'word' is reducible, add it and all its reducibles to a set of reducible words.

        word : str
        words: set, a set of valid words

        return: bool, True if word is reducible
        """
        if word in self.__reducibles:
            return True

        if not word:
            return False

        stack = []
        found = False
        index = 0
        while not found:
            for i in range(index, len(word)):
                # create sub word
                sub_word = word[:i] + word[i+1:]

                # if the sub word is in the reducible set add the word to the stack and stop
                # processing
                if sub_word in self.__reducibles:
                    stack.append((i+1, word))
                    found = True
                    break

                # If the sub word is a word then add the word it was produced from to the stack. If
                # the sub word is empty then the original word and all its sub words are reducible.
                if sub_word in words or not sub_word:
                    stack.append((i+1, word))
                    if not sub_word:
                        found = True
                    else: # if the sub word is not empty keep searching
                        word = sub_word
                        index = 0
                    break

            # if word is not reducible
            if not found and word != sub_word:
                if stack:
                    # pop the stack to continue processing from the last index of the last word
                    index, word = stack.pop()
                else:
                    break # if there's no stack then we are done processing

        # Add reducible words from the stack to the set of reducible words. Also if the longest
        # word in the stack is longer or equal to the longest reducible word, add it to the list
        # of longest reducible words.
        self.__add(stack, found)

        return found

    def __add(self, stack, found):
        """Add a list of words that are reducible to the set of reducible words.

        Also, and add the longest reducible word, if any, to the list of longest reducible words.

        stack: list of tuple(int, str)
                             int: index within the word
                             str: word to add to reducibles
        found: bool, True if a reducible word has been found
        """
        if found:
            # sort the stack by longest reducible word
            stack.sort(key=lambda frame: len(frame[1]), reverse = True)

            # append the longest reducible word
            if not self.__longest or \
               len(stack[0][1]) >= len(self.__longest[-1]):
                # in case more than one file has been read, check that the reducible already exists
                if stack[0][1] not in self.__longest:
                    self.__longest.append(stack[0][1])

                length = len(self.__longest)-1
                # keep only the longest reducible words
                if len(self.__longest[length-1]) < len(self.__longest[length]):
                    del self.__longest[:length]

            for frame in stack:
                self.__reducibles.add(frame[1])

_DESC = """\
Produce a set of reducible words from valid words read from files. A word is reducible if by
removing a letter, the word that remains is still valid. Continuing this process until only one
letter remains all intermediate words must be valid for the original to be reducible.
"""

def main():
    """Main entry point.

    return: int, success or failure
    """
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = _DESC)
    parser.add_argument('files', nargs='+', metavar = 'file', help = "the file(s) to read")
    args  = parser.parse_args()

    reducible = Reducible()
    reducible.extract(*args.files)
    print(reducible)

    return 0

if __name__ == '__main__':
    sys.exit(main())
