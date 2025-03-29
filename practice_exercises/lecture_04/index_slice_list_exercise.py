"""
Lists exercises
author: Argyriou Thanasis, email: argythana@gmail.com
version: python 3.6.3
encoding: utf-8
date: May 2019
"""

print('Examples')
list_example = ['nikos', 'maria', 'antonis', 'vasilis', 'afroditi']
list_example2 = ['christos', 'antonis', 'manolis']

print(list_example)
print(list_example2)
print()


# 1. Join the two lists in a new one
print('Join lists with + => new list.')
joined_lists = list_example + list_example2 # duplicates allowed in lists
print(joined_lists)
print()


# 2. Find 3rd item of joined list
third_student = joined_lists[2]
print('3rd item of joined list, get with index 2:')
print(joined_lists[2])
print(type(third_student))
print()


# 3. Find the 6th letter of the third item of list_example
letter6_item3 = list_example[2][5]
print('6th letter of the third item, det with index 5 :')
print(list_example[2][5])
print(type(list_example[2][5]))
print()


# 4. Join lists so that second list is a sub-list, but keep first list intact
list_example_copy = list_example.copy()
list_example_copy.append(list_example2) # SOS: no new variable assignment
print('Please remember: when using append(), the second list becomes a single item of first list.')
print(list_example_copy)
#this way the list_example would have been mutated
#list_example.append(list_example2)
# print(list_example) # check mutation
print()


# 5. Convert list items to string separated by : and blank space
print('Join string type items of list and select separating character:')
names_students =': '.join(joined_lists)
print(names_students, '\n')


# 6. Count the number of items in a list:
number_students = len(joined_lists)
print(f'Use len() to get the number of items in list:\n\
e.g. the number os students is {number_students}')
print(number_students)
