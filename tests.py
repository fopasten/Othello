
__author__ = "Felipe Joaquín Pastén Cáceres"

import timeit
from matplotlib import pyplot as plt

def test_suite(max_n):
    numbers, othello6, othello8 = [], [], [], 
    for i in range(1, max_n+1):
        setup6 = f'''        
from game import Othello

sample_board = [
    ['space', 'space', 'black', 'space', 'space', 'white'],
    ['space', 'space', 'space', 'black', 'white', 'black'],
    ['space', 'space', 'white', 'white', 'black', 'space'],
    ['space', 'white', 'white', 'white', 'black', 'space'],
    ['space', 'white', 'white', 'white', 'space', 'space'],
    ['space', 'white', 'space', 'white', 'space', 'space'],
]
player = Othello('black', 'white', 6, int({i}))
        '''

        setup8 = f'''        
from game import Othello

sample_board = [
    ['space', 'space', 'space', 'space', 'space', 'space', 'space', 'white'],
    ['space', 'space', 'space', 'black', 'space', 'space', 'white', 'space'],
    ['space', 'space', 'space', 'space', 'black', 'white', 'black', 'black'],
    ['space', 'space', 'space', 'white', 'white', 'black', 'space', 'space'],
    ['space', 'space', 'white', 'white', 'white', 'black', 'space', 'space'],
    ['space', 'space', 'white', 'white', 'white', 'space', 'space', 'space'],
    ['space', 'space', 'white', 'space', 'white', 'space', 'space', 'space'],
    ['space', 'space', 'space', 'space', 'space', 'space', 'space', 'space'],
]
player = Othello('black', 'white', 8, int({i}))
        '''
        numbers.append(i)

        othello6.append(timeit.timeit("player.move(sample_board,'black')", setup=setup6, number=1))
        othello8.append(timeit.timeit("player.move(sample_board,'black')", setup=setup8, number=1))

        print(numbers, othello6, othello8)
    return numbers, othello6, othello8

numbers, othello6, othello8 = test_suite(9)

plt.plot(numbers, othello6, 'b', label="Othello 6x6")
plt.plot(numbers, othello8, 'g', label="Othello 8x8")
plt.legend()
plt.show()

# plt.semilogy(numbers, othello6, 'b', label="Othello 6x6")
# plt.semilogy(numbers, othello8, 'g', label="Othello 8x8")
# plt.legend()
# plt.show()

