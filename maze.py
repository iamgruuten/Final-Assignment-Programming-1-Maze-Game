import os
import copy
import json
import hashlib
import time
from collections import deque  # Added for BFS queue
try:
    from sense_hat import SenseHat
    sense = SenseHat()
    isSenseHat = True
except:
    isSenseHat = False

class Board:
    '''
    Board class
    Board class design to manipulate the nested list.
    identifing characters in the maze
    INPUT: Random number of keyword arguments
    Keyword arguments:
        file - String of the filename to be opened
        file -> [['O', 'X', 'X'],['X', 'O', 'O']]
        list - Pass me a already created nested list
        list -> [['O', 'X', 'X'],['X', 'O', 'O']]
    '''
    def __init__(self, **kwargs):
        self.Scount = 0
        self.Ecount = 0
        if 'file' in kwargs:
            with open(kwargs["file"], 'r') as myfile:
                self.list = []
                # Able to read csv and text file
                for row in myfile.readlines():
                    row = row.split(',')
                    row = ''.join(row)
                    self.Scount += row.count('A')
                    self.Ecount += row.count('B')
                   
                    self.list.append(list(row.strip()))
                self.getEnd()
                self.getStart()
               
       
        elif 'list' in kwargs:
            self.list = kwargs['list']
       
        self.orginalList = copy.deepcopy(self.list)

    def __len__(self):
        count = 0
        for x in self.list:
            count += len(x)
        return count

    def uniqueValues(self):
        '''
        uniqueValues() to return all the unique characters from the maze
        '''
        maze = ''
        for x in self.list:
             maze += ''.join(x)
        return sorted(set(maze))

    def getStart(self):
        ''' getStart() return tuple of values of A position E.X (row,column) '''
        for row, col in enumerate(self.list):
                if 'A' in col:
                    self.start = (row, col.index('A'))
                    return (row, col.index('A'))

    def getEnd(self):
        ''' getEnd() return tuple of values of B position E.X (row,column) '''
        for row, col in enumerate(self.list):
                if 'B' in col:
                    self.end = (row, col.index('B'))
                    return (row, col.index('B'))
   
    def reset(self):
        ''' reset() change the maze to when it was first init '''
        self.list = copy.deepcopy(self.orginalList)

    def isAvailable(self, row, col):
        ''' isAvailable(row,col) check if the row col is a wall in the maze
       
        INPUT: row and col is a integer, a position in the nested list
       
        RETURN: True if no wall, False if wall
        '''
        if self.list[row][col] == "X":
            return False
        else:
            return True
   
    def changePostiton(self, row, col, value):
        ''' changePostiton(row,col,value) to change the value at the specific index '''
        self.list[row][col] = value
   
    def digestMaze(self):
        ''' digestMaze is to return the maze hashed using md5 '''
        value = ''
        for x in self.list:
            value += ''.join(x)
            value += '\n'
        return hashlib.md5(value.encode()).hexdigest()

    def workableMaze(self, keys):
         ''' This is designed to correct a STRING of characters to test if the
         maze is able to run
         '''
         prevent = {'W':'S','A':'D','D':'A','S':'W'}
         row, col = self.getStart()
         done = ''
         for key in keys:
         
             di = {"W":(row-1,col),"S":(row+1,col),"A":(row,col-1),"D":(row,col+1)}
             row, col = di[key]
             row, col = row % len(self.list), col % len(self.list[0])
           
             if self.list[row][col] == "X":
                return (False, (row, col))
             if done == prevent[key]:
                return (False, (row, col))
             done = key
         return (True, (row, col))

    def config(self, value, row, col):
        ''' config(value,row,col) to change the position of the
        maze and then changing it on the original maze
       
        INPUT:
        value -> A string that you want the maze with usually A,B,O and X
        row -> A string which is a number to direct which row on the list
        col -> A string which is a number to identify which position of the list
        '''
        self.list[int(row)][int(col)] = value
        self.orginalList = copy.deepcopy(self.list)

    # New method: BFS to find shortest path
    def find_shortest_path(self):
        ''' find_shortest_path() uses BFS to find the shortest sequence of moves from start to end.
        Accounts for wrapping (toroidal maze). Returns list of moves (e.g., ['D', 'S']) or None if no path. '''
        start = self.getStart()
        end = self.getEnd()
        if not start or not end:
            return None

        rows, cols = len(self.list), len(self.list[0])
        directions = [(-1, 0, 'W'), (1, 0, 'S'), (0, -1, 'A'), (0, 1, 'D')]  # Up, Down, Left, Right with move chars

        queue = deque([(start, [])])  # (position, path_moves)
        visited = set([start])

        while queue:
            (row, col), path = queue.popleft()
            if (row, col) == end:
                return path  # Shortest path found (list of moves)

            for dr, dc, move in directions:
                nr = (row + dr) % rows
                nc = (col + dc) % cols
                if self.list[nr][nc] != 'X' and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [move]))

        return None  # No path found

class LeaderBoard:
    '''
    LeaderBoard class
    leaderboard class was design to control the leader file to get and set it
    INPUT: A hashed maze for unique key
    '''
    def read(self):
       
        with open(self.filename, 'r') as f:
            self.data = json.load(f)
   
    def __init__(self, hashedMaze):
        self.currentPath = os.path.dirname(os.path.abspath(__file__))
        self.filename = self.currentPath + '/' + 'data.json'
        # To check if the file exists if doesn't it create
        if 'data.json' in os.listdir(path=self.currentPath):
            self.read()
        else:
            with open(self.filename, 'w+') as f:
                f.write('{"Maze": {}}')
            self.read()
          
        self.hashedMaze = hashedMaze
        self.leaderboardExist = str(self.hashedMaze) in self.data['Maze']
        if not self.leaderboardExist:
            self.update()
   
    def getLeaderBoard(self):
        # Get the leaderboard
        return self.data['Maze'][str(self.hashedMaze)]
   
    def update(self):
        # Add the unique maze id into the dictionary
        self.data['Maze'].update({str(self.hashedMaze):[]})

    def append(self, name, score):
        # Add the values name and score based on the Maze Id
        self.data['Maze'][self.hashedMaze].append([name, score])
       
    def writeLeaderBoard(self):
        # Write all the information into data.json
        with open(self.filename, 'w') as outfile:
            json.dump(self.data, outfile)
        self.read()

class Rashpi:
 
    x = 0
    y = 0
    def _decode_(move):
        def magic(self):
            sense.set_pixel(self.y, self.x, self.nothing)
            move(self)
            sense.set_pixel(self.y, self.x, self.red)
        return magic

    def PixelList(self):
        ''' Converting the maze nested list into a list
        with colour code
        '''
        piList = []
        for maze in self.board.list:
            for x in maze:
                if x == "X":
                    G = self.grey
                    piList.append(G)
                elif x == 'A':
                    R = self.red
                    piList.append(R)
                   
                elif x == 'B':
                    G = self.green
                    piList.append(G)
                   
                else:
                    n = self.nothing
                    piList.append(n)
        return piList

    def __init__(self, board):
        sense.low_light = True
        self.red = (255, 0, 0)
        self.nothing = (0, 0, 0)
        self.green = (0, 255, 0)
        self.grey = (225, 225, 225)
        self.x = board.getStart()[0]
        self.y = board.getStart()[1]
        self.end = board.getEnd()
        self.board = board
        lst = self.PixelList()
        sense.set_pixels(lst)

    def isAvailable(self, key):
        row, col = self.x, self.y
        dic = {"up":(row - 1, col), "down":(row + 1, col), "left":(row, col - 1), "right":(row, col + 1), "middle":(row, col)}
        row, col = dic[key]
       
        if self.board.list[row][col] == 'X':
            return False
        else:
            return True
   
    @_decode_
    def moveUp(self):
        self.x = (self.x - 1) % 8
       
    @_decode_
    def moveDown(self):
        self.x = (self.x + 1) % 8
       
    @_decode_
    def moveLeft(self):
        self.y = (self.y - 1) % 8
       
       
    @_decode_
    def moveRight(self):
        self.y = (self.y + 1) % 8
       
    @_decode_
    def middle(self):
       pass

    def isWin(self):
        return True if (self.x, self.y) == self.end else False

# New class: Player to encapsulate player position and movement (OOP improvement)
class Player:
    def __init__(self, position):
        ''' Initialize player with starting position (row, col) '''
        self.position = position

    def move(self, direction, board):
        ''' Move player in given direction if possible; returns True if moved, False if wall '''
        moves = {"W": (-1, 0), "S": (1, 0), "A": (0, -1), "D": (0, 1)}
        if direction not in moves:
            return False

        row, col = self.position
        dr, dc = moves[direction]
        new_row = (row + dr) % len(board.list)
        new_col = (col + dc) % len(board.list[0])

        if board.isAvailable(new_row, new_col):
            # Update maze: clear old position, set new to 'A'
            board.changePostiton(row, col, 'O')
            board.changePostiton(new_row, new_col, 'A')
            self.position = (new_row, new_col)
            return True
        return False

# New class: Game to encapsulate game logic (OOP improvement)
class Game:
    def __init__(self, board, leaderboard):
        self.board = board
        self.leaderboard = leaderboard
        self.player = None  # Will be set when playing

    def mazeCheck(self):
        ''' Check if maze is valid (has A, B, O, exactly one start/end, etc.) '''
        # All of this must be true for the maze to work
        trueTable = ['A' in self.board.uniqueValues(), 'B' in self.board.uniqueValues(),
                     'O' in self.board.uniqueValues(), self.board.Scount == 1, self.board.Ecount == 1]
        # If the leaderboard already exists meaning it is playable
        if self.leaderboard.leaderboardExist:
            return True
  
        if sum(trueTable) == 5:
            uniqueValues = self.board.uniqueValues()
       
            for x in ['A', 'B', 'O']:
                uniqueValues.remove(x)
            if 'X' in uniqueValues:
                uniqueValues.remove('X')
       
            # To ensure only A,B,O and X exists
            if uniqueValues != []:
                print(f'This character is not allowed {uniqueValues}, \nPlease configure the maze (Option 4) ')
                return False
        else:
            print('The maze created is invalid,\nPlease configure the maze (Option 4)')
            return False
        if not self.validMaze():
            print('This maze is not playable')
            return False
   
        # Successful
        return True

    def validMaze(self):
        ''' Validate if maze has a path to end using BFS-like search '''
        moves = ['A', 'D', 'W', 'S']
        done = [" "]
        Working = []
        flag = True
        while flag:
       
            Working = []
       
            for x in moves:
                for z in done:
                    put = z + x
         
                    try:
                        workingMaze = self.board.workableMaze(put.strip())
                   
                        if workingMaze[0]:
                            Working.append(put)
                      
                        if workingMaze[1] == self.board.getEnd():
                       
                            flag = False
                            valid = True
                            break
                    except:
                        continue
            if Working == []:
                valid = False
                break
            done = Working
        return valid

    def play(self):
        ''' Play the maze game manually '''
        if not self.mazeCheck():
            return

        self.player = Player(self.board.getStart())  # Create player at start
        end = self.board.getEnd()
  
        startTime = time.time()
        self.leaderboard.writeLeaderBoard()
        while True:
       
            viewmaze(self.board.list)
       
            print(f'\nLocation of Start (A) = (Row {self.board.getStart()[0]}, Column {self.board.getStart()[1]})\nLocation of End (B) = (Row {self.board.getEnd()[0]}, Column {self.board.getEnd()[1]})\n')
            moveEntered = input('Press \'W\' for UP, \'A\' for LEFT, \'S\' for DOWN, \'D\' for RIGHT,\'M\' for MAIN MENU: ').upper().strip()
            # Check if the option entered belongs to any option in the list
            if moveEntered not in ['W', 'A', 'S', 'D', 'M']:
                print('Only W,A,S,D,M characters are accepted\n')
                continue
            # To return to the main menu
            elif moveEntered == 'M':
                self.board.reset()
                break
            else:
                if self.player.move(moveEntered, self.board):
                    pass  # Moved successfully
                else:
                    print('The option you have chosen is wall\n')
           
                # If the player reaches end
                if self.player.position == end:
                    endTime = time.time()
                    score = endTime - startTime
                    tryNameAgain = True
                    while tryNameAgain:
                        print(f'{"YOU WON":*^30}')
                        print(f'Your score: {round(score, 2)}')
                        name = str(input('What is your name: ')).strip()
                        if not name:
                            tryNameAgain = False if input('You have entered no name, would like to stay anonymous? Y or N: ').strip().upper() == 'Y' else True
                        else:
                            tryNameAgain = False
                    if name:
                        self.leaderboard.append(name, round(score, 2))
                        self.leaderboard.writeLeaderBoard()
   
                    self.board.reset()
                    return

    def find_and_show_shortest_path(self):
        ''' Find and display the shortest path using BFS '''
        if not self.mazeCheck():
            return

        path = self.board.find_shortest_path()
        if path:
            print('Shortest path found (sequence of moves):')
            print(' -> '.join(path))
            print(f'Length: {len(path)} moves')
        else:
            print('No path to the end exists.')

# Main Menu option list (added new option for shortest path)
# To be able to iterate through the options
optionList = ["Exit Maze", "Read and load maze from file", "View maze", "Play maze game", "Configure current maze", "Export maze to file",
              "Create new maze", "Play maze using SenseHAT", "View Leaderboard", "Find shortest path using BFS"]

def isInterger(*Value):
    '''
    To check if this value input is a Integer
    INPUT:
    Values = Random Number of values
   
    RETURN:Boolean True (Integer) or False (Not Interger)
    '''
    try:
        for value in Value:
            value = int(value)
        return True
    except:
        return False

def isString(value):
    '''
    To check if this value input is a string
    INPUT:A string
    RETURN:Boolean True (String) or False (Not String)
    '''
    try:
        value = str(value)
        return True
    except:
        return False

def printMenu(meneList, heading):
    '''
    This is function to print maze
    INPUT:
    meneList = A list of strings that you want to print\n
    heading = A string that you wish to put as the header
    OUTUT: E.X [1] Read and load maze from file\n
                {index} {Name from list}\n
    RETURN: A String
    '''
    print(f'\n{heading}\n{"="*len(heading)}')
       
    # Example:
    # [1] Read and load maze from file
    # {Index} {Menu}
    for Index, Menu in enumerate(meneList[1:], 1):
        print(f'[{Index}] {Menu}')
    print(f"\n[0] {meneList[0]}")
    # To return input from user in STRING
    return input("\nEnter your option: ").strip()

def isReadFile(currentPath, filename):
    '''
    To check if this file is ready to be read
    INPUT: File Name in String
    Output: If there is any error
    RETURN: A tuple (Boolean, ErrorMessage(String)) or True
    '''
    # To check if this empty is file
    if not filename:
        return (False, 'Filename keyed in is empty\n')
    elif filename in os.listdir(path=currentPath):
        # To check if the file is in the directory
        return True
    elif not filename in os.listdir(path=currentPath):
        return (False, 'Does this file exist, it could not be found')
    elif not filename.endswith(('.txt', '.csv')):
        return (False, 'You are only allowed to use this .txt and .csv extension\n')
    else:
       return (False, 'Does this file exist, it could not be found')

def isWriteFile(currentPath, filename):
    if not filename:
        print('Filename keyed in is empty\n')
        return
   
    charRestricted = ['\\', '/', ':', '*', '"', '<', '>', '|']
    for restrict in charRestricted:
        if restrict in filename:
            print(f'Do not use this characters {charRestricted}')
            return False
   
    if not filename.endswith(('.txt', '.csv')):
        print('You are only allowed to use this .txt and .csv extension')
        return False
           
   
    if filename in os.listdir(path=currentPath):
        override = str(input('Do you want to override the existing file?\nY for yes or press any key to try again: '))
       
        export = True if override.upper() == 'Y' else False
        if export == False: print('\nYou have decided not to override try again!')
        return export
    else:
       return True

# Option Functions
# Option 1
def readfile(brd):
   
    '''
    Just to read the the name of the file
    and create a Board class
    RETURN: Board class
    '''
    # To get the current working directory
    currentPath = os.path.dirname(os.path.abspath(__file__))
    filename = input('Enter the name of the data file: ').strip(' ')
    isReadfile = isReadFile(currentPath, filename)
    # To check if this file is able to read
    if isReadfile == True:
        M = Board(file=currentPath + '/' + filename)
       
        # To check if this maze have a proper proportion
        if len(M) == len(M.list[0]) * len(M.list):
            print(f'Number of lines read: {len(M.list)}')
            return M
        else:
            print('Your maze is not balance, please read a proper file')
            if brd != None:
                print('Returning to previous Maze')
                return brd
            else:
                return
    # To ensure it returns back the brd if it already exists
    elif brd != None:
        print(isReadfile[1])
        return brd
    else:
        print(isReadfile[1])

# Option 2
def viewmaze(mazeList):
    '''
    Function used to view the class
    INPUT:mazeList -- Nested List
    Output: Rows of of each list from maze
    '''
    green = '\033[1;32;40m'
    red = '\033[1;31;40m'
    normal = '\033[0;37;40m'
    print('=' * 40 + '\n')
    # This were color codes to have color in maze
    # It is only compatible with mac terminal so it has been removed
    # comment it
    for row in mazeList:
        for values in row:
            if values.upper() == 'A':
                print(red + values + normal, end=' ')
            elif values.upper() == 'B':
                print(green + values + normal, end=' ')
            elif values.upper() == 'O':
                print(normal + '.', end=' ')
            else:
                print(normal + values, end=' ')
        print()
       
   
    # for x in mazeList:
    # print(x)

# Option 4
def configMaze(brd):
    configOption = ['', 'X', 'O', 'A', 'B']
    viewmaze(brd.list)
    optionlst = ['Exit Main Menu', 'Create wall', 'Create passageway', 'Create start point', 'Create end point']
   
    op = printMenu(optionlst, 'CONFIGURATION MENU')
    if not isInterger(op):
        print('We only accept integer')
        return True
    elif not int(op) in range(0, 5):
        print('Please only chose the option from 0 - 4')
        return True
    elif op == '0':
        return False
    else:
        op = int(op)
   
   
    while True:
        viewmaze(brd.list)
        approve = True
        coor = input('\nEnter the coordinate of the item you wish to change E.g. Row, Column \n\'B\' to return to Configure menu.\n\'M\'to return Main Menu: ')
       
        if coor.upper() == 'M':
            return False
        elif coor.upper() == 'B':
            break
        coor = coor.strip().split(',')
        conditions = [not len(coor) > 1 or not len(coor) < 3, not all(coor), not isInterger(*coor)]
        ErrorMessages = ['Invalid coordinates', 'The row or column is empty', 'Row and column must be integer']
       
        for condition, ErrorMessage in zip(conditions, ErrorMessages):
            if condition:
                print(ErrorMessage)
                approve = False
                break
       
        if approve:
            if int(coor[0]) < 0 or int(coor[1]) < 0:
                print('Coordinates should not be lesser than 0')
                continue
               
            row, col = int(coor[0]), int(coor[1])
            brdRow, brdCol = len(brd.list) - 1, len(brd.list[0]) - 1
           
            if (row > brdRow) or (col > brdCol):
                print(f'The maximum size is {brdRow},{brdCol}')
                continue
            else:
                # If the Start or end point exist this will replace instead of adding
                if op == 3 and brd.getStart() != None:
                    brd.config('X', *brd.getStart())
                if op == 4 and brd.getEnd() != None:
                    brd.config('X', *brd.getEnd())
               
                if op == 3 and brd.getStart() == None:
                    brd.Scount = 1
                if op == 4 and brd.getEnd() == None:
                    brd.Ecount = 1
                # To change the values
                brd.config(configOption[op], *coor)
                continue
    return True

# Option 5
def exportMaze(mazeList):
    # To get the current path
    currentPath = os.path.dirname(os.path.abspath(__file__))
    # Ask for user input
    filename = input('Enter the filename to save to: ')
    isWrite = isWriteFile(currentPath, filename)  # Check if the filenaming is able to read
    Curfilename = currentPath + '/' + filename
   
   
    if isWrite == True:
        with open(Curfilename, mode='w') as myfile:
                for n, x in enumerate(mazeList, 1):
                    myfile.write(''.join(x))
                    myfile.write("\n")
                        # Edit thisz
               
                print(f'File {filename} created with {n} records')
        return False
    elif isWrite == False:
        return True
    else:
        value = input('You have entered nothing do you wish to exit? \nN to try again or press any key to return to main menu: ')
       
        return True if value.upper() == 'N' else False

# Option 6
def createMaze():
    while True:
        emptyTheMaze = input('This will empty the current maze. Are you sure? (Y and N): ').strip()
        if not emptyTheMaze:
            print('You don\'t have reply, if you want to exit press N in the next question: ' )
            continue
        else:
            break
   
    if emptyTheMaze.upper() == 'Y':
        while True:
            coor = input("\nEnter the dimension of the new maze (row,column): ").strip().split(',')
           
          
            if isInterger(*coor):
                row, col = coor
                row, col = int(row), int(col)
                if (row * col) == 0:
                    print('Print chose a value with row and col must be above 0')
                    continue
                newMaze = []
                for x in range(row):
                    temp = []
                    for x in range(col):
                        temp.append('O')
                    newMaze.append(temp)
                M = Board(list=newMaze)
                createfile = input('\nWould you like to save the file. Y to create file or press any other key to continue: ').upper() == 'Y'
                if createfile:
                    breakLoop = True
                    while breakLoop:
                        breakLoop = exportMaze(M.list)
                print(f'A maze of {row} by {col} has been created\nPlease run the configuration maze to start configuring new maze')
                return M
           
            elif not all(coor):
                print('The row or column is empty\n')
                continue
            else:
                print('Row and column must be integer\n')
                continue
    elif emptyTheMaze.upper() == 'N':
        print('N has been keyed, returning back to Main Menu')
    else:
         print('Invalid input, returning back to Main Menu')
         return board

# Option 7
def movePi(brd, leaderboard):
   
    if isSenseHat == False:
        print('Please run this on a Raspberry Pi')
        return
    elif len(brd.list) != 8 or len(brd.list[0]) != 8:
        print('The maze must be 8 by 8')
        return
    game = Game(brd, leaderboard)  # Use Game class
    if not game.mazeCheck():
        return
    sense.clear()
    pi = Rashpi(brd)
   
    dic = {"up": pi.moveUp, "down": pi.moveDown, "left": pi.moveLeft, "right": pi.moveRight, "middle": False}
   
   
   
    flag = True
    startTime = time.time()
    while flag:
        for event in sense.stick.get_events():
            if event.action == "pressed":
                if pi.isAvailable(event.direction):
                    if event.direction != 'middle':
                        dic[event.direction]()
                    elif event.direction == 'middle':
                        sense.clear()
                        print('You have pressed the middle button returning to the Main Menu')
                        flag = False
                       
                else:
                    print('You hit the wall\n')
                if pi.isWin():
                    sense.clear()
                    endTime = time.time()
                    flag = False
                   
                    tryNameAgain = True
                    while tryNameAgain:
                        print(f'{"YOU WON":*^30}')
                        name = str(input('What is your name: ')).strip()
                        if not name:
                            tryNameAgain = False if input('You have entered no name, would like to stay anonymous? Y or N: ').strip().upper() == 'Y' else True
                        else:
                            tryNameAgain = False
                    if name:
                        leaderboard.append(name, round(endTime - startTime, 2))
                        leaderboard.writeLeaderBoard()
               
# Option 8
def printLeaderboard(lstOfLeaderBoard):
    print(f'{"Name":<30}{"Score"}')
    print('=' * 35)
   
   
    lstOfLeaderBoard = sorted(lstOfLeaderBoard, key=lambda x: x[1])
   
    if lstOfLeaderBoard == []:
        print('The leaderboard has no players who complete the maze, please play the maze game')
    index = 0
    for name, score in lstOfLeaderBoard:
            if index >= 10:
              break
            index += 1
            print(f'{name:<30}{score}')

board = None
game = None  # Will be initialized later
while True:
    breakLoop = True
    option = printMenu(optionList, 'Main Menu')
   
    if isInterger(option):
        option = int(option)
    else:
        print('The value keyed is not a Integer')
        continue
   
    if option in range(0, 10):
        print(f'\nOption [{option}] {optionList[option]}\n')
   
    if option == 0:
        print('Thank you for playing the maze game\nExiting the maze game')
        exit()
    elif option == 1:
        board = readfile(board)
        if board != None:
            leaderboard = LeaderBoard(board.digestMaze())
            game = Game(board, leaderboard)  # Initialize Game
    elif option == 2 and board != None:
        viewmaze(board.list)
    elif option == 3 and board != None:
        game.play()  # Use Game class for play
    elif option == 4 and board != None:
         while breakLoop:
             breakLoop = configMaze(board)
         leaderboard = LeaderBoard(board.digestMaze())
    elif option == 5 and board != None:
        while breakLoop:
            breakLoop = exportMaze(board.list)
    elif option == 6:
        board = createMaze()
        leaderboard = LeaderBoard(board.digestMaze())
        game = Game(board, leaderboard)  # Reinitialize Game
    elif option == 7 and board != None:
        movePi(board, leaderboard)
    elif option == 8 and board != None:
        printLeaderboard(leaderboard.getLeaderBoard())
    elif option == 9 and board != None:
        game.find_and_show_shortest_path()  # New option: show shortest path
    else:
        if not option in range(0, 10):
            print('The value key in must be from 0 - 9')
        else:
            print('Please read and load from file, THE 1st Option or The 6th Option')
        continue