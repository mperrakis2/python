"""This program takes as input a directory name and prints all contents of the directory and the
directories below it. The function os_walk() mimics the behavior of the os.walk() standard library
function.
"""
import os
import sys
import argparse

class DirWalk:
    """Implements functionality to traverse directories and store all filenames under the
    directories.
    """
    def __init__(self, dirname, topdown = True, followlinks = False, ext = ''):
        """ctor

        dirname    : str, the directory to traverse
        topdown    : bool, see documentation of python standard library os.walk()
        followlinks: bool, True if sym links that are dirs are to be traversed
        ext        : str, search only for files with this extension
        """
        _param_error(dirname, topdown, followlinks, ext) # raise exception if error

        self.__dirname = dirname
        self.__topdown = topdown
        self.__followlinks = followlinks
        self.__ext = ext
        self.__names = [] # directories and/or file names found under dirname

    def walk(self):
        """Get filenames under the directory stored in the class attribute variable.

        All directories under that variable are searched as well.
        """
        self.__names.clear()
        dirname = os.path.normpath(self.__dirname) # remove any trailing slashes
        if os.path.isfile(dirname): # if filename just print the ablolute filename path
            print(os.path.abspath(dirname))
        elif os.path.isdir(dirname): # if directory traverse directory list
            stack = []
            i = 0
            while True:
                tmp = dirname

                # Find filenames under directory 'dirname'. Also, get new directory name if one
                # exists.
                dirname, i, directory = self.__find_filenames(dirname, i)

                # if a new directory was found, append the current directory to the stack
                if directory:
                    stack.append((tmp, i))
                    i = 0
                # if no new directory was found, pop the previous directory to continue printing
                elif stack:
                    dirname, i = stack.pop()
                # no new directory and no more stack left so exit
                else:
                    break
        else:
            print(f"{dirname} is not a file or a directory")

    def os_walk(self):
        """Imitate the functionality of os.walk() of standard python library."""
        self.__names.clear()
        dirname = os.path.normpath(self.__dirname) # remove any trailing slashes

        # if directory traverse directory list
        if os.path.isdir(dirname):
            stack = []
            while True:
                # create lists of directory and file names
                dirnames, filenames = _create_lists(dirname)

                # add the lists of directory and file names to the list of names
                self.__names.append((dirname, dirnames, filenames))

                # push directories in dirnames to the stack
                self.__push_stack(stack, dirnames, dirname)

                if stack:
                    dirname = stack.pop() # get the new directory to process
                else:
                    break

    @property
    def names(self):
        """Return all filenames under the directory stored in the class attribute variable.

        return: list of str, i.e. filenames

                                or

                list of tuple(str, list of str, list of str)
                              str        : a directory name
                              list of str: all directories under the directory name
                              list of str: all filenames under the directory name
        """
        return self.__names if self.__ext or self.__topdown else reversed(self.__names)

    @property
    def dirname(self):
        """return: str, the directory name to traverse"""
        return self.__dirname

    @property
    def topdown(self):
        """return: bool"""
        return self.__topdown

    @property
    def followlinks(self):
        """return: bool, True if sym links that are dirs are to be traversed"""
        return self.__followlinks

    @property
    def ext(self):
        """return: str, search only for files with this extension"""
        return self.__ext

    def __str__(self):
        """Called when printing a dir walk object.

        return: str, a formatted string of directory and/or file names
        """
        if self.__ext:
            names = str(self.names)
        else:
            names = ''
            for dirpath, dirnames, filenames in self.names:
                names += (dirpath + ' ' + str(dirnames) + ' ' + str(filenames) + '\n')

        return names

    def __repr__(self):
        """Called when calling the representation (repr(dirwalk_obj)) of a dir walk object.

        return: str, the representation which allows a dir walk object to be identified
        """
        return f"<type: {self.__class__.__module__}.{self.__class__.__name__},"\
               f" id: {id(self)}>"

    def __call__(self):
        """See doc of returned method."""
        return self.names

    def __bool__(self):
        """Called when a dir walk object is used as a boolean in an expression.

        return: bool, True if directories and/or filenames have been found
        """
        return bool(self.__names)

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: DirWalk, the dir walk object to compare with

        return: bool or NotImplemented
                bool          : True if two dir walk objects are equal
                NotImplemented: if there's a parameter error
        """
        if not isinstance(other, DirWalk):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        return self.__dirname == other.dirname and \
               self.__topdown == other.topdown and \
               self.__followlinks == other.followlinks and \
               self.__ext == other.ext

    def __find_filenames(self, dirname, i):
        """Find the filenames of directory 'dirname'.

        dirname: str, a directory name
        i      : int, the index in the directory dirname

        return: tuple(str, int, bool)
                      str : a new directory name if one is found or else the old one
                      int : the updated index of the directory dirname
                      bool: True if a new directory was found
        """
        directory = False
        dirlist = os.listdir(dirname) # convert directory contents to a list
        for name in dirlist[i:]:
            path = os.path.join(dirname, name) # get full path name
            i += 1
            if os.path.isfile(path):
                if not self.__ext:
                    print(path)
                else:
                    root, ext = os.path.splitext(path)
                    if ext == self.__ext:
                        self.__names.append(path)
            else:
                # a new directory has been found
                dirname = path
                directory = True
                break

        return dirname, i, directory

    def __push_stack(self, stack, dirnames, dirname):
        """Push directories in dirnames to the stack.

        stack   : list of str, a list of directory names to traverse
        dirnames: list of str, a list of directories to add to the stack
        dirname : str, the parent directory that contains dirnames
        """
        # insert every directory in dirnames at the end of the stack
        for directory in reversed(dirnames) if self.__topdown else dirnames:
            new_dirname = os.path.join(dirname, directory)

            # if followlinks == False and new_dirname == link do not insert
            if self.__followlinks or not os.path.islink(new_dirname):
                stack.append(new_dirname)

_DESK = "Print the contents of a directory and the directories below it."

def main():
    """Main entry point.

    return: int, success or failure
    """
    args = _cmdline()

    if 'ext' in args:
        print(walk(args.dir, args.ext))
    else:
        sys_call = False
        top = bool(args.top)
        follow = bool(args.follow)
        if sys_call:
            for dirpath, dirnames, filenames in os.walk(args.dir, top, followlinks = follow):
                print(dirpath, dirnames, filenames)
        else:
            for dirpath, dirnames, filenames in os_walk(args.dir, top, follow):
                print(dirpath, dirnames, filenames)

    return 0

def walk(dirname, extension = ''):
    """Get filenames of the directory 'dirname' and all its subdirectories.

    dirname  : str, a directory name
    extension: str, a filename extension. If supplied, only files matching the extension are
                    collected

    return: list of str, filenames
    """
    dir_walk = DirWalk(dirname, ext = extension)

    dir_walk.walk()

    return dir_walk()

def os_walk(dirname, topdown = True, followlinks = False):
    """Imitate the functionality of os.walk() of standard python library.

    dirname    : str, the directory to traverse
    topdown    : bool, see documentation of python standard library os.walk()
    followlinks: bool, True if sym links that are dirs are to be traversed

    return: list of tuple, tuple(str, list of str, list of str)
                                 str        : a directory name
                                 list of str: all directories under the directory name above
                                 list of str: all filenames under the directory name above
    """
    dir_walk = DirWalk(dirname, topdown, followlinks)

    dir_walk.os_walk()

    return dir_walk()

def _cmdline():
    """Validate command line arguments.

    return: argparse.Namespace object
    """
    # directory command line option
    parser_d = argparse.ArgumentParser(add_help = False)
    parser_d.add_argument('-d', '--dir', default = ".", help = 'the directory name (default: ".")')

    # main parser
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = _DESK,
                                     epilog = 'for further help type: '
                                              f'python {sys.argv[0]} <command> -h')

    # subparsers for the different commands
    subparsers = parser.add_subparsers(title = 'Commands',
                                       description = "The following commands allow you to print "
                                                     "all directory contents or by file extention.",
                                       help = 'DESCRIPTION', required = True)

    # create the parser for the "all" command
    parser_a = subparsers.add_parser('all', aliases = ['a'], parents = [parser_d],
                                     formatter_class = argparse.RawTextHelpFormatter,
                                     help = 'print all directory contents')
    parser_a.add_argument('-t', '--top', type = int, choices = [0, 1], default = 1,
                          help = "0 or 1, traverse topdown or the other way around (default: 1)")
    parser_a.add_argument('-f', '--follow', type = int, choices = [0, 1], default = 1,
                          help = "0 or 1, traverse sym links if they are directories (default: 1)")

    # create the parser for the "ext" command
    parser_a = subparsers.add_parser('ext', aliases = ['e'], parents = [parser_d],
                                     formatter_class = argparse.RawTextHelpFormatter,
                                     help = 'print directory contents by file extention')
    parser_a.add_argument('-e', '--ext', default = ".py",
                          help = 'print files with this extention only (default: ".py")')

    return parser.parse_args()

def _param_error(dirname, topdown, followlinks, ext):
    """Validate parameters.

    dirname    : str, a directory name
    topdown    : bool, see documentation of python standard library os.walk()
    followlinks: bool, if True follow links that point to directories
    ext        : str, a filename extension

    exceptions: ValueError, in case a parameter is of the wrong type
    """
    if not isinstance(dirname, str) or not isinstance(ext, str):
        raise ValueError("error: 'dirname' and 'ext' have to be of type 'str'")
    if not isinstance(topdown, bool) or not isinstance(followlinks, bool):
        raise ValueError("error: 'topdown' and 'followlinks' have to be of type 'bool'")

def _create_lists(dirname):
    """Create a list of files and a list of directories under the directory dirname.

    dirname: str, a directory

    return: tuple(list of str, list of str)
                  directory names, file names
    """
    filenames = []
    dirnames = []
    for name in os.listdir(dirname): # convert directory contents to a list
        path = os.path.join(dirname, name) # get full path name
        if os.path.isdir(path): # it's a directory
            dirnames.append(os.path.basename(path))
        elif os.path.isfile(path): # it's a file
            filenames.append(os.path.basename(path))

    return dirnames, filenames

if __name__ == '__main__':
    sys.exit(main())
