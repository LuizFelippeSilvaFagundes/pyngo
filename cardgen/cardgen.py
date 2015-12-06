#!/usr/bin/env python
import random
from datetime import datetime

num_lists = []
card_list = []


def print_card(card):
    print "---------------------------"
    for i in range(3):
        for j in range(9):
            print ("%s" % card[j][i]).rjust(2),
        print
    print "---------------------------"


for card_number in range(150):

    repeated_card = False
    while True:
        # Generate numbers from 1 to 90, organized by their column
        columns = []
        for i in range(9):
            if i == 0:
                columns.append([x + 1 for x in range(9)])
            elif i == 8:
                columns.append([i * 10 + x for x in range(11)])
            else:
                columns.append([i * 10 + x for x in range(10)])

        # Init cards in group
        cards = []
        for i in range(6):
            card = [[], [], [], [], [], [], [], [], []]
            cards.append(card)
            # For each card, get at least one number from each column
            for idxcol in range(9):
                number = random.choice(columns[idxcol])
                columns[idxcol].remove(number)
                card[idxcol].append(number)

        unassigned = []
        # Remaining col numbers, assign to random cards
        for i in range(9):
            col = columns[i]
            for numero in col:
                if not unassigned:
                    unassigned.extend(cards)
                while True:
                    card = random.choice(unassigned)
                    # Only allow if less than 2 numbers in that card column
                    if len(card[i]) < 2:
                        unassigned.remove(card)
                        card[i].append(numero)
                        break

        # Sort columns, and generate list of numbers in each card
        for card in cards:
            for col in card:
                col.sort()
            num_list = [num for col in card for num in col]
            if num_list in num_lists:
                repeated_card = True
                break
        if not repeated_card:
            for card in cards:
                num_lists.append([num for col in card for num in col])
            break

            # If there is a repeated card, a new group will be generated

    # Insert random spaces in the cards ,with some conditions
    for card in cards:

        # Generate possible choices, in random order
        col_choices = [[], [], [], [], [], [], [], [], []]
        if len(card[0]) == 1:
            col_choices[0] = [(0, 1), (0, 2), (1, 2)]
        else:
            col_choices[0] = [(0,), (1,), (2,)]
        random.shuffle(col_choices[0])

        i = 0
        while i < 9:
            if not col_choices[i]:
                # no remaining choices, we need to backtrack
                i = i - 1
                # Clear blanks in previous column
                card[i] = [x for x in card[i] if x != '*']
                continue

            col = card[i]

            # Try first choice, and remove it
            idxs = col_choices[i].pop()

            right_elect = True
            for row in idxs:

                # No more than 4 blanks in a row
                total_blanks = 0
                for j in range(i):
                    if card[j][row] == '*':
                        total_blanks += 1
                if total_blanks >= 4:
                    right_elect = False
                    break
                # No more than 2 blanks side by side in a row
                if i >= 2 and card[i - 1][row] == '*' and card[i - 2][row] == '*':
                    right_elect = False
                    break

            if right_elect:
                for idx in idxs:
                    card[i].insert(idx, '*')
                i += 1
                if i < 9:
                    #Prepare random choices for next column
                    if len(card[i]) == 1:
                        col_choices[i] = [(0, 1), (0, 2), (1, 2)]
                    else:
                        col_choices[i] = [(0,), (1,), (2,)]
                    random.shuffle(col_choices[0])

        # Flatten list and save it to card_list
        card_list.append([num for col in card for num in col])

    #Inform progress
    print "cards %d to %d" % (len(num_lists) - 5, len(num_lists))

#     for card in cards:
#         print_card(card)
#         print
#

now = datetime.now()
filename = "cards_" + now.strftime("%Y%m%d%H%M%S") + ".csv"
print filename;
f = open(filename, "w")
f.write("NUM_CARTON\t")
for i in range(9):
    for j in range(3):
        f.write("C%dF%d\t" % (i+1,j+1))
f.write("\n")
for i, c in enumerate(card_list):
     f.write("%s\t" % (i+1))
     for n in c:
         f.write("%s\t" % n)
     f.write("\n")
f.close()

