"""Contains common utilities."""

import abc
import collections.abc
import os
import weakref
from copy import copy, deepcopy

class AdderWithRefCount(abc.ABC):
    """Base class for classes that need addition and reference counting of added objects.

    If the derived class overloads the clear() method, the overload must call the base only if
    reference counting has been enabled.
    """
    def __init__(self, count = True):
        """Initialize attributes.

        counter : bool, True if reference counting is enabled
        """
        if not isinstance(count, bool):
            raise TypeError("error: ctor param 'counter' has to be of type 'bool'")

        # references to objects that were added to this object
        self.__froms = [] if count else None

        # references to objects that this object was added to
        self.__tos = [] if count else None

    @abc.abstractmethod
    def _op_add(self, other):
        """Add an object to this one.

        other: subclass of this class
        """

    @abc.abstractmethod
    def __eq__(self, other):
        """Overloaded '==' operator.

        other: subclass of this class, the object to compare with

        return: bool or NotImplemented
                bool          : True if the two objects are equal
                NotImplemented: if there's a parameter error
        """

    @abc.abstractmethod
    def __bool__(self):
        """Called when an object is used as a boolean in an expression.

        return: bool, True if object evaluates as True
        """

    def is_add(self, other):
        """Check if two objects can be added.

        other: subclass of this class

        return: bool, True if self + other is valid
        """
        return self.__param_error(other, False)

    def add(self, *others):
        """Add objects to this one.

        other: tuple of subclass of this class
        """
        for other in others:
            self.__op_add(other)

    def clear(self):
        """Clear all references of other objects to self and of self to other objects."""
        if self.__froms or self.__tos:
            for wref in self.__froms:
                wref().tos.remove(weakref.ref(self))
            for wref in self.__tos:
                wref().froms.remove(weakref.ref(self))
            self.__froms.clear()
            self.__tos.clear()

    def __add__(self, other):
        """Overloaded '+' operator.

        other: subclass of this class, the object to add from

        return: see __op_add()
        """
        return self.__op_add(other, True)

    def __radd__(self, other):
        """Overloaded '+' operator.

        Called when '__add__(self, other)' fails because 'self' is not a subclass of this class.
        This call results to '__add__(other, self)' where 'other' is a subclass of this class.
        This method is added to have better error messaging.

        other: subclass of this class

        return: see __add__()
        """
        return self.__add__(other)

    def __iadd__(self, other):
        """Overloaded '+=' operator.

        other: subclass of this class, the object to add from

        return: see __op_add()
        """
        return self.__op_add(other)

    def __deepcopy__(self, memo):
        """Overloaded method of the standard library copy.deepcopy().

        When an object with references is copied custom behavior is required to update the
        references. Also, if references are not shallow copied then the program never ends and
        continues to consume more and more memory. On my system 70% of 32GB!

        The code was taken from

        https://stackoverflow.com/questions/1500718/how-to-override-the-copy-deepcopy-operations-for-a-python-object/24621200#24621200

        based on Anthony Hatchkins solution.

        memo: dict(int, any)
                   int: id(obj)
                   any: type(obj)

        return: subclass of this class, a newly constructed object
        """
        obj = memo.get(id(self), None) # added these 3 lines based on the comments in the article
        if obj:                        # to avoid possible infinite recursion (Antonín Hoskovec)
            return obj

        cls = self.__class__
        obj = cls.__new__(cls)
        memo[id(self)] = obj
        for attr, value in self.__dict__.items():
            # if shallow copy is not used we have the catastrophy described in the doc string
            if '__froms' in attr:
                setattr(obj, attr, copy(self.__froms))
            elif '__tos' in attr:
                setattr(obj, attr, copy(self.__tos))
            else: # all other attributes are deepcopied
                setattr(obj, attr, deepcopy(value, memo))

        # update references in existing and new object
        if self.__froms is not None:
            if self:
                obj.froms.append(weakref.ref(self))
            for wref in obj.froms:
                wref().tos.append(weakref.ref(obj))
            for wref in obj.tos:
                wref().froms.append(weakref.ref(obj))

        return obj

    def __del__(self):
        """Clear all references of other objects to self and of self to other objects.
        
        This is useful in case an object goes out of scope and is garbage collected.
        """
        self.clear()

    def _is_add(self, other):
        """Check if other can be added to this object.

        Default implementation in case a derived class does not need this method.

        other: subclass of this class

        return: bool, True
        """
        return True

    @property
    def froms(self):
        """Return a list of references to objects that were added to this object.

        return: list, list elements are a subclass of this class
        """
        return self.__froms

    @property
    def tos(self):
        """Return a list of references to objects that this object was added to.

        return: list, list elements are a subclass of this class
        """
        return self.__tos

    def __op_add(self, other, op_plus = False):
        """Add one object to another.

        other  : subclass of this class, the object to add from
        op_plus: bool, True if operator '+' is used instead of '+='

        return: subclass of this class,
                    or
                NotImplemented, if param error and operator '+' is used
        """
        if self.__param_error(other):
            if op_plus: # if param error and operator is '+'
                return NotImplemented

            return self # if param error and operator is '+='

        lhs = deepcopy(self) if op_plus else self

        if other:
            lhs._op_add(other)

            # the only way to check that ref counting is enabled is to compare to 'not None'
            if lhs.froms is not None:
                # add references to objects that have been added from and to
                lhs.froms.append(weakref.ref(other))
                other.tos.append(weakref.ref(lhs))
                lhs.froms.extend(other.froms)
                for wref in other.froms:
                    wref().tos.append(weakref.ref(lhs))

        return lhs

    def __param_error(self, other, stdout = True):
        """Validate parameters.

        other : subclass of this class, the object to add from
        stdout: bool, True if errors are to be printed

        return: bool: True if param error
        """
        if other is self:
            if stdout:
                print("error: can't add object to itself")
            return stdout

        if not isinstance(other, type(self)):
            if stdout:
                print(f"error: 'other' = '{other}' must be of type "
                      f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return stdout

        if not self._is_add(other):
            if stdout:
                print(f"error: all comparisons in method "
                      f"'{self.__class__.__module__}.{self.__class__.__name__}._is_add()' "
                      "must be true in order to add these two objects")
            return stdout

        # the only way to check that ref counting is enabled is to compare to 'not None'
        if self.__froms is not None:
            if weakref.ref(other) in self.__froms:
                if stdout:
                    print("error: 'other' has already been added to 'self'")
                return stdout

            for wref in other.froms:
                if wref is weakref.ref(self):
                    if stdout:
                        print("error: 'self' has already been added to 'other'")
                    return stdout

                if wref in self.froms:
                    if stdout:
                        print("error: part of 'other' has already been added to 'self'")
                    return stdout

        return not stdout

def get_filenames(filenames, old_filenames = None ):
    """Create a valid set of filenames based on an older set.

    filenames    : sequence
    old_filenames: set of str or None

    return: set(str): valid filenames
    """
    # keep unique filenames only and get their absolute path
    filenames = set(os.path.abspath(filename) for filename in filenames)

    for filename in filenames.copy(): # remove filenames that don't exist
        if not os.path.exists(filename):
            filenames.remove(filename)
            print(f"error: {filename!r} does not exist\n")

    filenames -= old_filenames if old_filenames else set() # remove old filenames

    return filenames

def in_bisect(sorted_seq, val, pos = False, begin = -1, end = -1):
    """Search the sorted sequence to find a value.

    The sequence must be sorted ascendingly. Optionally, a begin and end index may be specified if
    searching in a subsequence is desired. The default values of begin and end correspond to the
    entire sequence.

    sorted_seq: str, list, range or tuple
    val       : The value to search for. The type of val must be a type that is comparable with the
                type of the elements of the sequence.
    pos       : bool, if True return position even if 'val' is not found
    begin     : int, <= end and > -2, the begin index, defaults to -1 which is the beginning of the
                sequence
    end       : int, >= begin and > -2, the end index, defaults to -1 which is the end of the
                sequence

    return: int or
            None if 'pos == False' and no index is found
    """
    if _param_error_bisect(sorted_seq, pos, begin, end):
        if pos:
            return -1
        return None

    if begin == end == -1: # search the entire sequence
        begin = 0
        end = len(sorted_seq) - 1

    while begin <= end:
        middle = (begin + end) // 2
        if sorted_seq[middle] == val:
            return middle
        if sorted_seq[middle] < val:
            begin = middle + 1
        else:
            end = middle - 1

    if pos:
        return begin
    return None

_BASE = 10

def is_num_palindrome(num, begin = 0, end = 0):
    """Check if a number is a palindrome.

    If both begin and end are zero all digits of the number are checked.

    num  : int
    begin: int, the digit to begin from
    end  : int, the last digit to use

    return: bool, True if num is a palidrome
    """
    # extract the number and the number of digits based on begin and end positions
    num, digits = extract(num, begin, end)

    # to find if a number is a palindrome check every pair of digits in the number as follows:
    # 1234321 -> 1234321 -> 1234321 -> 1234321 -> it is a palindrome
    # ^     ^     ^   ^       ^ ^         ^
    # so the max number of pairs is (digits // 2), e.g. the max number of pairs for 1234321 is
    # (7 // 2) = 3
    for pos in range( digits // 2):
        # calculate the high order digit
        high = (num // (_BASE ** (digits - (pos + 1)))) % _BASE

        # calculate the low order digit
        low = (num % (_BASE ** (pos + 1))) // (_BASE ** pos)

        if high != low:
            return False

    return True

def reverse_num(num, begin = 0, end = 0):
    """Return the reverse of a number.

    num  : int, the number to reverse
    begin: int, the digit to begin reversing from
    end  : int, the last digit to use for reversing

    return: int, the number reversed
    """
    # extract the number and the number of digits based on begin and end positions
    num, digits = extract(num, begin, end)

    # to reverse a number reverse every pair of digits in the number like this:
    # 1234567 -> 7234561 -> 7634521 -> 7654321
    # ^     ^     ^   ^       ^ ^
    #  (1,7)      (2,6)      (3,5)
    # so the max number of pairs is (digits // 2), e.g. the max number of pairs for 1234567 is
    # (7 // 2) = 3
    rev = 0
    pairs = digits // 2
    for pos in range(pairs):
        power = _BASE ** (digits - (pos + 1))

        # calculate the high order digit
        high = (num // power) % _BASE

        # calculate the low order digit
        low = (num % (_BASE ** (pos + 1))) // (_BASE ** pos)

        # Calculate the reversed number based on high and low digit. Note that the low digit has to
        # be multiplied by power to become the new high digit
        rev += (low * power) + (high * (_BASE ** pos))

    # For numbers with odd number of digits the middle digit is not part of a pair so it is not
    # extracted by the loop above. The following statements extract the middle number and add it
    # to the reversed number.
    if digits % 2:
        middle_num = num % (_BASE ** ((digits + 1) // 2))
        rev += (middle_num - (middle_num % (_BASE ** (pairs))))

    return rev

def extract(num, begin, end):
    """Extract the number from begin and end positions within the number.

    num  : int
    begin: int, the digit in num to begin the extraction from
    end  : int, the last digit in num to use for the extraction

    return: tuple(int, int),
                  int: number
                  int: number of digits
    """
    _param_error_num(num, begin, end)

    if num < 0:
        num = abs(num)

    # count the number of digits
    digits = 0
    tmp = num
    while tmp > _BASE:
        tmp //= _BASE
        digits += 1
    digits += 1

    if begin:
        if begin > digits: # this is a special case where num = 0 and digits = 1
            end = begin
        elif not end: # if end is unspecified set it to maximum
            end = digits
        digits = end - begin + 1
        num = num // (_BASE ** (begin - 1))
        num = num % (_BASE ** digits)

    return num, digits

def cmpfiles(file1, file2):
    """Compare two files based on content. Use Windows 'fc' cmd.

    file1: str, a filename
    file2: str, a filename

    return: bool, False if files are the same
    """
    cmd = f"fc /U {file1} {file2}" # command on windows to compare two text files

    pipe = os.popen(cmd) # open pipe and initialize with cmd
    stat = pipe.close()  # get status of cmd, i.e. success or failure

    return bool(stat)

def md5(filename):
    """Create md5 for a file.

    filename: str

    return: str, md5 for the file
    """
    md5_val = ''

    # command on Windows to produce md5 value for a file
    cmd = "certutil -hashfile " + filename + " MD5"
    pipe = os.popen(cmd)                     # open pipe and initialize with cmd
    res = pipe.read()                        # read results of cmd
    stat = pipe.close()                      # get status of cmd, i.e. success or failure
    if not stat:                             # if not failure
        begin = res.find('\n')               # find beginning of md5 value
        if begin != -1:                      # -1 means find failed
            end = res.find('\n', begin+1)    # find end of md5 value
            if end != -1:                    # -1 means find failed
                md5_val = res[begin+1:end]   # extract the md5 value

    return md5_val

def _param_error_bisect(seq, pos, begin, end):
    """Validate parameters.

    seq  : a sequence
    pos  : bool
    begin: int, > -2 and <= end
    end  : int, > -2 and >= begin

    return: True if params error is found
    """
    if not isinstance(seq, collections.abc.Sequence):
        print("error: 'seq' has to be a sequence")
        return True
    if not seq:
        return True
    if not isinstance(pos, bool):
        print("error: 'pos' must be of 'bool' type")
        return True
    if not isinstance(begin, int) or not isinstance(end, int):
        print("error: 'begin' and 'end' must be of 'int' type")
        return True
    if begin > end:
        print("error: (begin > end) is not allowed")
        return True
    if begin < -1 or end < -1:
        print("error: (begin < -1 or end < -1) is not allowed")
        return True

    return False

def _param_error_num(num, begin, end):
    """Validate parameters.

    num  : int
    begin: int, the digit in num to begin from
    end  : int, the last digit in num to use

    exceptions: TypeError , if any parameter is not of type int
                ValueError, if begin and/or end have wrong integer values (see below)

    return: bool, False if no error
    """
    if not isinstance(num, int) or not isinstance(begin, int) or not isinstance(end, int):
        raise TypeError("error: all parameters have to be of type 'int'")
    if begin < 0 or end < 0 or (begin > end and end):
        raise ValueError("error: (begin < 0 or end < 0 or begin > end) is not allowed")
    if not begin and end:
        raise ValueError("error: when specifying a range, 'begin' cannot be zero -> "
                        f"[{begin}, {end}]")
