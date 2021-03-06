# Functions to create training datasets

import punmaker
import csv
import random

def get_list(name):
    with open('lists/'+name+'.txt') as f:
        items = [line.rstrip('\n') for line in f]
    return items

def write_training_data(data, file):
    with open(file, 'w+') as f:
        keys = ['str1', 'str2', 'pun', 'result', 'puntype', 'pct_overlap', 'swscore', 'short_strlen', 'long_strlen']
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

        # randomize order of items
        if random.randrange(2) == 0:
            l1 = list1
            l2 = list2
        else:
            l1 = list2
            l2 = list1

        breakfast1 = random.choice(l1)
        president1 = random.choice(l2)
        p1 = punmaker.Portmanteauer(breakfast1, president1, params).makePortmanteau()

        breakfast2 = random.choice(l1)
        president2 = random.choice(l2)
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

    write_training_data(training_data, output_file)
    print "all done!"
    return training_data

