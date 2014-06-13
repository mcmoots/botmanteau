botmanteau
==========

Botmanteau assembles puns. Do you need an exhaustive list of all the breakfast presidents, from Porridge Washington on?
Botmeanteau is the bot for you.

Except for the part where it doesn't really work yet and the code is a mess. Sorry.

Here is my approach though:
* Use the Smith-Waterman algorithm to find local alignment for two phoneme lists (obtained from CMU dictionary)
* Substitution penalties are currently completely arbitrary and made up by me
* Use a list of possible spellings for each phoneme to guess where the input strings should be spliced together

Some to-dos:
* Add initials to the spelling routine
* Reorganize functions
* Figure out a scoring system & score threshold for the results
* Have it loop through 2 lists to find the puns, start hashtag games on Twitter