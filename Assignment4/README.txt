Andrew Le-Xiong & Eric Sosa

There are 4 files:
1. README to give instructions
2. chatclient.py - the client side version for the chatroom
3. chatserver.py - the server side version for the chatroom
4. users.pickle - the file to store usernames and passwords

INSTRUCTIONS:
1. Start the server by entering "chatserver.py <port_num>" in the terminal. 
	For server starting with 0 users in users.pickle, the server will warn that the file did not load anything.
	ex. chatserver.py 56011

2. Start the client by entering "chatclient.py <server_name> <port_num> <username>" in the second terminal. 
	New users will be able to create a password for their username. 
	The server will automatically save it. 
	Start up to 10 client terminals as server will not accept anymore beyond that.
	ex. chatclient.py 127.0.0.1 56011 ericsosa123