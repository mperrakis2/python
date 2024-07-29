"""This program plays the game of tic tac toe with the user. The computer's moves are random and
not based on any AI.

The computer always uses the 'X' symbol and starts first by placing the 'X' in the center position.
Positions are numbered from 1 to 9 and the center position is 5. The user may choose any number
from 1 to 9 to place the 'O' in the desired position.
"""
import sys
from random import randrange

class TicTacToe:
    """Implements tic tac toe functionality. Computer moves are random, not based on AI."""
    __STRIKE = 3 # used for printing and to determine a winner
    __REPEAT = 7 # number of repetitions for the fill char when printing the tic tac toe square

    def __init__(self):
        """ctor"""
        # init tic tac toe square, computer always has the first move placing 'X' in the center
        self.__board = [[1, 2, 3], [4, 'X', 6], [7, 8, 9]]

    def display_board(self):
        """Display the current state of the board."""
        for row in self.__board:
            _display_line(range(TicTacToe.__STRIKE), "+", "-" * TicTacToe.__REPEAT)
            _display_line(range(TicTacToe.__STRIKE), "|", " " * TicTacToe.__REPEAT)
            for column in row:
                print("|", " " * TicTacToe.__STRIKE, column, " " * TicTacToe.__STRIKE,
                      sep = "", end = "")
            print("|")
            _display_line(range(TicTacToe.__STRIKE), "|", " " * TicTacToe.__REPEAT)
        _display_line(range(TicTacToe.__STRIKE), "+", "-" * TicTacToe.__REPEAT)

    def game_over(self, sign):
        """Determine if there'a winner or a tie.

        sign: str, 'X' or 'O'

        return: bool, True if there's a winner or a tie
        """
        if self.__winner(sign): # check if there's a winner
            if sign == 'O':
                print("You win!")
            else:
                print("I win!")
            return True
        if self.__tie(): # check if there's a tie
            print("It's a tie!")
            return True

        return False

    def enter_move(self):
        """Prompt the user to enter her move."""
        while True: # loop until input is valid
            try:
                num = int(input("Enter your move: "))
                row, col = divmod(num - 1, TicTacToe.__STRIKE) # map move to square coordinates

                # if coordinates don't exist raise error
                if (row, col) not in self.__free_fields():
                    raise ValueError
                self.__board[row][col] = 'O' # update board with user's move
                break

            # the user entered wrong data so display list of valid choices
            except ValueError:
                print("Your move has to be one of: ", end = "")
                for row, col in self.__free_fields():
                    print(row * TicTacToe.__STRIKE + col + 1, end = " ")
                print()

    def draw_move(self):
        """Draw random move, not AI based, on behalf of the computer."""
        while True:
            choice = randrange(1, TicTacToe.__STRIKE ** 2)
            row, col = divmod(choice - 1, TicTacToe.__STRIKE) # map choice to square coordinates

            # if coordinates are used try again
            if (row, col) not in self.__free_fields():
                continue
            self.__board[row][col] = 'X' # update board with computer's move
            break

    @property
    def board(self):
        """return: list of list of int, the representation fo the tic tac toe board"""
        return self.__board

    def __str__(self):
        """Called when printing a tic tac toe object.

        return: str, the current state of the board
        """
        board = ''
        for row in self.__board:
            board += (str(row) + '\n')

        return board

    def __repr__(self):
        """Called when calling the representation (repr(tictactoe_obj)) of a tic tac toe object.

        return: str, the representation which allows a tic tac toe object to be identified
        """
        return f"<type: {self.__class__.__module__}.{self.__class__.__name__},"\
               f" id: {id(self)}>"

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: TicTacToe, the tic tac toe object to compare with

        return: bool or NotImplemented
                bool          :True if the two anagram objects are equal
                NotImplemented: if there's a parameter error
        """
        if not isinstance(other, TicTacToe):
            print(f"error: 'other' = {other!r} must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        return self.__board == other.board

    def __winner(self, sign):
        """Checks if the user or computer wins.

        sign: str, the 'X' or 'O' char

        return: bool, True if there's a winner
        """
        # check diagonals
        if (self.__board[0][0] == self.__board[1][1] == self.__board[2][2] == sign) or \
           (self.__board[2][0] == self.__board[1][1] == self.__board[0][2] == sign):
            return True

        # check vertically and horizontally
        for i in range(TicTacToe.__STRIKE):
            if (self.__board[i][0] == self.__board[i][1] == self.__board[i][2] == sign) or \
               (self.__board[0][i] == self.__board[1][i] == self.__board[2][i] == sign):
                return True

        return False

    def __tie(self):
        """Check if there's a tie.

        return: bool, True if there's a tie
        """
        for row in self.__board:
            for col in row:
                if col not in ('O', 'X'):
                    return False

        return True

    def __free_fields(self):
        """Determine which squares of the game have not been used.

        return: list of tuple(int, int), list of squares not used
                              int: the row number (0 based)
                              int: the col number (0 based)
        """
        free_fields = []
        for i, row in enumerate(self.__board):
            for j, col in enumerate(row):
                if col not in ('O', 'X'):
                    free_fields.append((i, j))

        return free_fields

def main():
    """Main entry point.

    return: int, success or failure
    """
    tic_tac_toe = TicTacToe()
    while True:
        tic_tac_toe.display_board()
        if tic_tac_toe.game_over('X'): # check if game is over after computer's move
            break
        tic_tac_toe.enter_move() # accept user's move
        tic_tac_toe.display_board()
        if tic_tac_toe.game_over('O'): # check if game is over after user's move
            break
        tic_tac_toe.draw_move() # draw random move for computer

    return 0

def _display_line(iterable, edge, filler):
    """Display a line of the tic tac toe square on the screen.

    iterable: any iterable, the number of iterations required to print a line on screen
    edge    : str, the first and last char to print
    filler  : str, the chars between the edges
    """
    for i in iterable:
        print(edge, filler, sep = "", end ="")
    print(edge)

if __name__ == '__main__':
    sys.exit(main())
