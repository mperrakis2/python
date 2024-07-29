def print_exception_tree(thisclass, nest = 0):
    """Print all standard Python exceptions.

    thisclass: BaseException
    nest     : int, the level of nested exceptions
    """
    if nest > 1:
        print("   |" * (nest - 1), end="")
    if nest > 0:
        print("   +---", end="")

    print(thisclass.__name__)

    for subclass in thisclass.__subclasses__():
        print_exception_tree(subclass, nest + 1)

print_exception_tree(BaseException)
