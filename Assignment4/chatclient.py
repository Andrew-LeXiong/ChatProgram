"""
This is the client side setup for the chatroom server setup. 
The client side setup has the job of sending messages and 
confirming from server that messages are being received.

Eric Sosa
tq2689yo

Andrew Le-Xiong
nd2236xt

"""

import socket
import sys
import threading
import time

#argument validation
if len(sys.argv) > 4:
	print("ERROR: Too many arguments. Format: chatclient.py <server_name> <port_num> <username>")
	sys.exit()

if len(sys.argv) < 4: 
	print("ERROR: Too few arguments. Format: chatclient.py <server_name> <port_num> <username>")
	sys.exit()

#port number validation
try: 
	port_number = int(sys.argv[2])
except ValueError:
	print("ERROR: Invalid number for port(argument: " + str(sys.argv[2]) + ")")
	sys.exit()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((str(sys.argv[1]), int(port_number)))

latestCMessage = ""
latestDMessage = ""

#to check that it's a command message
def isCommandMessage(message):
	if message[0:1] == 'C':
		return True
	else:
		return False

#to check that it's a data message
def isDataMessage(message):
	if message[0:1] == 'D':
		return True
	else:
		return False

#method to handle all incoming messages
#command messages are stored while data messages are displayed right away
def receivingMessageThread(): 
	try:
		while True: 
			rawMessage = server.recv(2048)
			decodedMessage = rawMessage.decode()

			if isCommandMessage(decodedMessage): 
				global latestCMessage
				latestCMessage = decodedMessage[1:]
			elif isDataMessage(decodedMessage):
				global latestDMessage
				latestDMessage = decodedMessage[1:]
				splitMessage = latestDMessage.split("##", 1)
				sender = splitMessage[0]
				message = splitMessage[1]

				print("\n<From " + sender + ">: " + message)
			else: 
				print("Error: Neither D or C message")
				sys.exit()
	except ConnectionAbortedError: 
		print("Closing Client.")
		sys.exit()
	except:
		print("Error.")
		sys.exit()

#method to handle waiting for certain command messages to arrive in order for certain operations to continue
def waitingForMessage(matchingMessage):
	timeout = time.time() + 1
	while time.time() < timeout:
		if latestCMessage == matchingMessage:
			return True

	return False

t = threading.Thread(target=receivingMessageThread, args=())
t.start()

#if the server is full, exit
if waitingForMessage("no more space"):
	print("The server is currently full.")
	sys.exit()

#wait for server to send command to give username
if waitingForMessage("give username"):
	username = sys.argv[3]
	server.send(username.encode())
else: 
	print("Server not available.")
	sys.exit()

#if server says user is already logged in, exit
if waitingForMessage("user already logged in"):
	print("Username is already logged in.")
	sys.exit()

#if server detects a new user, enter password
if waitingForMessage("new user"):
	server.send(input("New user detected.\nCreate a new password: ").encode())
	if waitingForMessage("new user created"):
		print("Successful Login. Signed in as " + username)

#if server finds an existing user, enter correct password to continue
elif waitingForMessage("existing user"):
	print("User Found. ")
	while True:
		server.send(input("Enter password: ").encode())
		if waitingForMessage("password is good"):
			print("Successful Login!! Signed in as " + username)
			break
		elif waitingForMessage("password is wrong"):
			print("Invalid password. Try again.")
			continue

#while loop to repeatedly prompt and send messages
while True:
	response = input("Please enter PM, DM or EX: ")

	#public message
	if response == "PM":
		#request public message
		server.send("PM".encode())

		#wait for response
		if waitingForMessage("sending message for PM"):
			messageToSend = input("Enter your message: ")
			server.send(messageToSend.encode())
		else:
			print("messaged failed")
			continue

	#direct message
	elif response == "DM":
		server.send("DM".encode())
		if waitingForMessage("choose user for DM"):
			if waitingForMessage("no one online for DM"):
				print("No one is online for DM")
				continue

			#while loop to handle user trying to send messages to themselves
			while True:
				recipientUsername = input("Enter username to send message to: ")
				if recipientUsername == username:
					print("Cannot send message to yourself.")
				else:
					break

			server.send(recipientUsername.encode())

			if waitingForMessage("user found for DM"):
				server.send(input("<To " + recipientUsername + ">: ").encode())

				if waitingForMessage("message NOT successful for DM"):
					print("Message not received.")
			elif waitingForMessage("user not found for DM"):
				print("Username not found.\n")
			else:
				print("Did not get a reponse from server in time.\n")
		else:
			print("Did not get a reponse from server in time.\n")

	#exit
	elif response == "EX":
		server.send("EX".encode())
		server.close()
		sys.exit()

