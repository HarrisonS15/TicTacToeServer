import tkinter as tk
import socket
import time

HOST = '127.0.0.1'
PORT = 27399
 
    
class UserInterface(object):
    #handles user input (tkinter)

    # when a button is clicked, tell the server to try and click it
    # if the server adds the mark to the board, it will tell both UI's to add the mark to the UI 
    def buttonClick(self, x, y):
        if (self._myTurn and not self._isGameOver):
            self._buttons[x][y].configure(text=self._mark)
            self._myTurn = False
            self._lastMove = (x,y)


    def recieveFromClient(self, x, y):
        # Schedule the update to happen in the next iteration of the event loop
        print('wbh')
        self._window.after(10, self.updateButton, x, y)

    def updateButton(self, x, y):
        self._buttons[x][y].configure(text=self._otherMark)
        self._buttons[x][y].text = self._otherMark
        self._myTurn = True
        self._window.update()
        print('here')

    def getLastMove(self):
        return self._lastMove
    
    def endGame(self, iWon):
        self._isGameOver = True

        if (iWon == None):
            self._result.config(text="You Tied.")
            self._turn.config(text="")
        elif (iWon == True):
            self._result.config(text="You Win!")
            self._turn.config(text="")
        else:
            self._result.config(text="You Lost.")
            self._turn.config(text="")
        self._window.update()


    def __init__(self, myTurn):
        self._isGameOver = False
        self._mark = "X" if myTurn else "O"
        self._otherMark = "X" if not myTurn else "O"
        self._myTurn = myTurn
        self._lastMove = None

        self._window = tk.Tk()
        self._window.title("Tic Tac Toe")
        window_width = 250
        window_height = 450
        screen_width = self._window.winfo_screenwidth()
        screen_height = self._window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self._window.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')

        self._turn = tk.Label(self._window, text=("Your Turn" if myTurn else "Their Turn"), font=('Times New Roman', 20))
        self._turn.grid(row=0, column=0, columnspan=3, pady=5)
        self._move = tk.Label(self._window, text=("You are X" if myTurn else "You are O"), font=('Times New Roman', 20))
        self._move.grid(row=1, column=0, columnspan=3, pady=5)
        self._result = tk.Label(self._window, text="", font=('Times New Roman', 20))
        self._result.grid(row=2, column=0, columnspan=3, pady=5)

        self._buttons = [[None, None, None],
                        [None, None, None],
                        [None, None, None]]

        for i in range(3):
            for j in range(3):
                self._buttons[i][j] = tk.Button(self._window, text="", width=10, height=5)
                self._buttons[i][j].configure(command=lambda i=i, j=j: [self.buttonClick(i, j)])
                self._buttons[i][j].grid(row=i+3, column=j, padx=2, pady=2)

        self._window.mainloop()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Client Connected")
message = str(s.recv(4096).decode())


myUI = None
myTurn = None
lastMove = None
myMark = None
theirMark = None

if "You are X" in message:
    myUI = UserInterface(True)
    myTurn = True
    myMark = "X"
    theirMark = "O"
else:
    myUI = UserInterface(False)
    myTurn = False
    myMark = "O"
    theirMark = "X"

print(myMark)

s.send("READY".encode())
message = str(s.recv(4096).decode())
turn1 = True
while myUI._window.mainloop():
    # server sends "GAME START" msg to both, which triggers while loop to run
    
    if "GAME OVER" in message:
        break

    while myTurn:
        newMove = myUI.getLastMove()
        if lastMove != newMove:
            print(f'{myMark}: {newMove[0]},{newMove[1]}')
            s.send(f'{myMark}: {newMove[0]},{newMove[1]}'.encode())
            lastMove = newMove
            break
        else:
            continue
        
    message = str(s.recv(4096).decode())
    while not myTurn:
        print(message)
        if turn1:
            message = str(s.recv(4096).decode())
            print(message)
        movesMsg = str(message)[3:]
        moves = movesMsg.split(',')
        myUI.recieveFromClient(int(moves[0]), int(moves[1]))
        break
    turn1 = False
    myTurn = not myTurn

if (myMark in message[10:]):
    myUI.endGame(True)
    s.close()
elif (theirMark in message[10:]):
    myUI.endGame(False)
    s.close()
else:
    myUI.endGame(None)
    s.close()


