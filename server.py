
# *****************************************************
# This file implements a server for receiving the file
# sent using sendfile(). The server receives a file and
# prints it's contents.
# *****************************************************

import socket
import sys
import os

# The port on which to listen
listenPort = sys.argv[1]

# Create a welcome socket. 
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
welcomeSock.bind(('', int(listenPort)))

# Start listening on the socket
welcomeSock.listen(1)

# ************************************************
# Receives the specified number of bytes
# from the specified socket
# @param sock - the socket from which to receive
# @param numBytes - the number of bytes to receive
# @return - the bytes received
# *************************************************
def recvAll(sock, numBytes):
	
	# The buffer
	recvBuff = ""
	
	# The temporary buffer
	tmpBuff = ""
	
	# Keep receiving till all is received
	while len(recvBuff) < numBytes:
		
		# Attempt to receive bytes
		tmpBuff =  sock.recv(numBytes).decode('ascii')
		
		# The other side has closed the socket
		if not tmpBuff:
			break
		
		# Add the received bytes to the buffer
		recvBuff += tmpBuff
	
	return recvBuff

# Send Data
def get_command(file, clientSock, addr):
	fileObj = open(file, "r")
	numSent = 0
	fileData = None
	while True:
		fileData = fileObj.read(65536)
		if fileData:
			dataSizeStr = str(len(fileData))

			while len(dataSizeStr) < 10:
				dataSizeStr = "0" + dataSizeStr

			fileData  = dataSizeStr + fileData
			numSent = 0

			while len(fileData) > numSent:
				numSent += clientSock.send(fileData[numSent:].encode('ascii'))
		else:
			break
	clientSock.send(numSent)
	fileObj.close()

# Receive Data
def put_command(clientSock, addr):
	# The buffer to all data received from the
	# the client.
	fileData = ""
		
	# The temporary buffer to store the received
	# data.
	recvBuff = ""
		
	# The size of the incoming file
	fileSize = 0	
		
	# The buffer containing the file size
	fileSizeBuff = ""
		
	# Receive the first 10 bytes indicating the
	# size of the file
	fileSizeBuff = recvAll(clientSock, 10)
			
	# Get the file size
	fileSize = int(fileSizeBuff)
		
	print("The file size is ", fileSize)
		
	# Get the file data
	fileData = recvAll(clientSock, fileSize)
		
	print("The file data is: ")
	print(fileData)
			
	# Close our side
	clientSock.close()

def ls_command(clientSock, addr):
	lst = os.listdir('.')
	numSent = 0
	
	print(len(lst))

def quit_command(clientSock, addr):
	print('quit')
		
# Accept connections forever
if __name__ == '__main__':
	while True:
		print("Waiting for connections...")
				
		# Accept connections
		clientSock, addr = welcomeSock.accept()
			
		print("Accepted connection from client: ", addr)
		print("\n")

		command = clientSock.recv(1)

		if(command == b'p'):
			put_command(clientSock, addr)

		if(command == b'g'):
			fNamelen = clientSock.recv(1).decode('ascii')
			fName = clientSock.recv(int(fNamelen)).decode('ascii')
			get_command(fName, clientSock, addr)

		if(command == b'l'):
			ls_command(clientSock, addr)

		if(command == b'q'):
			quit_command(clientSock, addr)
