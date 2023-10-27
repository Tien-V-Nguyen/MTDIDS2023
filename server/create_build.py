""" Strip comments and docstrings from a file.
"""

import os
import sys, token, tokenize
from distutils.dir_util import copy_tree

# Inspiration: https://stackoverflow.com/questions/1769332/script-to-remove-python-comments-docstrings
def do_file(fname):
    """ Run on just one file.

    """
    source = open(fname)
    #mod = open(fname + ",strip", "w")
    mod = open(fname + ",strip", "w")

    prev_toktype = token.INDENT
    first_line = None
    last_lineno = -1
    last_col = 0

    tokgen = tokenize.generate_tokens(source.readline)
    for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
        if 0:   # Change to if 1 to see the tokens fly by.
            print("%10s %-14s %-20r %r" % (
                tokenize.tok_name.get(toktype, toktype),
                "%d.%d-%d.%d" % (slineno, scol, elineno, ecol),
                ttext, ltext
                ))
        if slineno > last_lineno:
            last_col = 0
        if scol > last_col:
            mod.write(" " * (scol - last_col))
        if toktype == token.STRING and prev_toktype == token.INDENT:
            # Docstring
            #mod.write("")
            pass
        elif toktype == tokenize.COMMENT:
            # Comment
            #mod.write("##\n")
            pass
        else:
            mod.write(ttext)
        prev_toktype = toktype
        last_col = ecol
        last_lineno = elineno
    
    # Remove old file
    os.remove(fname)
    # Rename the stripped file
    os.rename(fname + ",strip", fname)

def iterate():
    """
    Copies the microPython to a build directory,
    then strips the python files for comments.
    """
    current_directory = os.getcwd()
    fromDirectory = os.path.join(current_directory, r'microPython')
    toDirectory = os.path.join(current_directory, r'microPythonBuild')

    if not os.path.exists(toDirectory):
        print("Creating directory", toDirectory)
        os.makedirs(toDirectory)

    copy_tree(fromDirectory, toDirectory)

    # Iterate over all the python files in the build
    for subdir, dirs, files in os.walk(toDirectory):
        for file in files:
            fileName = os.path.join(subdir, file)
            print("File:", fileName)

            # If python file, remove comments!
            if file.endswith('.py'):
                do_file(fileName)
            elif file.endswith('.txt') or file.endswith('.conf'):
                pass
            elif file.endswith(''):
                # Remove the file (license in this case)
                os.remove(fileName)

if __name__ == '__main__':
    iterate()
    #do_file(sys.argv[1])