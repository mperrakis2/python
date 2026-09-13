# python

Exercises I wrote while learning Python, mostly from *Think Python* by Allen Downey, plus two programs of my own that go well beyond the exercises: **poker_hand.py** and **poker_stats.py**.

> **If you've come here from my CV:** read [poker_hand.py and poker_stats.py](#the-poker-programs). The first classifies a poker hand of 5 to 7 cards and compares two hands; the second measures poker probabilities by simulation, and its results match the published figures to three decimal places. Together they're about 1,200 lines covering inheritance, operator overloading, the data model, `argparse` and performance tuning. The rest of the repository is book exercises.

## The poker programs

### poker_hand.py — classifying a hand

`PokerHand` extends the `Hand` class from `card.py` and works out the best poker hand in 5 to 7 cards: straight flush, four of a kind, full house, flush, straight, three of a kind, two pair, pair or high card. It also finds the kickers, which it calls the rest of the hand, so that hand plus rest always comes to five cards.

It relies on two ideas that keep the work small. Cards are bucketed into dictionaries by suit and by rank, so a flush or a pair is a matter of bucket sizes rather than combinations. And a straight is found by checking whether a card five places down the sorted list is four ranks lower, which takes at most three comparisons in a seven-card hand. Aces work at both ends, so A-K-Q-J-10 and A-2-3-4-5 are both straights.

Because it implements the Python data model, a hand behaves like a built-in object:

```python
from card import Card
from poker_hand import PokerHand

hand  = PokerHand(Card(1,12), Card(1,11), Card(1,10), Card(1,9), Card(1,8))
other = PokerHand(Card(2,12), Card(2,11), Card(2,10), Card(2,8), Card(2,5))

hand.has(PokerHand.STRAIGHT_FLUSH)   # True
hand > other                         # True
print(hand)                          # readable description of the hand
print(hand.compare(other))           # both hands side by side, and the winner
len(hand), list(hand), hand[0]       # __len__, __iter__, __getitem__
```

`__eq__` and `__lt__` compare by hand type first, then by card rank, then by the kickers, and return `NotImplemented` rather than a wrong answer when a hand is incomplete. Running the file directly (`python poker_hand.py`) runs a demonstration that also exercises the error handling.

### poker_stats.py — probabilities by simulation

`PokerStats` deals random hands, classifies each one with `PokerHand` and builds a histogram of how often each hand type comes up. One shuffled deck supplies several hands, so a 52-card deck yields seven 7-card hands per shuffle.

```bash
python poker_stats.py                    # 10,000 iterations of 7 hands, 7 cards each
python poker_stats.py -i 100000 -c 5     # 100,000 iterations, 5 cards per hand
python poker_stats.py -i 10000 -r 10     # repeat 10 times and report the average time
```

| Option | Description |
|---|---|
| `-i`, `--iterations` *n* | Number of iterations, each dealing one shuffled deck (default 10,000) |
| `-c`, `--cards` *n* | Cards per hand, 5 to 7 (default 7) |
| `-r`, `--repeat` *n* | Repeat the run and report the average time, via `timeit`, for performance testing (default 1) |

Sample output:

```text
cards per hand = 7
hands per deck = 7     , (52 / 7 = cards per deck / cards per hand)
iterations     = 10,000
samples        = 70,000, (7 * 10,000 = hands per deck * iterations)

high card      : 11,966 ->  17.094%
pair           : 30,716 ->  43.880%
two pair       : 16,508 ->  23.583%
three of a kind:  3,468 ->   4.954%
straight       :  3,251 ->   4.644%
flush          :  2,189 ->   3.127%
full house     :  1,773 ->   2.533%
four of a kind :    106 ->   0.151%
straight flush :     23 ->   0.033%
```

The point of a simulation is that you can check it. Over a million 5-card hands, the measured frequencies agree with the exact probabilities, which is a good end-to-end test of the classifier:

| Hand | Measured | Exact |
|---|---|---|
| High card | 50.063% | 50.118% |
| Pair | 42.344% | 42.257% |
| Two pair | 4.702% | 4.754% |
| Three of a kind | 2.126% | 2.113% |
| Straight | 0.402% | 0.392% |
| Flush | 0.195% | 0.197% |
| Full house | 0.142% | 0.144% |
| Four of a kind | 0.027% | 0.024% |
| Straight flush | 0.0014% | 0.0014% |

Two other things the class does. `classify(normal_flow=False)` turns off the work that only matters when a human is reading the result, such as deep-copying the cards and building labels, which is what makes a million-hand run practical. And two `PokerStats` objects can be added with `+` to pool their histograms, but only when the runs used the same settings, so results that aren't comparable can't be merged by accident.

## Requirements

Python 3.10 or later, for the `match` statement. Standard library only, with no third-party packages.

## Where to start reading

| Where | What it shows |
|---|---|
| `classify` and `__suit` in `poker_hand.py` | The bucketing approach, and straight detection in a few comparisons |
| `__lt__` and `__rest` in `poker_hand.py` | Ranking two hands of the same type, down to the kickers |
| `__generate` in `poker_stats.py` | The simulation loop, and reusing one deck for several hands |
| `AdderWithRefCount` in `utility.py` | An abstract base class that gives a subclass `+`, `+=` and reference counting |

## The rest of the repository

Exercises from *Think Python*, most of them from the later chapters on data structures, files and objects:

- **Words and text:** anagram finding, with a `shelve` database version and unit tests (`anagram.py`, `anagram_db.py`, `anagram_db_test.py`); reducible words (`reducible.py`); word-frequency ranking and Zipf's law (`rank.py`); character frequencies (`frequency.py`); Markov-chain text generation (`markov.py`)
- **Files:** a re-implementation of `os.walk` (`directory.py`); finding duplicate files by MD5 (`same_files.py`)
- **Simulation and maths:** the birthday problem (`birthday.py`); a prime sieve (`prime_numbers.py`)
- **Other:** tic-tac-toe against the computer (`tic_tac_toe.py`); printing the exception hierarchy (`all_exceptions.py`)
- **Shared code:** `utility.py`, with the abstract base class above plus helpers for binary search, palindromes and file comparison

The `.txt` files are the word lists and sample texts these exercises read.

## Attribution

`card.py` is by Allen Downey, from *Think Python*, 2nd edition, and is licensed under [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/). I modified it: an `__repr__` for `Card`, a `QUALIFIER` constant, and f-strings in `__str__`. Everything else in this repository is my own work.

## Author

Markos Perrakis — [github.com/mperrakis2](https://github.com/mperrakis2)
