"""This programs goes through a list or tuple of files with a specific extention and checks whether
files with exactly the same contents exist using md5.
"""
import sys
import os
import argparse

import directory
import utility

_DESC = """\
Read files with a specific extention under a directory and create an MD5 value for each file. Print
the files that have the same MD5 value and then double check that their contents are identical.
"""

def main():
    """Main entry point.

    return: int, success or failure
    """
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = _DESC,
                                     epilog = f'usage example: python {sys.argv[0]} . .py')
    parser.add_argument('-d', '--dir', required = True, help = "read files under this directory")
    parser.add_argument('-e', '--ext', required = True, help = "the file extention")
    args  = parser.parse_args()

    # get all files under the args.dir that have extention args.ext
    filenames = directory.walk(args.dir, args.ext)

    # print all filenames that have the same content
    for md5_val, fnames in _md5_filenames(filenames).items():
        if len(fnames) > 1:        # more than one file with same content has been found
            print(md5_val, fnames) # print filenames with same content
            _cmpfiles(fnames)      # double check files have the same content

    return 0

def _md5_filenames(filenames):
    """Return a dictionary with md5 values for all files in 'filenames'.

    filenames: list of str

    return: dict(str, list of str)
                 str        : md5 value
                 list of str: filenames with the same md5
    """
    md5_fnames = {}

    for filename in utility.get_filenames(filenames): # get full path of filenames
        try:
            size = os.path.getsize(filename)
        except OSError as exc:
            print(f"error: when accessing file {filename} "
                  f"the following exception occured: {exc}")
        else:
            if size > 0: # md5 can't be calculated on empty files
                md5_val = utility.md5(filename) # calculate md5 value for given file
                if md5_val:
                    # get value for key=md5_val if one exists else get the emtpy list
                    file_names = md5_fnames.setdefault(md5_val, [])
                    file_names.append(filename) # add filename to filename list
                else:
                    print(f"error: could not calculate md5 value of file '{filename}'. "
                           "File can't be compared.")

    return md5_fnames

def _cmpfiles(filenames):
    """Compare all files in 'filenames'.

    Comparison is based on file contents. Print filenames that are not identical.

    filenames: list of str
    """
    for fname in filenames:
        i = 1
        for filename in filenames[i:]:
            if utility.cmpfiles(fname, filename):
                print(f"error: files '{fname}', '{filename}' are not equal!")
        i += 1

if __name__ == '__main__':
    sys.exit(main())
