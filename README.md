botmanteau
==========

Botmanteau assembles puns. Do you need an exhaustive list of all the breakfast presidents, from Porridge Washington on?
Botmeanteau is the bot for you.

Here is how it works:
* Find local alignment for two phoneme lists (obtained from CMU dictionary) using Smith-Waterman algorithm
* Substitution penalties are currently completely arbitrary and made up by me
* Use a list of possible spellings for each phoneme to guess where the input strings should be spliced together

To-dos:
* Add initials to the spelling routine
* Proper scikit-learn pipeline, more sophisticated modeling (right now the scoring is just logistic regression)
* Amass enough training data to learn a substitution matrix?
* Additional bot behavior, perhaps interacting with other posts to the day's hashtag

Contribute!
-----------

Please please please send pull requests with additional topical lists! I have thought about harvesting these from 
Wikipedia but I think that human curation will keep the topics and items a little more accessible to everyone.