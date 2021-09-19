import copy
import timeit

# Returns the input of the board elements separated by commas
def readBoardInput(n):
  board = []
  for i in range(int(n)):
    str = input()
    row = [int(x) for x in str.split(',')]
    board.append(row)
  return board

# Returns an ID formed from the order of the items in the list
def getBoardID(board, n):
  id = ''
  for i in range(n):
    for j in range(n):
      id += str(board[i][j]) + '-'
  return id

# Function to find the zero element in the board
def findEmptySpacePosition(x, n):
  currentBoard = graph[x]['board']
  for i in range(n):
    for j in range(n):
      if(currentBoard[i][j] == 0):
        return { 'row': i, 'column': j }
  return { 'row': -1, 'column': -1 }

def swap(x, emptySpace, rowShift, columnShift):
  # Get row and column where the empty space is
  row = emptySpace['row']
  column = emptySpace['column']
  # Create a copy of the board
  swappedBoard = copy.deepcopy(graph[x]['board'])
  # Swap elements based on given shift
  swappedBoard[row][column] = swappedBoard[row + rowShift][column + columnShift]
  swappedBoard[row + rowShift][column + columnShift] = 0
  return swappedBoard

def swapLeft(x, emptySpace):
  return swap(x, emptySpace, 0, -1)

def swapRight(x, emptySpace):
  return swap(x, emptySpace, 0, 1)

def swapUp(x, emptySpace):
  return swap(x, emptySpace, -1, 0)

def swapDown(x, emptySpace):
  return swap(x, emptySpace, 1, 0)

def generateChildren(x, n):
  # Create empty list to store node children later on
  children = []
  # Find empty position (0) in board
  emptySpace = findEmptySpacePosition(x, n)
  # Make a left swap if possible and add swapped board to children list
  if emptySpace['column'] > 0:
    tempBoard = swapLeft(x, emptySpace)
    children.append(tempBoard)
  # Make a right swap if possible and add swapped board to children list
  if emptySpace['column'] != n-1:
    tempBoard = swapRight(x, emptySpace)
    children.append(tempBoard)
  # Make an up swap if possible and add swapped board to children list
  if emptySpace['row'] > 0:
    tempBoard = swapUp(x, emptySpace)
    children.append(tempBoard)
  # Make a bottom swap if possible and add swapped board to children list
  if emptySpace['row'] != n-1:
    tempBoard = swapDown(x, emptySpace)
    children.append(tempBoard)

  return children

# Get coordinates of elements to calculate Manhattan distance
def getCoordinates(board):
  coordinates = {}
  for row in range(len(board)):
    for column in range(len(board)):
      coordinates[board[row][column]] = { 'x': column, 'y': row }
  return coordinates

# Manhattan distance is calculated as the sum of the absolute differences between the two elements
def getManhattanDistance(current, target):
  currentCoordinates = getCoordinates(current)
  targetCoordinates = getCoordinates(target)  
  h = 0
  for key in currentCoordinates:
    deltaX = abs(currentCoordinates[key]['x'] - targetCoordinates[key]['x'])
    deltaY = abs(currentCoordinates[key]['y'] - targetCoordinates[key]['y'])
    h += deltaX + deltaY
  return h

# Function to sort open list by heuristic value
def getFn(key):
  return graph[key]['f(n)']

# Recursive function to get all descendants of a given node
def getDescendants(id, acc):
  for child in graph[id]['children']:
    acc.append(child)
    getDescendants(child, acc)
  return acc

# Delete node and remove its id from open or closed
def deleteNodes(nodes):
  for key in nodes:
    graph.pop(key)
    if key in openList:
      openList.remove(key)
    if key in closedList:
      closedList.remove(key)

def analizeChildren(children, x, n, target):
  for child in children:
    childID = getBoardID(child, n)

    # Case 1: child is neither open nor closed
    if not childID in openList and not childID in closedList:
      # Get heuristic value
      g = graph[x]['g(n)'] + 1
      h = getManhattanDistance(child, target)
      # Create node
      graph[childID] = { 'board': child, 'f(n)': g + h, 'g(n)': g, 'h(n)': h, 'children': [], 'parent': x }
      # Add node id to its parent
      graph[x]['children'].append(childID)
      # Add node id to open
      openList.append(childID)

    # Case 2: child is in opens
    elif childID in openList:
      # Get heuristic value
      g = graph[x]['g(n)'] + 1
      h = getManhattanDistance(child, target)
      # Compare heuristics of the existing node with this new node
      if graph[childID]['f(n)'] > g + h:
        # Obtain descendants of the graph
        descendants = getDescendants(childID, [])
        # Delete child nodes, and delete their ids from open and/or closed
        deleteNodes(descendants)
        # Get id of previous parent
        oldParent = graph[childID]['parent']
        # Remove child from previous parent
        graph[oldParent]['children'].remove(childID)
        # Create new childless node with new heuristics
        graph[childID] = { 'board': child, 'f(n)': g + h, 'g(n)': g, 'h(n)': h, 'children': [], 'parent': x }        
        # Add child to new parent
        graph[x]['children'].append(childID)

    # Case 3: child is in closed
    elif childID in closedList:
      # Get heuristic value
      g = graph[x]['g(n)'] + 1
      h = getManhattanDistance(child, target)
      # Compare heuristics of the existing node with this new node
      if graph[childID]['f(n)'] > g + h:
        # Obtain descendants of the graph
        descendants = getDescendants(childID, [])
        # Delete child nodes, and delete their ids from open and/or closed
        deleteNodes(descendants)
        # Get id of previous parent
        oldParent = graph[childID]['parent']
        # Remove child from previous parent
        graph[oldParent]['children'].remove(childID)
        # Create new childless node with new heuristics
        graph[childID] = { 'board': child, 'f(n)': g + h, 'g(n)': g, 'h(n)': h, 'children': [], 'parent': x }
        # Add child to new parent
        graph[x]['children'].append(childID)
        # Remove id from closed
        closedList.remove(childID)
        # Add id to open
        openList.append(childID)

    else:
      exit()

  # Add X to closed and sort open by heuristic value
  closedList.append(x)
  openList.sort(key=getFn)

# Function that starts from the target node, and searches for its parent nodes until it reaches the root
def getPath(node, path):
  path.append(graph[node]['board'])
  if not graph[node]['parent'] is None:
    getPath(graph[node]['parent'], path)
  return path

# Get coordinates of the nodes that make up the solution path
def checkPath(path):
  index = 0
  movements = {}
  for board in path:
    for i in range(len(board)):
      for j in range(len(board)):
        if(board[i][j] == 0):
          movements[index] = {'x': j, 'y': i}
    index += 1
  return movements

# Analyze how the blank was moved to obtain the solution moves to solve the puzzle
def getDirections(movements):
  directions = []
  for index in range(len(movements) - 1):
    deltaX = movements[index]['x'] - movements[index+1]['x']
    deltaY = movements[index]['y'] - movements[index+1]['y']
    if deltaX == 1:
      directions.append('Izquierda')
    if deltaX == -1:
      directions.append('Derecha')
    if deltaY == 1:
      directions.append('Arriba')
    if deltaY == -1:
      directions.append('Abajo') 
  return directions

def executeAlgorithm():
  # Create path, open and closed list as global variables
  global path
  path = []
  global openList
  openList = []
  global closedList
  closedList = []

  # Read input and generate starting board
  n = int(input())
  root = readBoardInput(n)
  target = readBoardInput(n)

  # Get ID for the root element of the graph
  rootID = getBoardID(root, n)

  # Graph will be represented as a dictionary
  global graph
  graph = {}
  # Adding first node to graph
  graph[rootID] = { 'board': root, 'f(n)': 0, 'g(n)': 0, 'h(n)': 0, 'children': [], 'parent': None }
  # Adding first node to open list
  openList = [rootID]
  while openList:
    # Remove the leftmost state from open and add it to X
    x = openList.pop(0)
    # Check if current board is already the target
    if target == graph[x]['board']:
      path = getPath(x, [])
      path.reverse()
      movements = checkPath(path)
      directions = getDirections(movements)
      print(', '.join(directions))
      return directions
    else:
      # Generate children and analyse each one
      children = generateChildren(x, n)
      analizeChildren(children, x, n, target)
  
  # Inform that a solution was not found
  print('No se encontro una solucion')

start_time = timeit.default_timer()
executeAlgorithm()
# Print program execution time
print('Tiempo en segundos:', timeit.default_timer() - start_time)