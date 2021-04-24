Names and Emails
------------------------------------------------
Raphael Andaya - raphyand@csu.fullerton.edu
William Huynh - WilliamTHuynh@csu.fullerton.edu
Kevin Peralta - kevinaperalta@csu.fullerton.edu
Jake Sichley - jsichley@csu.fullerton.edu

Programming Language
------------------------------------------------
Python 3.6 or higher

How to execute the program
------------------------------------------------
The server is ran by inputting the following in a terminal. 
python server.py <PORT NUMBER>
For example: python3 server.py 1234

The ftp client is ran by inputting the following in a terminal. 
client <server machine> <server port>
For example: python3 client.py ecs.fullerton.edu 1234

After connecting to the server, the client prints out ftp>, which allows the user to execute the following commands.
ftp> get <file name> (downloads file <file name> from the server) 
ftp> put <filename> (uploads file <file name> to the server)
ftp> ls (lists files on the server)
ftp> quit (disconnects from the server and exits)


Anything special about the submission that should be noted
------------------------------------------------
Run in a linux enviroment.

The waiting module must be installed. The following command installs it:
pip install waiting or pip3 install waiting
