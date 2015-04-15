Simulate, and calculate odds for, AEG-style roll-and-keep dice rolling.

An example of use (and the built-in help):
<pre>
(roll) 7k5<br>
<br>
36: 10 + 1, 7, 7, 6, 5 <<<>>> 4, 4<br>
<br>
(roll) 7k5m<br>
<br>
57: 9 + 10 + 5, 10 + 5, 8, 6, 4 <<<>>> 2, 2<br>
<br>
(roll) prob 7k5<br>
<br>
TN:  15   20   25   30   35   40   45   50   55   60   65   70   75   80<br>
%: 100%  99%  93%  79%  59%  39%  24%  13%  7%   4%   2%   1%   0%   0%<br>
<br>
(roll) prob 7k5m<br>
<br>
TN:  15   20   25   30   35   40   45   50   55   60   65   70   75   80<br>
%: 100%  99%  94%  84%  70%  55%  41%  29%  20%  13%  8%   5%   3%   2%<br>
<br>
(roll) help<br>
<br>
Enter the typical L5R roll format at the (roll) prompt.  For example:<br>
<br>
(roll) 6k3<br>
28 : 10 + 8, 5, 5 <<<>>> 4, 3, 1<br>
<br>
Kept rolls are shown on the left, unkept rolls are shown on the right.<br>
"Exploding" dice are handled automatically.  You can use the up and down<br>
keys to cycle through previous rolls.<br>
<br>
Enter 'prob' before a roll to display the probability of beating (i.e.,<br>
rolling equal to or higher) a range of TN numbers:<br>
<br>
(roll) prob 6k3<br>
TN:  10   15   20   25   30   35   40   45   50   55   60<br>
%: 100%  97%  82%  52%  31%  16%  8%   3%   2%   1%   0%<br>
<br>
Type 'help advanced' for more options.<br>
<br>
(roll) help advanced<br>
<br>
Change the type of a roll by adding a 'u', 'm', or 'e' after the roll.<br>
Some example roll types and how they work:<br>
<br>
6k3    -- the default roll, dice explode on 10<br>
6k3u   -- (u)nskilled, dice do not explode<br>
6k3m   -- (m)astery, dice explode on 9 or 10<br>
6k3e   -- (e)mphasis, reroll a one, once, before any explosions<br>
<br>
You can also add or subtract a modifier by adding "+ [mod]" or "- [mod]"<br>
after a roll.  Here is an example of an 8k4 roll, with an extra +7<br>
modifier, and with emphasis:<br>
<br>
(roll) 8k4e + 7<br>
45: 1 -> 10 + 6, 9, 7, 6 [+7] <<<>>> 5, 4, 3, 2<br>
<br>
Roll types and modifiers can also be used when displaying probabilities.<br>
<br>
Rolls of more than 10 dice are reformulated as smaller rolls with static<br>
bonus.  Add a 'b' to the end of a roll to disable this behavior.<br>
</pre>