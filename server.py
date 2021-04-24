
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
def get_command(file, dataSock):
	fileObj = open(file, "r")
	numSent = 0
	fileData = None
	while True:
		fileData = fileObj.read(65536)
		if fileData:
			dataSizeStr = str(len(fileData))

			dataSizeStr = dataSizeStr.rjust(10, '0')

			fileData  = dataSizeStr + fileData
			numSent = 0

			while len(fileData) > numSent:
				numSent += dataSock.send(fileData[numSent:].encode('ascii'))
			dataSock.send(str(numSent).encode('ascii'))
		else:
			break
	fileObj.close()
	dataSock.close()

# Receive Data
def put_command(dataSock):
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
	fileSizeBuff = recvAll(dataSock, 10)
			
	# Get the file size
	fileSize = int(fileSizeBuff)
		
	print("The file size is ", fileSize)
		
	# Get the file data
	fileData = recvAll(dataSock, fileSize)
		
	print("The file data is: ")
	print(fileData)
			
	# Close our side
	dataSock.close()

def ls_command(dataSock):
	lst = os.listdir('.')
	numSent = 0
	lslen = len(lst)
	dataSock.send(str(lslen).rjust(2,'0').encode('ascii'))
	for i in lst:
		numSent = len(i)
		dataSock.send(str(numSent).rjust(2,'0').encode('ascii'))
		dataSock.send(i.encode('ascii'))
	dataSock.close()
	
def quit_command(dataSock):
	dataSock.close()
	
# Accept connections forever
if __name__ == '__main__':
	end = True
	print("Waiting for connections...")
				
	# Accept connections
	clientSock, addr = welcomeSock.accept()
		
	print("Accepted connection from client: ", addr)
	print("\n")
	while end:

		command = clientSock.recv(1)

		dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		dataSock.connect(('0.0.0.0', 1235))

		if(command == b'p'):
			put_command(dataSock)

		if(command == b'g'):
			fNamelen = dataSock.recv(2).decode('ascii')
			fName = dataSock.recv(int(fNamelen)).decode('ascii')
			get_command(fName, dataSock)

		if(command == b'l'):
			ls_command(dataSock)

		if(command == b'q'):
			quit_command(dataSock)
		
		if(command == b'e'):
			end = False
