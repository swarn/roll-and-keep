# roll.py: simulate and calculate odds for roll-and-keep dice rolling
# Copyright (C) 2012, Seth Warn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Roll-and-Keep is a trademark of Alderac Entertainment Group

import cmd
import random
import re
from functools import lru_cache, partial
from math import factorial

random.seed()


help_text = """
    Enter the typical L5R roll format at the (roll) prompt.  For example:

      (roll) 6k3
        28 : 10 + 8, 5, 5 <<<>>> 4, 3, 1

    Kept rolls are shown on the left, unkept rolls are shown on the right.
    "Exploding" dice are handled automatically.  You can use the up and down
    keys to cycle through previous rolls.

    Enter 'prob' before a roll to display the probability of beating (i.e.,
    rolling equal to or higher) a range of TN numbers:

        (roll) prob 6k3
          TN:  10   15   20   25   30   35   40   45   50   55   60
           %: 100%  97%  82%  52%  31%  16%  8%   3%   2%   1%   0%

    Type 'help advanced' for more options.
"""

advanced_text = """
    Change the type of a roll by adding a 'u', 'm', or 'e' after the roll.
    Some example roll types and how they work:

        6k3    -- the default roll, dice explode on 10
        6k3u   -- (u)nskilled, dice do not explode
        6k3m   -- (m)astery, dice explode on 9 or 10
        6k3e   -- (e)mphasis, reroll a one, once, before any explosions
        6k3em  -- combine emphasis and mastery

    You can also add or subtract a modifier by adding "+ [mod]" or "- [mod]"
    after a roll.  Here is an example of an 8k4 roll, with an extra +7
    modifier, and with emphasis:

        (roll) 8k4e + 7
          45: 1 -> 10 + 6, 9, 7, 6 [+7] <<<>>> 5, 4, 3, 2

    Roll types and modifiers can also be used when displaying probabilities.

    Rolls of more than 10 dice are reformulated as smaller rolls with static
    bonus.  Add a 'b' to the end of a roll to disable this behavior.
"""


class CommandLoop(cmd.Cmd, object):
    prompt = "(roll) "
    intro = """
    L5R Dice Rolling: type 'help' for options
    """

    def do_help(self, s):
        if s == "advanced":
            print(advanced_text)
        else:
            print(help_text)

    def default(self, s):
        opts = parse_input(s)
        if opts:
            throw(*opts)
        else:
            print("\n  *** invalid input string ***\n")

    def emptyline(self):
        pass

    def do_prob(self, s):
        opts = parse_input(s)
        if opts:
            show_prob(*opts)
        else:
            print("\n  *** invalid input string ***\n")

    def do_EOF(self, _):
        print()
        return True

    def do_quit(self, _):
        return True

    do_exit = do_quit


def main():
    interpreter = CommandLoop()
    interpreter.cmdloop()


def parse_input(in_string):
    """
    Extract throw parameters from a string.

    Returns a tuple (r, k, mods, add) where
      r:    number of dice to roll
      k:    number of dice to keep
      mods: variants of roll mechanics, chars from [ume]
      add:  static bonus/penalty to roll
    """
    regex = re.compile(
        r"""
        (\d+)k(\d+)             # dice to roll and keep
        ([mue]*)?               # optional kind
        (\s*[+-]\s*\d+)?        # optional modifier
        (\s*b\s*)?              # optional uncapped roll
        \s*$                    # and nothing else
        """,
        re.VERBOSE,
    )

    m = regex.match(in_string)
    if not m:
        return

    p = m.groups()

    r, k = int(p[0]), int(p[1])
    mods = "" if not p[2] else p[2]
    mods = "em" if mods == "me" else mods
    if "u" in mods and "m" in mods:
        return
    add = 0 if not p[3] else int(re.sub(r"\s+", "", p[3]))
    capped = not p[4]

    # if the roll is capped (the default), call the cap function and print
    # a notification if it modified the throw parameters.
    if capped:
        r_new, k_new, add_new = cap(r, k, add)
        if r_new != r or k_new != k:
            old = show_par(r, k, add)
            new = show_par(r_new, k_new, add_new)
            print("\n  {0} ==> {1}".format(old, new))
            r, k, add = r_new, k_new, add_new

    return r, k, mods, add


def show_par(r, k, mod):
    """Returns string describing throw parameters."""
    if mod == 0:
        return f"{r}k{k}"

    return f"{r}k{k} {'+' if mod > 0 else '-'} {abs(mod)}"


def cap(r, k, add):
    """
    Convert excessively large numbers of thrown dice to flat bonuses.

    The roll-and-keep rules suggest a maximum of 10 dice be rolled. Every two
    rolled dice above 10 are converted to a single kept dice. Once there are
    10 kept dice, any additional unkept or kept dice are converted into a
    flat +2 bonus.
    """
    # convert rolled to kept dice at 2:1 ratio
    while r > 11 and k < 10:
        r -= 2
        k += 1

    # additional rolled or kept over 10 become a static +2 bonus
    if r > 10:
        add += 2 * (r - 10)
        r = 10
    if k > 10:
        add += 2 * (k - 10)
        k = 10

    return r, k, add


########## Dice Rolling ##########

# In the following code, various terms have specific meaning:
#
#   Die (or dice): the result of a single d10 being rolled, resulting
#       in a number from 1 to 10.
#
#   Roll: The L5R-style rolling of dice, where a d10 is rolled, and if
#       the result is 10, roll again and add the result (called
#       "exploding") until getting a result other than 10.
#
#   Kind: Variations on how to roll.  The standard roll is described
#       above.  The mastery roll explodes on 9 or 10.  The unskilled
#       roll doesn't explode.  The empahsis roll rerolls if the first
#       die is 1.
#
#   Throw: Rolling some number of times, and summing the result of
#       highest rolls.


def d10():
    return random.randint(1, 10)


def roll(mods):
    """
    Perform a single, L5R-style die roll of the given kind.

    mods: a string containing a subset of 'emu', which change the rules of
    the roll as described above.

    returns a tuple: (result, (string representing roll sequence))
    """
    expertise = "e" in mods
    explode = 10
    if "m" in mods:
        explode = 9
    elif "u" in mods:
        explode = 11

    dice = [d10()]
    sequence = ""

    if expertise and dice[0] == 1:
        sequence = "1 -> "
        dice = [d10()]

    while dice[-1] >= explode:
        dice.append(d10())

    result = sum(dice)
    sequence += " + ".join(str(die) for die in dice)
    return result, sequence


def throw(r, k, mods, add):
    """Print a single throw with the given kind and modifier."""
    rolls = [roll(mods) for _ in range(r)]
    rolls.sort(reverse=True)
    high_rolls, low_rolls = rolls[:k], rolls[k:]

    result = "{0}: ".format(sum(r for r, _ in high_rolls) + add)
    kept = ", ".join(s for _, s in high_rolls)
    bonus = "" if add == 0 else " [{0:+}]".format(add)
    unkept = ""
    if low_rolls:
        unkept = " <<<>>> " + ", ".join(s for _, s in low_rolls)

    print("\n  " + result + kept + bonus + unkept + "\n")


def show_prob(r, k, kind, mod):
    """Print a table of probabilites for the given throw"""
    # Start the table at the first TN less than 99.9% likely to succeed
    min_TN = 5 - mod
    while throw_v_or_up(r, k, min_TN, kind) > 0.999:
        min_TN += 5

    # Calculate the probabilites for 14 TN values
    TNs = [min_TN + i * 5 for i in range(14)]
    probs = [throw_v_or_up(r, k, TN, kind) for TN in TNs]

    tn_line = " TN: " + "".join("{0:^5}".format(TN + mod) for TN in TNs)
    prob_line = "   %: " + "".join("{0:^5.0%}".format(p) for p in probs)
    print("\n", tn_line)
    print(prob_line, "\n")


########## Calculating Probabilities ##########


@lru_cache(maxsize=None)
def C(n, r):
    """Return the number of combinations of n objects taken r at a time"""
    return factorial(n) / (factorial(r) * factorial(n - r))


def F(n):
    """Return the chance of getting n on a single die"""
    if n < 1 or n > 10:
        return 0.0
    else:
        return 0.1


@lru_cache(maxsize=None)
def standard(n):
    """Return the chance of getting n on a standard roll"""
    if n < 10:
        return F(n)
    else:
        return F(10) * standard(n - 10)


@lru_cache(maxsize=None)
def mastery(n):
    """Return the chance of getting n on a roll with mastery

    For this type of roll, die "explode" on a both 9 and 10.
    """
    if n < 9:
        return F(n)
    else:
        return F(9) * mastery(n - 9) + F(10) * mastery(n - 10)


@lru_cache(maxsize=None)
def emphasis(n, D):
    """Return the chance of getting n on a roll of kind D with emphasis.

    For this type of roll, if the first die comes up 1, then it is
    rerolled.  All further 1's are not rerolled.
    """
    if n == 1:
        return F(1) * F(1)
    else:
        return D(n) + F(1) * D(n)


@lru_cache(maxsize=None)
def P(r, k, v, t, D):
    """Calculate throw probability with a number of constraints

    Given roll r, keep k, what is the chance that the result of the throw
    is v and that all rolls are t or less? D is the PDF of the roll.
    """
    # There's no chance of throwing less than one

    if r < 1 or k < 1 or v < 1 or t < 1:
        return D(0)

    # The chance of throwing v when all the rolls are t or less includes
    # the chance of throwing v when all the rolls are t-1 or less.

    acc = P(r, k, v, t - 1, D)

    # Now, add the chance of throwing v when at least one roll is t.
    # First count the throws where there are less than k rolls of t.  For
    # example, on 5k3, this loop would add the chance of rolling t once
    # and the chance of rolling t twice.  The terms are:
    #
    #   C(r,n): The number of ways to get a result, n times, on r rolls
    #
    #   D(t) ** n: The chance of throwing t on n rolls
    #
    #   P(...): The chance that the rest of the rolls add up with the
    #       n rolls of t to get the desired total, v

    for n in range(1, k + 1):
        acc += C(r, n) * (D(t) ** n) * P(r - n, k - n, v - n * t, t - 1, D)

    # Having examined up to k rolls, now consider exactly k rolls of t.
    # This means all kept rolls have a value of t, since t is the the
    # highest rolled value.  This means that for n = k and higher, all
    # throws will have result k * t.  If this value does not match v,
    # then none of these throws will contribute to the chance of throwing
    # v, and the function can return now.

    if k * t != v:
        return acc

    # The value of k * t is equal to v.  This means that the other
    # rolls (the rolls that are not t) can add up to any value, as long
    # as they are all individually less than t.  The terms:
    #
    #   C(r, n): The number of ways to roll n results on r rolls
    #
    #   D(t) ** n: The chance of rolling t on on n rolls
    #
    #   lt_t ** (r-n): The chance of rolling less than t on r rolls

    lt_t = sum(D(i) for i in range(t))
    for n in range(k, r + 1):
        acc += C(r, n) * (D(t) ** n) * (lt_t ** (r - n))

    return acc


@lru_cache(maxsize=None)
def throw_v(r, k, v, mods):
    """Return the probability of getting exactly v for roll r, keep k"""
    pdf = {
        "": standard,
        "u": F,
        "m": mastery,
        "e": partial(emphasis, D=standard),
        "em": partial(emphasis, D=mastery),
    }
    return P(r, k, v, v, pdf[mods])


@lru_cache(maxsize=None)
def throw_v_or_up(r, k, v, mods):
    """Return the probability of getting v or higher for roll r, keep k"""
    return 1 - sum(throw_v(r, k, i, mods) for i in range(1, v))


if __name__ == "__main__":
    main()
