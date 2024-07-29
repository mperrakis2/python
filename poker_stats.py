"""This program calculates the probability of poker hands by generating a large number of random
sample hands."""
import sys
import timeit
import argparse

import utility
from poker_hand import PokerHand, Hand, Deck, Card

# Inherit class that provides functionality for adding two instances of the derived class and
# reference counting as well.
class PokerStats(utility.AdderWithRefCount):
    """Generate poker stats by generating random poker hands and classifying them."""
    NONE = 0
    UPDATE = 1
    APPEND = 2
    ITERATIONS = 10_000
    CARDS_PER_DECK = len(Card.suit_names) * len(Card.rank_names[1:])

    def __init__(self):
        super().__init__()
        self.__iterations = PokerStats.ITERATIONS # number of iterations to execute
        self.__cards_per_hand = PokerHand.MAX_NUM_CARDS # number of cards in a sample hand
        self.__operation = PokerStats.UPDATE # operation to execute
        # number of sample hands in a deck
        self.__hands_per_deck = PokerStats.CARDS_PER_DECK // self.__cards_per_hand
        self.__histogram = {} # contains poker hand types and their frequencies
        self.__samples = 0 # total number of sample hands generated

    def update(self, iterations = ITERATIONS, cards_per_hand = PokerHand.MAX_NUM_CARDS):
        """Generate poker hands, analyze them and store their frequencies.

        Clear previously generated stats if any.

        iterations    : int, the number of iterations to execute
        cards_per_hand: int, the number of cards in a generated sample hand

        return: bool, True if stats were updated
        """
        return self.__generate(iterations, cards_per_hand)

    def append(self, iterations = ITERATIONS, cards_per_hand = PokerHand.MAX_NUM_CARDS):
        """Generate poker hands, analyze them and append their frequencies to existing stats.

        iterations    : int, the number of iterations to execute
        cards_per_hand: int, the number of cards in a generated sample hand

        return: bool, True if stats were appended
        """
        return self.__generate(iterations, cards_per_hand, PokerStats.APPEND)

    def print(self, operation = NONE, iterations = ITERATIONS,
              cards_per_hand = PokerHand.MAX_NUM_CARDS):
        """Print existing or newly generated poker stats depending on the operation.

        operation     : int, the operation to execute, e.g. 'NONE' will print existing stats
        iterations    : int, the number of iterations to execute
        cards_per_hand: int, the number of cards in a generated sample hand

        return: bool, True if no error occured
        """
        generate = self.__generate(iterations, cards_per_hand, operation)
        print(self)

        return generate

    def clear(self):
        """Clear all poker stats."""
        self.__set(PokerStats.ITERATIONS, PokerHand.MAX_NUM_CARDS, PokerStats.UPDATE)

    @property
    def iterations(self):
        """return: int, number of iterations"""
        return self.__iterations

    @property
    def cards_per_hand(self):
        """return: int, number of cards per hand"""
        return self.__cards_per_hand

    @property
    def operation(self):
        """return: int, the operation type"""
        return self.__operation

    @property
    def histogram(self):
        """return: dict(int, int), key: hand type, value: frequency"""
        return self.__histogram

    def __str__(self):
        """Called when printing a poker stats object.

        return: str, the statistics collected so far
        """
        # The char width of the number of samples including commas. The number of samples is the
        # largerst number so its width should accomodate for any number printed
        int_width = self.__num_samples_width()

        # build the common part of the stats header
        common_header, str_width = self.__common_header(int_width)

        if self.__samples:
            pstats = self.__header(common_header, str_width) # build the stats header

            # iterate over histogram and store its hand data in a string
            for htype, freq in sorted(self.__histogram.items()):
                pstats += f"{PokerHand._LABELS[htype]:{PokerHand._LABEL_WIDTH}}: " \
                          f"{freq:{int_width},} -> " \
                          f"{freq / self.__samples:8.3%}\n"
        else:
            # if stats haven't been generated yet just print the values of data attributes as set
            # in the constructor
            pstats = self.__plain_header(common_header, str_width)

        return pstats

    def __repr__(self):
        """Called when calling the representation (repr(pokerstats_obj)) of a poker stats object.

        return: str, the representation which allows a poker stats object to be identified
        """
        return f"<type: {self.__class__.__module__}.{self.__class__.__name__},"\
               f" id: {id(self)}>"

    def __call__(self, iterations = ITERATIONS, cards_per_hand = PokerHand.MAX_NUM_CARDS):
        """See doc of returned method."""
        return self.update(iterations, cards_per_hand)

    def __bool__(self):
        """Called when a poker stats object is used as a boolean in an expression.

        return: bool, see __len__()
        """
        return bool(self.__len__())

    def __len__(self):
        """Called when calling the length (len(poker_stats_obj)) of a poker stats object.

        return: int, the number of poker hands generated
        """
        return self.__samples

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: PokerStats, the poker stats to compare with

        return: bool or NotImplemented
                bool          : True if two poker stats are equal
                NotImplemented: if there's a parameter error
        """
        if not isinstance(other, PokerStats):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        return self._is_add(other) and self.__histogram == other.histogram

    def __iter__(self):
        """Called whenever an iterator of a poker stats object is requested.

        return: iterator object, a poker stats object iterator
        """
        return iter(self.__histogram)

    def __getitem__(self, key):
        """Called when implementing evaluation of self[key].

        key: int, the poker hand type

        exceptions: TypeError, if key is of an inappropriate type
                    KeyError, if key is not in the container

        return: int, the poker hand type frequency
        """
        return self.__histogram[key]

    def _is_add(self, other):
        """Check if two poker stats objects can be added.

        other: PokerStats, the poker stats object to compare this one to

        return: bool, True if both poker stats objects can be added
        """
        return self.__iterations == other.iterations and \
               self.__cards_per_hand == other.cards_per_hand and \
               self.__operation == other.operation

    def _op_add(self, other):
        """Add a poker stats object to this one.

        other: PokerStats
        """
        for htype, freq in other.histogram.items():
            self.__histogram.setdefault(htype, 0)
            self.__histogram[htype] += freq
        self.__samples += len(other)

    def __generate(self, iterations, cards_per_hand, operation = UPDATE):
        """Generate poker hands, analyze them and store their frequencies.

        iterations    : int, the number of iterations to execute
        cards_per_hand: int, the number of cards in a generated sample hand
        operation     : int, the operation to execute, e.g. 'UPDATE' will generate new stats

        return: bool, True if no parameter error
        """
        if operation: # in case it's called by print() with operation = NONE
            # check and store new parameters
            if self.__set(iterations, cards_per_hand, operation):
                deck = Deck()
                hand = PokerHand()
                for i in range(self.__iterations):
                    deck.shuffle()
                    for j in range(self.__hands_per_deck): # iterate over number of hands in a deck
                        deck.move_cards(hand, self.__cards_per_hand) # add cards to sample hand

                        # classify the hand and use False to enable performance optimizations
                        current_hand = hand.classify(normal_flow = False)
                        if current_hand: # if it's a valid hand
                            htype = current_hand[0] # get hand type
                            self.__histogram.setdefault(htype, 0) # add to the hand type histogram
                            self.__histogram[htype] += 1 # increment hand type frequency

                        Hand.__init__(hand) # reset base class data attributes
                    deck.__init__() # reset deck data attributes

                self.__samples += self.__iterations * self.__hands_per_deck

                return True
            return False
        return True

    def __set(self, iterations, cards_per_hand, operation):
        """Set data attributes.

        iterations    : int, the number of iterations to execute
        cards_per_hand: int, the number of cards in a generated sample hand
        operation     : int, the operation to execute

        return: bool, True if no parameter error
        """
        if self.__iterations != iterations or \
           self.__cards_per_hand != cards_per_hand or \
           self.__operation != operation:
            if _param_error(iterations, cards_per_hand, operation): # check for param errors
                return False
            if operation == PokerStats.APPEND and \
               self.__cards_per_hand != cards_per_hand and \
               self.__histogram:
                # When appending, the new number of cards per sample hand has to be equal with the
                # previous one to keep the statistics consistent. However, there's an error only if
                # a histogram with different number of cards per hand already exists.
                print("append error: current and new number of cards must be equal: "
                      f"{self.__cards_per_hand} != {cards_per_hand}")
                return False

            self.__iterations = iterations
            self.__cards_per_hand = cards_per_hand
            self.__operation = operation
            # number of sample hands in a deck
            self.__hands_per_deck = PokerStats.CARDS_PER_DECK // self.__cards_per_hand

        # clear stats if stats exist and update was requested
        if self.__samples and self.__operation == PokerStats.UPDATE:
            self.__clear()

        return True

    def __clear(self):
        """Clear poker stats for an update."""
        self.__histogram.clear()
        self.__samples = 0
        super().clear()

    def __num_samples_width(self):
        """Calculate the char width of the number of samples including commas.

        return: int, the char width of the number of samples including commas
        """
        digits = len(str(self.__samples)) # the number of digits in the number of samples
        commas = digits // 3 # number of commas in the number of samples

        # add to the number of digits the number of commas
        return digits + (commas if digits % 3 else commas - 1)

    def __common_header(self, int_width):
        """Build the common part of the stats header.

        int_width: int, the char width to print numbers

        return: tuple(str, int), the common part of the stats header and the char width of the
                                 longest string
        """
        # build the common part of stats
        common_header = "cards per hand" # longest string
        str_width = len(common_header) # width of longest string
        common_header = f"{common_header} = {self.__cards_per_hand}\n" \
                        f"{'hands per deck':{str_width}} = {self.__hands_per_deck:<{int_width}}, "\
                        f"({PokerStats.CARDS_PER_DECK} / {self.__cards_per_hand} = " \
                        "cards per deck / cards per hand)\n"

        return common_header, str_width

    def __header(self, common_header, width):
        """Build the stats header.

        common_header: str, the common part of the stats header
        width        : int, the char width to print strings

        return: str, the stats header
        """
        # self.__iterations is NOT equal to total iterations
        total_iterations = self.__samples // self.__hands_per_deck

        return f"{common_header}" \
               f"{'iterations':{width}} = {total_iterations:,}\n" \
               f"{'samples':{width}} = {self.__samples:,}, " \
               f"({self.__hands_per_deck} * {total_iterations:,} = hands per deck * iterations)\n\n"

    def __plain_header(self, common_header, width):
        """Build the stats header when no stats have been generated yet.

        common_header: str, the common part of the stats header
        width        : int, the char width to print strings

        return: str, the stats header when no stats have been generated yet
        """
        # if stats haven't been generated yet just print the values of data attributes as set in
        # the constructor
        return f"{common_header}" \
               f"{'iterations':{width}} = {self.__iterations:,}\n" \
               f"{'operation':{width}} = " \
               f"{'UPDATE' if self.__operation == PokerStats.UPDATE else 'APPEND'}\n"

_DESC = f"""\
Calculate poker statistics by generating random poker hands and classifying them.

A number of iterations is executed and in each iteration a number of random poker hands are
generated per deck. The number of cards per deck is {PokerStats.CARDS_PER_DECK}. If cards == {PokerHand.MAX_NUM_CARDS} then {PokerStats.CARDS_PER_DECK // PokerHand.MAX_NUM_CARDS} ({PokerStats.CARDS_PER_DECK} / {PokerHand.MAX_NUM_CARDS}) random
poker hands are generated per iteration. Thus, if iterations == {PokerStats.ITERATIONS} and cards == {PokerHand.MAX_NUM_CARDS} the total
number of random poker hands generated is {PokerStats.ITERATIONS} * ({PokerStats.CARDS_PER_DECK} / {PokerHand.MAX_NUM_CARDS}) = {PokerStats.ITERATIONS * (PokerStats.CARDS_PER_DECK // PokerHand.MAX_NUM_CARDS)}.
"""

_EPILOG = f"""\
usage example: python {sys.argv[0]} -i {PokerStats.ITERATIONS} -c {PokerHand.MAX_NUM_CARDS}
                   or
               python {sys.argv[0]} -i {PokerStats.ITERATIONS} -c {PokerHand.MAX_NUM_CARDS} -r 10
"""

def main():
    """Main entry point.

    return: int, success or failure
    """
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = _DESC, epilog = _EPILOG)
    parser.add_argument('-i', '--iterations', type = int, default = 10_000,
                        help = "the number of iterations to run; must be > 0 (default: 10,000)")
    parser.add_argument('-c', '--cards', type = int, default = PokerHand.MAX_NUM_CARDS,
                        help = "the number of cards per sample; must be within "
                               f"[{PokerHand.MIN_NUM_CARDS}, {PokerHand.MAX_NUM_CARDS}] "
                               f"(default: {PokerHand.MAX_NUM_CARDS})")
    parser.add_argument('-r', '--repeat', type = int, default = 1,
                        help = "the number of times to repeat the iterations; "
                               "used for performance testing only (default: 1)")
    args  = parser.parse_args()

    # check integer command line parameters
    if args.iterations < 1 or \
       not PokerHand.MIN_NUM_CARDS <= args.cards <= PokerHand.MAX_NUM_CARDS:
        sys.exit("error: 'iterations' must be an integer > 0 and "
                 "'cards' an integer within "
                 f"[{PokerHand.MIN_NUM_CARDS}, {PokerHand.MAX_NUM_CARDS}]")
    if args.repeat < 1:
        sys.exit("error: 'repeat' must be integer > 0")

    if args.repeat > 1:
        custom_namespace = {'test_perf':_perf_test,
                            'iterations':args.iterations,
                            'cards_per_hand':args.cards}
        duration = timeit.timeit(stmt = 'test_perf(iterations, cards_per_hand)',
                                 number = args.repeat,
                                 globals = custom_namespace)

        # the following is commented out but it is slightly faster as it does not involve a
        # function call

        #custom_namespace2 = {'PokerStats':PokerStats,
        #                     'iterations':args.iterations,
        #                     'cards_per_hand':args.cards}
        #duration = timeit.timeit(stmt = 'pstats = PokerStats();'
        #                                'pstats.update(iterations, cards_per_hand);'
        #                                'print(pstats)',
        #                         number = args.repeat,
        #                         globals = custom_namespace2)

        print(f'On average it took {duration} seconds.')
    else:
        pstats = PokerStats()
        pstats(args.iterations, args.cards)
        print(pstats)

    return 0

def _perf_test(iterations, cards_per_hand):
    """Wrapper function used for testing."""
    pstats = PokerStats()
    pstats(iterations, cards_per_hand)
    print(pstats)

def _param_error(iterations, cards_per_hand, operation):
    """Validate parameters.

    iterations    : int, the number of times to iterate
    cards_per_hand: int, the number of cards in a sample hand
    operation     : int, the type of operation to execute

    exceptions: TypeError,  in case any of the parameters is not an int
                ValueError, in case iterations < 1
                            in case the number of cards is not within a valid range
                            in case the operation is not a valid one
    """
    if not isinstance(iterations, int) or \
       not isinstance(operation, int) or \
       not isinstance(cards_per_hand, int):
        print("error: all parameters have to be of type 'int'")
        return True
    if iterations < 1:
        print(f"error: 'iterations' = '{iterations}' must be > 0")
        return True
    if not PokerHand.MIN_NUM_CARDS <= cards_per_hand <= PokerHand.MAX_NUM_CARDS:
        print(f"error: 'cards_per_hand' = {cards_per_hand} must be within "
              f"[{PokerHand.MIN_NUM_CARDS}, {PokerHand.MAX_NUM_CARDS}]")
        return True
    if operation not in range(PokerStats.APPEND + 1):
        print(f"error: 'operation' = {operation} must be within "
              f"[{PokerStats.NONE}, {PokerStats.APPEND}]")
        return True

    return False

if __name__ == '__main__':
    sys.exit(main())
