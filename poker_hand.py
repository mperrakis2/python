"""This program classifies a poker hand from a list of cards. It can print the poker hand and
compare it to a different one to identify the better hand.
"""
import sys
import copy

from card import Hand, Deck, Card

class PokerHand(Hand):
    """Classifies a poker hand from a list of cards. The number of cards must be within a valid
    range.
    """
    # all possible poker hands
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8

    MIN_NUM_CARDS = 5 # min number of cards in a hand
    MAX_NUM_CARDS = 7 # max number of cards in a hand

    _LABELS = ("high card", "pair", "two pair", "three of a kind", "straight",
                "flush", "full house", "four of a kind", "straight flush", "rest of hand")
    _LABEL_WIDTH = len(max(_LABELS, key = len)) # maximum width of a hand label

    __SEQUENCE = 5 # number of cards in a straight flush and straight

    # the maximum length of the data structure that holds the hand,
    # see 'self.__hand' comments below
    __MAXLEN_HAND = 3

    def __init__(self, *cards):
        """cards: tuple or list of Card, a sequence of cards to initialize the poker hand object"""
        super().__init__()
        for card in cards: # if cards exist, initialize the poker hand object with them
            if len(self.cards) == PokerHand.MAX_NUM_CARDS:
                print(f"error: number of cards cannot be > {PokerHand.MAX_NUM_CARDS}")
                break
            if isinstance(card, Card): # add the card to the cards list
                # can't use derived class method as it uses an attribute that has not yet been
                # initialized by the ctor
                super().add_card(card)
            else:
                print(f"error: 'card' = '{card}' must be of type 'Card'")

        self.__reset() # init data attributes

        if cards: # if cards were passed as parameters, the hand needs to be classified
            self.classify()

    def add_card(self, card):
        """Override base class method.

        Add check to make sure the number of cards and card type are correct.

        card: Card, the new card to add to the list of cards

        return: bool, True if the new card was added
        """
        if self.__normal_flow: # no performance optimizations
            if len(self.cards) == PokerHand.MAX_NUM_CARDS:
                print(f"error: number of cards cannot be > {PokerHand.MAX_NUM_CARDS}")
                return False
            if not isinstance(card, Card):
                print(f"error: 'card' = '{card}' must be of type 'Card'")
                return False

        super().add_card(card)
        return True

    def classify(self, normal_flow = True, print_error = True):
        """Classify hand from a list of cards.

        normal_flow: bool, True if no performance optimizations
        print_error: bool, print errors if any

        return: list (see definition of self.__hand), the classified hand
        """
        if normal_flow != self.__normal_flow and not isinstance(normal_flow, bool):
            print(f"error: 'normal_flow' = '{normal_flow}' must be of type 'bool'")
            return self.__hand

        if not normal_flow or self.__update(print_error): # check if cards have been updated
            self.__reset(normal_flow) # reset data attributes

            # iterate over all cards and populate data structures for suits and ranks
            for card in self.cards:
                self.__suits.setdefault(card.suit, []).append(card)
                self.__ranks.setdefault(card.rank, []).append(card)

            self.__suit() # check for straight flush or flush
            self.__rank() # check for 4 of a kind, full house, straight, 3 of a kind, 2 pair or pair

            if not self.__hand: # add high card if no hand was added
                self.__add(PokerHand.HIGH_CARD, [self.__high_card()])

            if self.__normal_flow: # no performance optimizations
                self.__rest() # add the rest of the hand, if any

        return self.__hand

    def has(self, htype):
        """Check if the hand has the requested hand type.

        htype: int, the requested hand type to check for

        return: bool, True if the hand has the requested hand type
        """
        if not isinstance(htype , int):
            print(f"error: 'htype' = '{htype}' must be of type 'int'")
            return False
        if not htype in range(PokerHand.STRAIGHT_FLUSH + 1):
            print(f"error: 'htype' = {htype} must be within "
                  f"[{PokerHand.HIGH_CARD}, {PokerHand.STRAIGHT_FLUSH}]")
            return False

        return htype == self.__hand[0] if self.classify() else False

    def compare(self, other):
        """Compare this hand to the hand passed in as a parameter.

        other: PokerHand, a hand to compare to this hand

        return: str, the comparison description
        """
        if not isinstance(other , PokerHand):
            print("error: 'other' must be of type 'PokerHand'")
            return str()

        if other is self:
            desc = 'comparing poker hand object to itself'
        else:
            desc = "\nresult\n======\n"
            # execute the comparison operators first to make sure there exist valid hands
            result = self == other
            if result:
                desc += "the two hands are equal\n"
            elif result is not None:
                result = self > other
                if result:
                    desc += "'this hand' is better\n"
                elif result is not None:
                    desc += "'other hand' is better\n"

            if result is None:
                desc += "one or both hands are in error\n"
            else:
                desc = f"\nthis hand\n=========\n{super().__str__()}" \
                       f"\n\nother hand\n==========\n{Deck.__str__(other)}" \
                       f"\n\nthis hand\n========={self.string(False)}" \
                       f"\nother hand\n=========={other.string(False)}" \
                       f"{desc}"

        return desc

    def string(self, base = True):
        """Create a printable poker hand object.

        base: bool, True if super().__str__() is to be called

        return: str, the hand description
        """
        if not isinstance(base, bool):
            return f"error: 'base' = '{base}' must be of type 'bool'"

        desc = super().__str__() if base else ''

        if self.classify(print_error = False): # if no error
            # append the hand description
            if base:
                desc += '\n'
            desc += f"\n{self.label:{PokerHand._LABEL_WIDTH}}: {_description(self.__hand[1])}\n"

            # append the description for the rest of the hand
            if len(self.__hand) == PokerHand.__MAXLEN_HAND:
                desc += f"{PokerHand._LABELS[-1]:{PokerHand._LABEL_WIDTH}}: " \
                        f"{_description(self.__hand[2])}\n"
        else: # an error occured
            desc += "\n\nerror: the number of cards in a hand must be >= " \
                    f"{PokerHand.MIN_NUM_CARDS}"

        return desc

    def clear(self):
        """Clear the hand by calling ctor."""
        super().__init__()
        self.__reset() # init data attributes

    def __str__(self):
        """Called when printing a poker hand object.

        return: str, the hand description
        """
        return self.string()

    def __repr__(self):
        """Called when calling the representation (repr(poker_hand_obj)) of a poker hand object.

        return: str, the representation which allows an object equal to this one to be created
        """
        return f"{self.__class__.__module__}.{self.__class__.__name__}"\
               f"({str(self.cards).replace('[', '').replace(']', '')})"

    def __call__(self, htype):
        """See doc of returned method."""
        return self.has(htype)

    def __len__(self):
        """Called when calling the length (len(poker_hand_obj)) of a poker hand object.

        return: int, the number of cards in a hand
        """
        return len(self.__hand)

    def __eq__(self, other):
        """Overloaded '==' operator.

        other: PokerHand, the poker hand to compare with

        return: bool or NotImplemented
                bool          :True if two poker hands are equal
                NotImplemented: if there's a parameter error or any hand is incomplete
        """
        if not isinstance(other, PokerHand):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        self.classify()
        other_hand = other.classify() # get hand for other object

        # Two hands are equal if the hand types are equal and the ranks of the cards are equal. If
        # rest of hand exists, card ranks must be equal as well.
        if self.__hand and other_hand:
            # hands have the same type and same cards based on rank
            if self.__hand[0] == other_hand[0] and _compare_eq(self.__hand[1], other_hand[1]):
                # compare rest of hand if it exists
                return _compare_eq(self.__hand[2], other_hand[2]) \
                       if len(self.__hand) == PokerHand.__MAXLEN_HAND \
                       else True
        else:
            return NotImplemented

        return False

    def __lt__(self, other):
        """Overloaded '<' operator.

        other: PokerHand, the poker hand to compare with

        return: bool or NotImplemented
                bool          :True if poker hand is < other poker hand
                NotImplemented: if there's a parameter error or any hand is incomplete
        """
        if not isinstance(other, PokerHand):
            print(f"error: 'other' = '{other}' must be of type "
                  f"'{self.__class__.__module__}.{self.__class__.__name__}'")
            return NotImplemented

        self.classify()
        other_hand = other.classify() # get hand for other object

        if self.__hand and other_hand:
            if self.__hand[0] < other_hand[0]: # one hand is smaller than the other
                return True
            if self.__hand[0] == other_hand[0]: # hands have same hand type
                cmp = _compare_lt(self.__hand[1], other_hand[1]) # compare cards of hands
                if cmp is None: # cards are equal
                    # compare rest of hand if it exists
                    return bool(_compare_lt(self.__hand[2], other_hand[2])) \
                           if len(self.__hand) == PokerHand.__MAXLEN_HAND \
                           else False
                return cmp
        else:
            return NotImplemented

        return False

    def __le__(self, other):
        """Overloaded '<=' operator.

        other: PokerHand, the poker hand to compare with

        return: bool or NotImplemented
                bool          :True if poker hand is <= other poker hand
                NotImplemented: if there's a parameter error or any hand is incomplete
        """
        return cmp_lt \
               if (cmp_lt := self.__lt__(other)) is NotImplemented or cmp_lt else \
               self.__eq__(other)

    def __iter__(self):
        """Called whenever an iterator of a poker hand object is requested.

        return: iterator object, a poker hand object iterator
        """
        return iter(self.__hand)

    def __getitem__(self, key):
        """Called when implementing evaluation of self[key].

        key: int or slice

        return: Card

        exceptions: TypeError, if key is of an inappropriate type
                    IndexError, if key is of a value outside the set of indexes for the sequence
        """
        return self.__hand[key]

    def __update(self, print_error):
        """Check if cards have been updated.

        print_error: bool, print errors, if any

        return: bool, True if hand needs classification and there's no error
        """
        if not isinstance(print_error, bool):
            print(f"error: 'print_error' = '{print_error}' must be of type 'bool'")
            return False
        if len(self.cards) < PokerHand.MIN_NUM_CARDS: # not enough cards
            self.__reset(normal_flow = True) # reset data attributes
            if print_error:
                print(f"{super().__str__()}\n\n"
                      f"error: the number of cards in a hand must be >= {PokerHand.MIN_NUM_CARDS}")
            return False
        if sorted(self.__cards_copy) == sorted(self.cards): # check if cards have been updated
            return False

        return True

    def __reset(self, normal_flow = False):
        """Initialization method called by ctor and elsewhere.

        normal_flow: bool, True if no performance optimizations
        """
        self.__normal_flow = normal_flow # if False, enable performance optimizations
        self.__cards_copy = [] # copy of the cards
        if self.__normal_flow: # copy the cards
            self.__cards_copy = copy.deepcopy(self.cards)
        self.__suits = {} # cards with same suit
        self.__ranks = {} # cards with same rank

        # Hand classified from list of cards. Its structure is as follows:
        #
        # first element : int, the hand type
        # second element: list of Card, the hand itself
        # third element : list of Card if any, the rest of the hand if any
        #
        # As by poker rules, hand + rest of hand = 5 cards always. Thus, if a hand
        # is 5 cards already, e.g. full house, there's no rest of hand.
        self.__hand = []

    def __suit(self):
        """Classify hand based on suit, i.e. straight flush and flush."""
        # If there are 7 cards, at least MIN_NUM_CARDS are required to have a suit hand. That means
        # that a maximum of 3 different suits are possible out of 7 cards, provided a suit hand
        # exists. In general, if there are 'n' cards, 'n - MIN_NUM_CARDS + 1' is the maximum number
        # of suits possible, provided a suit hand exists.
        if len(self.__suits) <= len(self.cards) - PokerHand.MIN_NUM_CARDS + 1:
            for hand in self.__suits.values(): # iterate over suits
                if len(hand) >= PokerHand.MIN_NUM_CARDS: # a suit hand exists
                    # the hand has to be sorted descendingly in order to determine if it is a
                    # straight flush and have the highest cards first
                    hand.sort(reverse = True)

                    ace = hand[-1].rank == 1
                    # check if the hand is a straight flush where the ace is the first card
                    if ace and hand[PokerHand.__SEQUENCE-2].rank == 10: # ace, king, queen, jack, 10
                        hand.insert(0, hand.pop()) # insert the ace as the first card

                        # add straight flush
                        self.__add(PokerHand.STRAIGHT_FLUSH, hand[:PokerHand.__SEQUENCE])
                        return

                    # Suppose the cards are 10,8,6,5,4,3,2. The straight flush is 6,5,4,3,2.
                    # So the algorithm is: is 10 == 4 + 4 -> no
                    #                      is  8 == 3 + 4 -> no
                    #                      is  6 == 2 + 4 -> yes
                    # So, out of 7 cards there's a maximum of 3 iterations. In general, if there
                    # are 'n' cards, the maximum number of iterations is 'n - SEQUENCE + 1'.
                    for i in range(len(hand) - PokerHand.__SEQUENCE + 1):
                        high_card_rank = hand[i+PokerHand.__SEQUENCE-1].rank + \
                                         PokerHand.__SEQUENCE - 1
                        if hand[i].rank == high_card_rank:
                            # add straight flush
                            self.__add(PokerHand.STRAIGHT_FLUSH, hand[i : i+PokerHand.__SEQUENCE])
                            return

                    if ace: # if we got here it's a flush and last card is an ace
                        hand.insert(0, hand.pop()) # insert the ace as the first card

                    self.__add(PokerHand.FLUSH, hand[:PokerHand.MIN_NUM_CARDS]) # add flush
                    return

    def __rank(self):
        """Add rank hand, i.e. 4 of a kind, full house, straight, 3 of a kind, two pair and pair."""
        if not self.__hand:
            # sort ranks descendingly so that better hands are detected first
            ranks = sorted(self.__ranks.items(), reverse = True)
            ace = None

            # ranks[i] -> a single rank which is a tuple -> (int, list of Card or hand)
            #      [0] -> the first element of the tuple, i.e. the rank of the hand
            if ranks[-1][0] == 1: # save the ace card if any
                # ranks[i] -> a single rank which is a tuple -> (int, list of Card or hand)
                #      [1] -> the second element of the tuple, i.e. the hand
                #      [0] -> the first card of the hand
                ace = ranks[-1][1][0]

            if self.__straight(ranks, ace): # add straight if any
                return

            # There is no straight so if an ace card exists, make the ace hand the first hand in
            # the list of hands. This is necessary, as for example a pair of aces is preferred
            # over a pair of kings in a full house.
            if ace:
                ranks.insert(0, ranks.pop())

            three = []
            pairs = []
            for hand in ranks:
                match len(hand[1]):
                    case 2: # pair, add potential full house
                        if self.__full_house(hand[1], pairs, three):
                            return
                    case 3: # three of a kind, add potential full house
                        if self.__full_house(hand[1], three, pairs):
                            return
                    case 4: # add 4 of a kind
                        self.__add(PokerHand.FOUR_OF_A_KIND, hand[1])
                        return

            if len(pairs) == 2: # add pair
                self.__add(PokerHand.PAIR, pairs)
            elif pairs: # add two pair
                self.__add(PokerHand.TWO_PAIR, pairs[:4])
            elif three: # add 3 of a kind
                self.__add(PokerHand.THREE_OF_A_KIND, three)

    def __straight(self, ranks, ace):
        """Add a straight hand.

        ranks: list of tuple, tuple is the rank of a hand and the hand itself, i.e.
                              tuple -> (int, list of Card)
        ace  : Card or None, the ace card or None if no ace card exists

        return: bool, True if a straight was added
        """
        # for a straight to exist, at least 5 ranks are required
        if len(ranks) >= PokerHand.__SEQUENCE:
            # check if the hand is a straight where the ace is the first card
            if ace and ranks[PokerHand.__SEQUENCE-2][0] == 10: # ace, king, queen, jack, 10
                hand = []
                hand.append(ace) # add the ace as the first card

                # after the ace card add the rest of the cards
                # ranks[i] -> a single rank which is a tuple -> (int, list of Card or hand)
                #      [1] -> the second element of the tuple, i.e. the hand
                #      [0] -> the first card of the hand
                hand.extend(ranks[i][1][0] for i in range(PokerHand.__SEQUENCE - 1))
                self.__add(PokerHand.STRAIGHT, hand) # add straight
                return True

            # Same exact logic as per straight flush. See comments for adding a straight flush
            # that does not have an ace.
            for i in range(len(ranks) - PokerHand.__SEQUENCE + 1):
                # ranks[i] -> a single rank which is a tuple -> (int, list of Card or hand)
                #      [0] -> the first element of the tuple, i.e. the rank of the hand
                high_card_rank = ranks[i+PokerHand.__SEQUENCE-1][0] + PokerHand.__SEQUENCE - 1
                if ranks[i][0] == high_card_rank:
                    hand = []
                    # to get an explanation for ranks[j][1][0] see the comments above for adding
                    # a straight that contains an ace
                    hand.extend(ranks[j][1][0] for j in range(i, i + PokerHand.__SEQUENCE))
                    self.__add(PokerHand.STRAIGHT, hand) # add straight
                    return True

        return False

    def __full_house(self, hand, same_hand, complementary_hand):
        """Add a potential full house.

        hand:               list of Card, the hand
        same_hand:          list of Card, a hand with the same hand type as 'hand'
        complementary_hand: list of Card, a hand that is a complement of 'hand', e.g. if 'hand' is
                            a pair then 'complementary_hand' could be a three of a kind so that
                            3 + 2 = full house

        return: bool, True if a full house was added
        """
        if complementary_hand: # if a complementary hand exists, add a full house
            if len(hand) == 2: # pair
                self.__add(PokerHand.FULL_HOUSE, complementary_hand + hand)
            else:
                self.__add(PokerHand.FULL_HOUSE, hand + complementary_hand[:2])
            return True

        # a three exists already in 'same_hand' and 'hand' is another three so add a full house
        # (the highest three is 'same_hand')
        if len(same_hand) == 3:
            self.__add(PokerHand.FULL_HOUSE, same_hand + hand[:-1])
            return True

        same_hand.extend(hand)

        return False

    def __add(self, htype, hand):
        """Add a single hand and its label.

        htype: int, the hand type, e.g. pair, flush, etc.
        hand : list of Card, the cards of the hand
        """
        self.__hand.extend((htype, hand))
        if self.__normal_flow: # no performance optimizations
            self.label = PokerHand._LABELS[htype]

    def __high_card(self):
        """Get the high card in a list of cards.

        return: Card, the high card
        """
        high_card = Card() # init to smallest value
        for card in self.cards:
            if card.rank == 1: # ace is always the high card
                return card
            if card.rank > high_card.rank:
                high_card = card

        return high_card

    def __rest(self):
        """ Add the rest of the hand, if any, to the hand.

        The rest of the hand are cards that when added to the hand make up a total of MIN_NUM_CARDS
        cards. Thus, 'hand + rest = MIN_NUM_CARDS'. This is required, as it is a rule of Poker.
        """
        if len(self.__hand) == PokerHand.__MAXLEN_HAND - 1: # only add the rest of the hand once!
            # If hand has length < MIN_NUM_CARDS add to it the rest of the cards, in order of rank,
            # so that 'hand + rest = MIN_NUM_CARDS'.
            rest = PokerHand.MIN_NUM_CARDS - len(self.__hand[1])
            if rest:
                # delete cards that are part of the hand to facilitate extracting the rest of the
                # hand
                for card in self.__hand[1]:
                    self.__cards_copy.remove(card)

                # the remaining cards are part of the rest of the hand and are sorted descendingly
                # by rank
                self.__cards_copy.sort(key=lambda card: card.rank, reverse = True)

                # if an ace exists, add it to the top of the list
                if self.__cards_copy[-1].rank == 1:
                    self.__cards_copy.insert(0, self.__cards_copy.pop())

                self.__hand.append(self.__cards_copy[:rest]) # finally, add the rest of the hand
                self.__cards_copy.extend(copy.deepcopy(self.__hand[1])) # restore original cards

def main():
    """Main entry point.

    return: int, success or failure
    """
    hand = PokerHand()
    print(hand(PokerHand.TWO_PAIR))
    print(hand) # test __str__() with no cards
    hand = PokerHand(Card(1,12), Card(1,11), "zxczxcxz", Card(1,10), Card(1,8))
    print(hand.has(PokerHand.PAIR))
    hand = PokerHand(Card(1,12), Card(0,12), Card(3,1), Card(2,3), "sdfsdfsdf",
                        Card(1,5), Card(2,6), Card(3,7), Card(2,4))
    print(hand)
    print(repr(hand))
    hand.clear() # test clearing the hand
    hand.add_card(Card(1,12))
    hand.add_card(Card(1,11))
    hand.add_card(Card(1,10))
    hand.add_card(Card(1,8))
    hand.add_card(Card(1,9))
    hand.add_card(Card(1,7))
    hand.add_card(Card(1,6))
    hand.classify() # test classify()
    print(hand.has(-1))
    print(hand.has("sdfdsf"))
    print(hand.has(PokerHand.HIGH_CARD)) # test wrong hand
    print(hand.has(PokerHand.STRAIGHT_FLUSH)) # test right hand
    hand2 = PokerHand(Card(2,12), Card(2,2), Card(2,11), Card(2,10),
                        Card(2,5), Card(2,8), Card(1,7))
    # test comparison operators
    print("== :", hand == hand2)
    print("!= :", hand != hand2)
    print("<  :", hand < hand2)
    print("<= :", hand <= hand2)
    print(">  :", hand > hand2)
    print(">= :", hand >= hand2)
    print(hand.compare(hand2)) # test compare()

    return 0

def _description(hand):
    """Get string description of hand.

    hand: list of Card, the hand itself

    return: str, the string description of the hand
    """
    desc = ''
    for card in hand: # iterate over hand and store its description
        desc += f"{str(card) + ',':{CARD_DESC_WIDTH + 1}} "

    return desc

# maximum width of a card description
CARD_DESC_WIDTH = len(max(Card.rank_names[1:], key = len)) + \
                  len(Card.QUALIFIER) + \
                  len(max(Card.suit_names, key = len))

def _compare_eq(cards, other_cards):
    """Iterate over the cards from different hands and compare if they have the same rank.

    cards      : list of Card, list of cards of the hand
    other_cards: list of Card, list of cards of the other hand

    return: bool, True if cards from different hands have the same rank
    """
    for card, other_card in zip(cards, other_cards):
        if card.rank != other_card.rank: # if card ranks are different, hands are different
            return False

    return True

def _compare_lt(cards, other_cards):
    """Compare cards from two hands based on rank and 'less than' operator.

    cards      : list of Card, list of cards of one hand
    other_cards: list of Card, list of cards of the other hand

    return: None or bool, True if cards are smaller, False if greater and None if equal
    """
    for card, other_card in zip(cards, other_cards):
        if card.rank != 1 and (card.rank < other_card.rank or other_card.rank == 1):
            return True
        if other_card.rank != 1 and (card.rank > other_card.rank or card.rank == 1):
            return False

    return None # all cards are equal

if __name__ == '__main__':
    sys.exit(main())
