"""This program imports the anagrams module and uses it to retrive anagrams from text files. The
anagrams are then stored to disk using the shelve standard python module. As an example, one of
the stored anagrams is retrieved from the disk and displayed on screen.
"""
import sys
import shelve
import contextlib
import argparse

import anagram

_STORE = 1
_READ = _STORE * 2
_STORE_READ = _STORE | _READ
_COMMANDS = (_STORE, _READ, _STORE_READ)

# inherit from AbstractContextManager to get the default implementation of __enter__()
# which just returns self
class AnagramDB(contextlib.AbstractContextManager):
    """Store and read anagrams to and from a DB using the standard Python library shelve."""
    def __init__(self, filename, command = _READ):
        """ctor

        filename: str, the filename to use to store and read anagrams
        """
        if not isinstance(filename, str):
            raise TypeError("error: 'filename' has to be of type 'str'")
        if not isinstance(command, int):
            raise TypeError("error: 'command' has to be of type 'int'")
        if command not in _COMMANDS:
            raise ValueError(f"error: 'command' has to be one of {_COMMANDS}")

        self.__filename = filename
        self.__anagram_db = shelve.open(filename, 'c' if command == _READ else 'n')

    def read(self, key):
        """Read anagrams from the disk that match a particular key.

        key: str, a word sorted in ascending order

        return: list of str, i.e. the anagrams or None if key does not exist

        exceptions: TypeError, if key is not str
        """
        if not isinstance(key, str):
            raise TypeError("error: 'key' has to be of type 'str'")

        try:
            return self.__anagram_db[key] # return value of key if it exists
        except KeyError:
            print(f"key error: {key}")
            return None

    def store(self, agrams):
        """Store anagrams to the disk using the shelve module.

        agrams: key is str, a word sorted in ascending order
                value is list of str, i.e. the anagrams
        """
        # iterate over the dictionary and store each entry
        for sorted_word, agram_list in agrams.items():
            self.__anagram_db[sorted_word] = agram_list

    def clear(self):
        """Clear anagram DB."""
        self.__anagram_db.clear()

    def close(self):
        """Close anagram DB.""" 
        self.__anagram_db.close()

    @property
    def anagram_db(self):
        """return: shelve, instance of anagram db"""
        return self.__anagram_db

    def __str__(self):
        """Called when printing an anagram DB object.

        return: str, a formatted string containing all anagrams
        """
        return anagram.anagram_str(self.__anagram_db.values())

    def __repr__(self):
        """Called when calling the representation (repr(anagram_db_obj)) of an anagram DB object.

        return: str, the representation which allows an object equal to this one to be created
        """
        return f"{self.__class__.__module__}.{self.__class__.__name__}('{self.__filename}')"

    def __exit__(self, exc_type, exc_value, traceback):
        """Called right after the 'with' statement and before any exception is raised."""
        self.close()

    def __call__(self, key):
        """See doc of returned method."""
        return self.read(key)

    def __len__(self):
        """Called when calling the length (len(anagram_db_obj)) of an anagram DB object.

        return: int, the length of the anagram_db object
        """
        return len(self.__anagram_db)

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: AnagramDB, the anagrams db to compare with

        return: bool or NotImplemented
                bool          : True if the two anagram db objects are equal,
                NotImplemented: if there's a parameter error
        """
        if not isinstance(other, AnagramDB):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        if len(self.__anagram_db) == len(other.anagram_db):
            for word in self.__anagram_db:
                try:
                    if self.__anagram_db[word] != other.anagram_db[word]:
                        return False
                except KeyError: # key does not exist in other
                    return False
        else:
            return False

        return True

    def __iter__(self):
        """Called whenever an iterator of an anagram DB object is requested.

        return: iterator object, an anagram_db object iterator
        """
        return iter(self.__anagram_db)

    def __getitem__(self, key):
        """Called when implementing evaluation of self[key].

        key: str, a word sorted in ascending order

        return: list of str, i.e. the anagrams or None if key does not exist

        exceptions: TypeError, if key is not str
        """
        return self.read(key)

def main():
    """Main entry point.

    return: int, success or failure
    """
    args = _cmdline()

    # get command type
    if 'type' in args:
        if 'key' in args:
            command = _STORE_READ
        else:
            command = _STORE

        agram_type = args.type # get anagram type
    else:
        command = _READ

    with AnagramDB(args.db, command) as anagram_db:
        # create anagrams and store them to disk
        if command in (_STORE, _STORE_READ):
            agram = anagram.Anagram()
            if agram.create(*args.input, flag = agram_type):
                anagram_db.store(agram()[1])

        if command != _STORE: # read anagrams based on key
            print(anagram_db(args.key))

    return 0

_DESC = f"""\
Store and read anagrams to and from a DB file.
{anagram._DESC_COMMON}
"""

def _cmdline():
    """Validate command line arguments.

    return: argparse.Namespace object
    """
    # anagram db command line option
    parser_db = argparse.ArgumentParser(add_help = False)
    parser_db.add_argument('-d', '--db', required = True,
                           help = 'the full pathname of the anagrams DB file')

    # sorted literal (key) command line option
    parser_key = argparse.ArgumentParser(add_help = False)
    parser_key.add_argument('-k', '--key', required = True,
                            help = 'the sorted literal to read from the anagrams DB file')

    # main parser
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = _DESC,
                                     epilog = 'for further help type: '
                                              f'python {sys.argv[0]} <command> -h')

    # subparsers for the different commands
    subparsers = parser.add_subparsers(title = 'DB commands',
                                       description = "The following commands allow you to "
                                                     "store, read or store & read anagrams.",
                                       help = 'DESCRIPTION', required = True)

    # create the parser for the "store" command
    parser_s = subparsers.add_parser('store', aliases = ['s'], parents = [parser_db],
                                     formatter_class = argparse.RawTextHelpFormatter,
                                     help = 'read text files and store anagrams in a DB file')
    parser_s.add_argument('-t', '--type', type = int, choices = [1, 2, 4], default = 1,
                          help = anagram._HELP_ANAGRAM_TYPE)
    parser_s.add_argument('-i', '--input', nargs='+', required = True, help = anagram._HELP_INPUT)

    # create the parser for the "read" command
    subparsers.add_parser('read', aliases = ['r'], parents = [parser_db, parser_key],
                          formatter_class = argparse.RawTextHelpFormatter,
                          help = 'use a sorted literal to read all its anagrams from a DB file')

    # create the parser for the "store & read" command, set add_help = False, as help command line
    # options are provided by the parent
    subparsers.add_parser('store-read', aliases = ['sr'], add_help = False,
                          parents = [parser_s, parser_key],
                          formatter_class = argparse.RawTextHelpFormatter,
                          help = 'store first and then read (combination of the commands above)')

    return parser.parse_args()

if __name__ == '__main__':
    sys.exit(main())
