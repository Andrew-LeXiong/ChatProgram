"""
This is the server side setup for the chatroom server. It will handle
messages coming from client and either broadcast it or send it to 
specific user. 

Eric Sosa
tq2689yo


andrew Le-Xiong 
nd2236xt
"""

import socket
import sys
import threading
import pickle 
import time

#argument validation
if len(sys.argv) > 2:
	print("ERROR: Too many arguments. Format: chatserver.py <port_num>")
	sys.exit()

if len(sys.argv) < 2: 
	print("ERROR: Too few arguments. Format: chatserver.py <port_num>")
	sys.exit()

#port number validation
try: 
	port_number = int(sys.argv[1])
except ValueError:
	print("ERROR: Invalid number for port(argument: " + str(sys.argv[1]) + ")")
	sys.exit()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', int(port_number)))

#create dictionaries to be used
maximumNumofThread = 10
active_clients_dict = {}
users_dict = {}

server_socket.listen(10)

#thread for handling each different client
def newThread(conn, address): 
	usernameDecoded = ""

	try:
		#logging in
		conn.send("Cgive username".encode())
		usernameMessage = conn.recv(2048)
		usernameDecoded = usernameMessage.decode()

		#if user is already logged in, exit
		if usernameDecoded in active_clients_dict.keys():
			conn.send("Cuser already logged in".encode())
			return

		#if user doesn't exist yet, create a new user and ask for password
		if not usernameDecoded in users_dict.keys():
			conn.send("Cnew user".encode())
			newPasswordMessage = conn.recv(2048)
			users_dict[usernameDecoded] = newPasswordMessage.decode()
			conn.send("Cnew user created".encode())

			addActiveUser(usernameDecoded, conn)
			updateUserFile()
		#else logging normally
		else:	
			conn.send("Cexisting user".encode())
			
			#while loop will repeat until user enters correct password
			while True:
				passwordMessage = conn.recv(2048)
				if passwordMessage.decode() == users_dict.get(usernameDecoded):
					conn.send("Cgood password".encode())
					addActiveUser(usernameDecoded, conn)
					break
				else: 
					conn.send("Cbad password".encode())
					time.sleep(.2)
					continue

		#while loop to keep receiving message from user
		while True:
			message = conn.recv(2048)

			#if message is public message
			if message.decode() == 'PM':
				conn.send("Csending message for PM".encode())

				receivedMessage = conn.recv(2048)
				sendToAll(receivedMessage.decode(), usernameDecoded)

			#if message is direct message
			elif message.decode() == 'DM':
				conn.send(listOfActiveUsers(usernameDecoded).encode())
				time.sleep(.2)
				conn.send("Cchoose user for DM".encode())
				
				#if there's no other user online
				if len(active_clients_dict) == 1:
					conn.send("Cno one online for DM".encode())
					continue

				message = conn.recv(2048)
				recipientUsername = message.decode()

				#if recipient is found
				if recipientUsername in active_clients_dict.keys():
					conn.send("Cuser found for DM".encode())
					message = conn.recv(2048)
					messageToSend = "D" + usernameDecoded + "##" + message.decode()

					#if recipient is still online at the moment the message is being sent
					if recipientUsername in active_clients_dict.keys():
						active_clients_dict[recipientUsername].send(messageToSend.encode())
					else:
						conn.send("Cmessage NOT successful for DM".encode())
				else:
					conn.send("Cuser not found for DM".encode())
					continue

			#if message is exit then close the socket and remove client
			elif message.decode() == "EX":
				removeActiveUser(usernameDecoded, conn)
				conn.close()
	except ConnectionResetError:
		removeActiveUser(usernameDecoded, conn)
	except OSError:
		removeActiveUser(usernameDecoded, conn)

#method to add user
def addActiveUser(username, connection):
	active_clients_dict[username] = connection

#method to remove user
def removeActiveUser(username, connection):
	if username in active_clients_dict.keys():
		del active_clients_dict[username]
		connection.close()

#method to return a list of active user
def listOfActiveUsers(currentUser):
	total = "DServer##\nList of all active users:\n"
	if len(active_clients_dict) == 1:
		total += "No one else online.\n"
	else:	
		for user in active_clients_dict.keys():
			if currentUser!=user:
				total += user + "\n"
	return total	

#method to update file whenever a new user is added
def updateUserFile():
	with open('users.pickle' , 'wb') as f:
		pickle.dump(users_dict, f, pickle.HIGHEST_PROTOCOL)

#method to load in the user file once the program loads
def loadUserFile():
	with open('users.pickle' , 'rb') as f:
		global users_dict
		users_dict = pickle.load(f)

#send to all online users
def sendToAll(message, username):
	for user in active_clients_dict.keys():
		if user!=username:
			active_clients_dict[user].send(("D" + username +"##" + message).encode())

try:
	loadUserFile()
except:
	print("File is empty. Nothing to load")

while True:
	conn, address = server_socket.accept()

	#if maximum number of user is on, reject the client, otherwise start thread
	if len(active_clients_dict) + 1 > maximumNumofThread:
		conn.send("Cno more space".encode())
		conn.close()
	else: 
		t = threading.Thread(target=newThread, args=(conn , address))
		t.start()




