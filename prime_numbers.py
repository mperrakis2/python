"""This module calculates prime numbers up to a number entered by the user.

To calculate prime numbers up to a number we need to eliminate all the multiples of the numbers that
are not greater than the square root of the number.

For example, take the sequence 2,3,4,5,6,7,...,20. The nearest square root of 20 is 4,
as 5 ** 2 = 25 > 20

So, starting with number 2, use the first 3 numbers, i.e. 2,3,4, and eliminate all their multiples,
which are non-primes, in the following order:

Step 1. 2*2, 2*3, 2*4, 2*5, 2*6, 2*7, 2*8, 2*9, 2*10
Step 2. 3*3, 3*4, 3*5, 3*6
        (Note that 3*2 = 2*3, 3*4 = 2*6, 3*6 = 2*9 and thus have been eliminated in step 1)
Step 3. 4*4, 4*5
        (Note that 4*4 = 2*8, 4*5 = 2*10 and thus have been eliminated in step 1)

Graphically, 2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
             x   x   x x  x     x     x  x  x     x     x  (x: non-primes that are eliminated)

             2,3,  5,  7,       11,   13,         17,   19 (primes up to 20)
"""
import sys
import argparse

def main():
    """Main entry point.

    return: int, success or failure
    """
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter,
                                     description = "display prime numbers up to a number entered "
                                                   "by the user")
    parser.add_argument('number', type = int,
                        help = "display prime numbers up to this number, must be > 1")
    args  = parser.parse_args()

    if args.number < 2:
        sys.exit("error: integer > 1 required")

    for i, is_prime in enumerate(primes(args.number)):
        if is_prime:
            print(i, end = " ")
    print()

    #print(primes_slow(num)) # much slower than primes(num)

    return 0

def primes(limit):
    """Calculate prime numbers up to the limit passed in as a parameter.

    Based on the module comments, for a limit of 20, the number of outer iterations is
    int(20 ** 0.5) - 1 = 3 and in general, int(limit ** 0.5) - 1. Again, based on the module
    comments, for a limit of 20, the number of inner iterations is:

    outer iteration 1: (20 // 2) - 1 = 9 <- num of inner iterations
    outer iteration 2: (20 // 3) - 2 = 4 ---------- ditto ---------
    outer iteration 3: (20 // 4) - 3 = 2 ---------- ditto ---------

    and in general: (limit // num) - (num - 1) = (limit // num) - num + 1

    limit: int, calculate prime numbers up to this number

    return: list of bool, list has size of limit. List indices represent all numbers up to limit.
                          List elements of non-prime indices are set to False, all others to true.
    """
    _param_error(limit) # validate limit

    nums = [False, False] # 0 and 1 are not prime numbers
    nums.extend([True for i in range(limit - 1)])

    # As per the docstring, the number of outer iterations is int(limit ** 0.5) - 1.
    #
    # Therefore, the iterable is range(0, int(limit ** 0.5) - 1) or
    #                            range(2, int(limit ** 0.5) + 1)
    for i in range(2, int(limit ** 0.5) + 1):
        if nums[i]: # needed, as elements with non-prime indices are set to False below

            # As per the docstring, the number of inner iterations is (limit // i) - i + 1
            #
            # Therefore, the iterable is range(0, limit // i - i + 1) or
            #                            range(i, limit // i + 1)
            for j in range(i, limit // i + 1):
                index = i * j   # index of non-prime number
                if nums[index]: # set element of non-prime index to False if not set already
                    nums[index] = False

    return nums

def primes_slow(limit):
    """Calculate prime numbers up to the limit passed in as a parameter.

    limit: int, calculate prime numbers up to this number

    return: list of int, list of prime numbers
    """
    _param_error(limit) # validate limit

    prime_nums = []
    for num in range(2, limit):
        prime = True
        for i in range(2, num):
            if i > int(num ** 0.5): # see comments at the beginning of the module
                break
            if num % i == 0: # not a prime
                prime = False
                break

        if prime:
            prime_nums.append(num)

    return prime_nums

def _param_error(limit):
    """Validate parameters.

    limit: int

    exceptions: TypeError , if limit not of type int
                ValueError, if limit < 2
    """
    if not isinstance(limit, int):
        raise TypeError("error: 'limit' has to be of type 'int'")
    if limit < 2:
        raise ValueError("error: 'limit' must be > 1")

if __name__ == '__main__':
    sys.exit(main())
