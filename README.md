# Serve-Client for Huge file transfer

Server RUN:
python3 server.py

Client RUN:
python3 client.py {Server thread count} {Path to file to be copied} {Client thread count} {Path to file where data should be copied}

ex.
python3 client.py 4 source_file.txt 4 dest_file.txt
Program will divide data from source_file into 4 threads on server-side and then it will be received by 3 threads on client- side.


The program can serve several clients simultaneously
For each client request, the program divides data of the required file between server-threads and then sends it to client-threads which writes it to the required place.

Use Ctrl+C to stop the server.

Also, if you have blinded port, wait about 1 min and try again or change port number in Clinet class and MultiThreadServer class.