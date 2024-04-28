import socket

HOST = '127.0.0.1'
PORT = 27399

def isValid(input):
    input = str(input)
    if ',' in input and len(input) == 3:
        if input not in invalidMoves and input[1] == ",":
            arr = input.split(',')
            if len(arr) == 2:
                val1 = int(arr[0])
                val2 = int(arr[1])
                if (val1 >= 0 and val1 <= 2) and (val2 >= 0 and val2 <= 2):
                    return True
    return False

def getMovesFromBoard(board):
        # "| | | |\n-------\n| | | |\n-------\n| | | |\n"
        invMoves = []
        firstIteration = True
        for i in range(3):
            if not firstIteration:
                board = board[8:]
            for j in range(3):
                if board[1] != " ":
                    invMoves.append(f'{i},{j}')
                board = board[2:]
                firstIteration = False
            board = board[2:]
        return invMoves

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Client Connected")
message = str(s.recv(4096).decode())

myTurn = None
lastMove = None
myMark = None
theirMark = None
invalidMoves = []

if "You are X" in message:
    myTurn = True
    myMark = "X"
    theirMark = "O"
else:
    myTurn = False
    myMark = "O"
    theirMark = "X"

print(message)
s.send(f'{myMark}: {"OK"}'.encode())
# get game board and print it
message = str(s.recv(4096).decode())
print(message)

while True:
    # get info about winner
    message = str(s.recv(4096).decode())
    if "WINS" in message or "TIE" in message:
        print(message)
        break

    if myTurn:
        val = input("Input comma delimited coordinates. Ex: 0,0\n")
        while not isValid(val):
            val = input("Input comma delimited coordinates. Ex: 0,0\n")
        else:
            arr = val.split(',')
            s.send(f'{myMark}: {arr[0]},{arr[1]}'.encode())
            message = str(s.recv(4096).decode())

            # prints updated gameboard
            print(message)
            myTurn = not myTurn
    else:
        print("Waiting for opponent to move...")
        message = str(s.recv(4096).decode())
        # prints game board
        print(message)
        invalidMoves = getMovesFromBoard(message)
        myTurn = not myTurn