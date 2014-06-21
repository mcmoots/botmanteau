botmanteau
==========

Botmanteau assembles puns. Do you need an exhaustive list of all the breakfast presidents, from Porridge Washington on?
Botmeanteau is the bot for you.

Except for the part where it doesn't really work yet and the code is a mess. Sorry.

Here is my approach though:
* Use the Smith-Waterman algorithm to find local alignment for two phoneme lists (obtained from CMU dictionary)
* Substitution penalties are currently completely arbitrary and made up by me
* Use a list of possible spellings for each phoneme to guess where the input strings should be spliced together

To-dos:
* Add initials to the spelling routine
* Store training/test data in less model-dependent form (str1, str2, pun, win/lose) and recalculate the scores each time
* Proper scikit-learn pipeline
* Amass enough training data to learn a substitution matrix?
* Format incl. metadata for the content lists
* Twitterbot routines:
    * Pick 2 lists, find top N puns, dole out over course of ~ a day, repeat
    * Retweet anyone using that day's hashtag