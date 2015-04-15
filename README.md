# An AEG-style dice rolling and odds calculator

This is a simple command-line tool for

* simulating die rolls in AEG's roll-and-keep system, including variant rolls
  representing skills with *mastery* or *emphasis*, and

* calculating the odds of success for any of those rolls.


# Usage

Running the script shows a prompt, ``(roll)``, after which you can type a roll
in AEG's standard notation:

    (roll) 7k5
 
      36: 10 + 1, 7, 7, 6, 5 <<<>>> 4, 4

This shows that seven dice were rolled, one "exploded," and the total of the
highest five was 36. If you're curious about the odds of hitting various TN
values, use ``prob``:

    (roll) prob 7k5

      TN:  15   20   25   30   35   40   45   50   55   60   65   70   75   80  
       %: 100%  99%  93%  79%  59%  39%  24%  13%  7%   4%   2%   1%   0%   0%

You can simulate variant rules, e.g. rolls of skills with an applicable 
emphasis, by changing the notation slightly:

    (roll) 7k5e

      46: 1 -> 10 + 8, 9, 8, 6, 5 <<<>>> 3, 1 -> 1

This shows that, of seven dice rolled, two came up with ones, and each was
rerolled once. You can also see the odds for variant rolls:

    (roll) prob 7k5e

      TN:  20   25   30   35   40   45   50   55   60   65   70   75   80   85  
       %: 100%  97%  87%  68%  46%  29%  17%  9%   5%   2%   1%   1%   0%   0% 

Type ``help`` or ``help advanced`` at the prompt for a description of all 
options.
