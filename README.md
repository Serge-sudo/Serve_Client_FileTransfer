# Multithreaded Large File Transfer

To transfer large files efficiently, a multithreaded approach can be used. This involves dividing the file into multiple chunks and transferring each chunk simultaneously using separate threads. 

To use this approach, you can run the provided server and client scripts. 

## Running the Server

To run the server, navigate to the directory containing the `server.py` script and run the following command:

```
python3 server.py
```

## Running the Client

To run the client, navigate to the directory containing the `client.py` script and run the following command:

```
python3 client.py {server_thread_count} {source_file_path} {client_thread_count} {destination_file_path}
```

Here's an example command:

```
python3 client.py 4 source_file.txt 4 dest_file.txt
```

This command will initiate a transfer of the `source_file.txt` file to the `dest_file.txt` file using 4 server threads and 4 client threads. The program will divide the data from the source file into 4 threads on the server-side, and then it will be received by 4 threads on the client-side.

The program is designed to serve several clients simultaneously. For each client request, the program divides the data of the required file between server-threads and then sends it to client-threads, which writes it to the required place.

To stop the server, use Ctrl+C.

Note that if the port is blocked, you may need to wait for about a minute and try again or change the port number in the client class and MultiThreadServer class.
