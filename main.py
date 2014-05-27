# Portmanteau punning algorithm.

# needs to take 2 strings and:
#   convert to phonetic representation (CMU pronouncing dict + ???)
#   calculate "match" score between 2 phoneme strings at given loc.
#   return top-scoring match with the overlap substituted
#       - which term "wins" in this? the shorter one?
#   identify the point in the strings corresponding to the phonemic overlap
#       and construct appropriately overlapped string

# Easy test case: Eggsbraham Lincoln? Porridge Washington?

import punmaker
import csv
import random


with open('lists/test.txt') as f:
    tests = [line.rstrip('\n') for line in f]
with open('lists/examples.txt') as f:
    examples = [line.rstrip('\n') for line in f]


def get_ynq_input(prompt):
    ans = raw_input(prompt)
    while ans not in ['y', 'n', 'q']:
        ans = raw_input('y/n (or q to quit) ')
    return ans


def write_training_data_to_file(data, file):
    with open(file, 'w+') as f:
        keys = ['pun', 'len_ph_1', 'len_ph_2', 'len_str_1', 'len_str_2',
                'puntype', 'pct_overlap', 'swscore', 'result']
        datawriter = csv.DictWriter(f, keys)
        datawriter.writer.writerow(keys)
        datawriter.writerows(data)
    return 0

def get_123_input(prompt):
    ans = raw_input(prompt)
    while ans not in ['1', '2', '3', 'q']:
        ans = raw_input('1, 2, 3 or q to quit')
    return ans

def gather_forced_comparisons(list1, list2, iterations, output_file):
    params = punmaker.PhonemeDictset()
    training_data = []

    iters = 0

    while iters < iterations:
        breakfast1 = random.choice(list1)
        president1 = random.choice(list2)
        p1 = punmaker.Portmanteauer(breakfast1, president1, params).makePortmanteau()

        breakfast2 = random.choice(list1)
        president2 = random.choice(list2)
        p2 = punmaker.Portmanteauer(breakfast2, president2, params).makePortmanteau()

        if p1 is None or p2 is None:
            continue

        pun1 = '1. ' + breakfast1 + ' + ' + president1 + ' = ' + p1['pun']
        pun2 = '2. ' + breakfast2 + ' + ' + president2 + ' = ' + p2['pun']
        pun_choice = get_123_input( pun1 + '\n' + pun2 + '\n 3. these are both terrible?')

        if pun_choice == 'q':
            print "Ok, enough."
            write_training_data_to_file(training_data, output_file)
            return training_data
        elif pun_choice == '1':
            p1['result'] = 'w'
            p2['result'] = 'l'
        elif pun_choice == '2':
            p1['result'] = 'l'
            p2['result'] = 'w'
        elif pun_choice == '3':
            p1['result'] = 'l'
            p2['result'] = 'l'
        else:
            print "WTF!" + pun_choice
            return 2

        training_data.append(p1)
        training_data.append(p2)

        iters += 1

    write_training_data_to_file(training_data, output_file)
    print "all done!"
    return training_data






