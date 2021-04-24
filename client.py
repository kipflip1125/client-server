# *******************************************************************
# This file illustrates how to send a file using an
# application-level protocol where the first 10 bytes
# of the message from client to server contain the file
# size and the rest contain the file data.
# *******************************************************************
import socket
import os
import sys
from waiting import wait, TimeoutExpired


class Socket:
    def __init__(self):
        self.data = None

    def execute(self, func, *_args, **_kwargs):
        self.data = func(*_args, **_kwargs)
        return True if self.data else False


def recvAll(sock, numBytes):
    # The buffer
    recvBuff = ""

    # The temporary buffer
    tmpBuff = ""

    # Keep receiving till all is received
    retry_count = 0
    _socket = Socket()

    while len(recvBuff) < numBytes:
        try:
            wait(lambda: _socket.execute(sock.recv, numBytes), sleep_seconds=5)
            break
        except TimeoutExpired:
            retry_count += 1

            if retry_count >= 5:
                return ""
        # Attempt to receive bytes

        tmpBuff = _socket.data.decode('ascii')

        # The other side has closed the socket
        if not tmpBuff:
            break

        # Add the received bytes to the buffer
        recvBuff += tmpBuff

    return recvBuff


# Receive Data
def get_command(file, dataSock):
    fNamelen = len(file)
    fNamelen = str(fNamelen).rjust(2, '0')

    retry_count = 0
    _socket = Socket()

    while True:
        try:
            wait(lambda: _socket.execute(dataSock.send, str(fNamelen).encode('ascii')), sleep_seconds=5)
            break
        except TimeoutExpired:
            retry_count += 1

            if retry_count >= 5:
                dataSock.close()
                return

    retry_count = 0

    while True:
        try:
            wait(lambda: _socket.execute(dataSock.send, file.encode('ascii')), sleep_seconds=5)
            break
        except TimeoutExpired:
            retry_count += 1

            if retry_count >= 5:
                dataSock.close()
                return

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

    retry_count = 0

    while True:
        try:
            wait(lambda: _socket.execute(recvAll, dataSock, 10), sleep_seconds=5)
            break
        except TimeoutExpired:
            retry_count += 1

            if retry_count >= 5:
                dataSock.close()
                return

    # Receive the first 10 bytes indicating the
    # size of the file
    fileSizeBuff = _socket.data

    # Get the file size
    fileSize = int(fileSizeBuff)

    print("The file size is ", fileSize)

    retry_count = 0

    while True:
        try:
            wait(lambda: _socket.execute(recvAll, dataSock, fileSize), sleep_seconds=5)
            break
        except TimeoutExpired:
            retry_count += 1

            if retry_count >= 5:
                dataSock.close()
                return

    # Get the file data
    fileData = _socket.data

    print("The file data is: ")
    print(fileData)

    # Close our side
    print('Received ', fileSize, ' bytes')
    dataSock.close()


# Send Data
def put_command(file, dataSock):
    # Open the file
    fileObj = open(file, "r")

    # The number of bytes sent
    numSent = 0

    # The file data
    fileData = None

    _socket = Socket()

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

            retry_count = 0

            # Send the data!
            while len(fileData) > numSent:
                try:
                    wait(lambda: _socket.execute(dataSock.send, fileData[numSent:].encode('ascii')), sleep_seconds=5)
                    numSent += _socket.data
                except TimeoutExpired:
                    retry_count += 1

                    if retry_count >= 5:
                        dataSock.close()
                        return

        # The file has been read. We are done
        else:
            break

    print("Sent ", numSent, " bytes.")
    fileObj.close()
    dataSock.close()


# Print out directory
def ls_command(dataSock):
    numBytes = 0

    _socket = Socket()
    retry_count = 0

    while True:
        try:
            wait(lambda: _socket.execute(dataSock.recv, 2), sleep_seconds=5)
            break
        except TimeoutExpired:
            retry_count += 1

            if retry_count >= 5:
                dataSock.close()
                return

    numFiles = int(_socket.data.decode('ascii'))

    for i in range(numFiles):
        retry_count = 0

        while True:
            try:
                wait(lambda: _socket.execute(dataSock.recv, 2), sleep_seconds=5)
                break
            except TimeoutExpired:
                retry_count += 1

                if retry_count >= 5:
                    dataSock.close()
                    return

        length = int(_socket.data.decode('ascii'))

        retry_count = 0

        while True:
            try:
                wait(lambda: _socket.execute(dataSock.recv, length), sleep_seconds=5)
                break
            except TimeoutExpired:
                retry_count += 1

                if retry_count >= 5:
                    dataSock.close()
                    return

        ls_data = _socket.data.decode('ascii')
        print(ls_data)
        numBytes = numBytes + len(ls_data)
    print('Received ', numBytes, ' bytes.')
    dataSock.close()


# Quit
def quit_command(dataSock):
    dataSock.close()
    quit()


if __name__ == '__main__':

    # Command line checks
    if len(sys.argv) < 2:
        print("USAGE python " + sys.argv[0] + " <FILE NAME>")

    # Server address
    serverAddr = socket.gethostbyname(sys.argv[1])

    # Server port
    serverPort = sys.argv[2]

    connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connSock.connect((serverAddr, int(serverPort)))

    print("Connected to the server socket")

    welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcomeSock.bind(('', 1235))
    while True:
        welcomeSock.listen(1)

        # Get client command
        text = input('ftp>  ')
        args = text.split(' ')

        if (args[0] == 'get'):
            connSock.send(b'g')
            dataSock, addr = welcomeSock.accept()
            get_command(args[1], dataSock)

        if (args[0] == 'put'):
            connSock.send(b'p')
            dataSock, addr = welcomeSock.accept()
            put_command(args[1], dataSock)

        if (args[0] == 'ls'):
            connSock.send(b'l')
            dataSock, addr = welcomeSock.accept()
            ls_command(dataSock)

        if (args[0] == 'quit'):
            connSock.send(b'q')
            dataSock, addr = welcomeSock.accept()
            quit_command(dataSock)

        if (args[0] == 'end'):
            connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connSock.connect((serverAddr, int(serverPort)))
            connSock.send(b'e')
            quit()
