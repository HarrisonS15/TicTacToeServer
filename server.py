import tkinter as tk
import socket
import time
from _thread import *
import threading

HOST = '127.0.0.1'
PORT = 27399


class Moves(enumerate):
    X = 'X'
    O = 'O'
    EMPTY = ' '

class TicTacToeModel(object):
    #Handles game logic
    
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self._lastTurn = Moves.O
        self._board = [[Moves.EMPTY for i in range(3)] for j in range(3)]
        
        
    def checkWinner(self):
        winner = Moves.X
        for x in range(2):
            #vertical wins
            if (self._board[0][0] == winner and self._board[0][1] == winner and self._board[0][2] == winner):
                return winner
            if (self._board[1][0] == winner and self._board[1][1] == winner and self._board[1][2] == winner):
                return winner
            if (self._board[2][0] == winner and self._board[2][1] == winner and self._board[2][2] == winner):
                return winner
            #horizontal wins
            if (self._board[0][0] == winner and self._board[1][0] == winner and self._board[2][0] == winner):
                return winner
            if (self._board[0][1] == winner and self._board[1][1] == winner and self._board[2][1] == winner):
                return winner
            if (self._board[0][2] == winner and self._board[1][2] == winner and self._board[2][2] == winner):
                return winner
            #diagonal wins
            if (self._board[0][0] == winner and self._board[1][1] == winner and self._board[2][2] == winner):
                return winner
            if (self._board[0][2] == winner and self._board[1][1] == winner and self._board[2][0] == winner):
                return winner
            winner = Moves.O
        
        #checks if game can continue, then return null, else return empty which means a tie
        for i in range(3):
            for j in range(3):
                if (self._board[i][j] == Moves.EMPTY):
                    return None
            
        
        #if none of the cells are empty, and no winner has been returned yet, its a tie.
        return Moves.EMPTY

    def addMark(self, x, y):
        if ((0 > x | x >= 3) | (0 > y | y >= 3)):
            return False
        if (self._board[x][y] != Moves.EMPTY):
            return False
        if (self._lastTurn == Moves.O):
            self._board[x][y] = self._lastTurn = Moves.X
            return True
        else:
            self._board[x][y] = self._lastTurn = Moves.O
            return True
        

    def valueToString(self, val):
        if (val ==  Moves.X):
            return "X"
        if (val == Moves.O):
            return "O"
        else:
            return " "
        
    def boardToString(self):
        returnStr = ""
        for i in range(3):
            if returnStr != "":
                returnStr += "-------\n"
            for j in range(3):
                returnStr += "|" + self.valueToString(self._board[i][j])
            returnStr += "|\n"
        return str(returnStr)

def playGame(prev_connection, conn):
    print("game running")
    player1sTurn = True
    game = TicTacToeModel(prev_connection, conn)

    game.player1.send("You are X".encode())
    game.player2.send("You are O".encode())
    move = str(game.player1.recv(4096).decode())
    move = str(game.player2.recv(4096).decode())
    game.player1.send(game.boardToString().encode())
    game.player2.send(game.boardToString().encode())
    while True:
        
        winner = game.checkWinner()
        if (winner == None):
            game.player1.send("C".encode())
            game.player2.send("C".encode())
        else:
            if (winner == Moves.X):
                game.player1.send("GAME OVER! X WINS".encode())
                game.player2.send("GAME OVER! X WINS".encode())
            elif (winner == Moves.O):
                game.player1.send("GAME OVER! O WINS".encode())
                game.player2.send("GAME OVER! O WINS".encode())
            else:
                game.player1.send("GAME OVER! TIE".encode())
                game.player2.send("GAME OVER! TIE".encode())
            break

        #accept move from appropriate person, check for win. if win, send message to both, else only send message to other
        if (player1sTurn):
            move = str(game.player1.recv(4096).decode())
            moveSubString = move[3:]
            moveArr = moveSubString.split(',')
            game.addMark(int(moveArr[0]),int(moveArr[1]))
            game.player1.send(game.boardToString().encode())
            game.player2.send(game.boardToString().encode())
        else:
            move = str(game.player2.recv(4096).decode())
            moveSubString = move[3:]
            moveArr = moveSubString.split(',')
            game.addMark(int(moveArr[0]),int(moveArr[1]))
            game.player1.send(game.boardToString().encode())
            game.player2.send(game.boardToString().encode())
        player1sTurn = not player1sTurn
        
    

def run(s):
    prev_connection = None
    while True:
        conn, addr = s.accept()
        print("client connected")
        if prev_connection:
            
            playGame(prev_connection, conn)
            prev_connection = None
            conn = None
        else:
            prev_connection = conn
            


client1 = None
client2 = None

sockets = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
print('Server Listening')
s.listen(5)

run(s)

s.close()