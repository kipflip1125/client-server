
# *******************************************************************
# This file illustrates how to send a file using an
# application-level protocol where the first 10 bytes
# of the message from client to server contain the file
# size and the rest contain the file data.
# *******************************************************************
import socket
import os
import sys

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

# Receive Data
def get_command(file, serverAddr, serverPort):
	# Create a TCP socket and connect to the address and socket port
	try:
		connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print('Failed to create a socket')

	try:
		connSock.connect((serverAddr, int(serverPort)))
	except:
		print('Failed to connect to ', severAddr, ':', serverPort)

	print("Connected to ", serverAddr, ":", serverPort)
	connSock.send(b'g')
	
	fNamelen = len(file)
	while len(file) < 3:
		fNamelen = "0" + fNamelen

	connSock.send(str(fNamelen).encode('ascii'))
	connSock.send(file.encode('ascii'))
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
	fileSizeBuff = recvAll(connSock, 10)
			
	# Get the file size
	fileSize = int(fileSizeBuff)
		
	print("The file size is ", fileSize)
		
	# Get the file data
	fileData = recvAll(connSock, fileSize)
		
	print("The file data is: ")
	print(fileData)
			
	# Close our side
	numlen = connSock.recv(2).decode('ascii')
	print('Received ', numlen, ' bytes')
	connSock.close()

# Send Data
def put_command(file, serverAddr, serverPort):
	# Create a TCP socket and connect to the address and socket port
	try:
		connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print('Failed to create a socket')

	try:
		connSock.connect((serverAddr, int(serverPort)))
	except:
		print('Failed to connect to ', severAddr, ':', serverPort)

	print("Connected to ", serverAddr, ":", serverPort)
	connSock.send(b'p')

	# Open the file
	fileObj = open(file, "r")
	
	# The number of bytes sent
	numSent = 0

	# The file data
	fileData = None

	# Keep sending until all is sent
	while True:
		
		# Read 65536 bytes of data
		fileData = fileObj.read(65536)

		# Make sure we did not hit EOF
		if fileData:
				
			# Get the size of the data read
			# and convert it to string
			dataSizeStr = str(len(fileData))
			
			# Prepend 0's to the size string
			# until the size is 10 bytes
			while len(dataSizeStr) < 10:
				dataSizeStr = "0" + dataSizeStr
		
			# Prepend the size of the data to the
			# file data.
			fileData = dataSizeStr + fileData	
			
			# The number of bytes sent
			numSent = 0
			
			# Send the data!
			while len(fileData) > numSent:
				try:
					numSent += connSock.send(fileData[numSent:].encode('ascii'))
				except:
					print('Failed to send message')
		
		# The file has been read. We are done
		else:
			break

	print("Sent ", numSent, " bytes.")
	fileObj.close()

# Print out directory
def ls_command(serverAddr, serverPort):
	# Create a TCP socket and connect to the address and socket port
	try:
		connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print('Failed to create a socket')

	try:
		connSock.connect((serverAddr, int(serverPort)))
	except:
		print('Failed to connect to ', severAddr, ':', serverPort)
	
	print("Connected to ", serverAddr, ":", serverPort)
	connSock.send(b'l')
	numBytes = 0
	numFiles = int(connSock.recv(2).decode('ascii'))
	for i in range(numFiles):
		length = connSock.recv(2).decode('ascii')
		ls_data = connSock.recv(int(length)).decode('ascii')
		print(ls_data)
		numBytes = numBytes + len(ls_data)
	print('Received ', numBytes, ' bytes.')
	connSock.close()

# Quit
def quit_command():
	# Create a TCP socket and connect to the address and socket port
	try:
		connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print('Failed to create a socket')

	try:
		connSock.connect((serverAddr, int(serverPort)))
	except:
		print('Failed to connect to ', severAddr, ':', serverPort)

	print("Connected to ", serverAddr, ":", serverPort)

	connSock.send(b'q')
	quit()

if __name__ == '__main__':
	
	# Command line checks 
	if len(sys.argv) < 2:
		print("USAGE python " + sys.argv[0] + " <FILE NAME>")

	# Server address
	serverAddr = socket.gethostbyname(sys.argv[1])

	# Server port
	serverPort = sys.argv[2]

	while True:
		# Get client command
		text = input('ftp>  ')
		args = text.split(' ')
		
		if(args[0] == 'get'):
			get_command(args[1], serverAddr, serverPort)

		if(args[0] == 'put'):
			put_command(args[1], serverAddr, serverPort)

		if(args[0] == 'ls'):
			ls_command(serverAddr, serverPort)

		if(args[0] == 'quit'):
			quit_command()
