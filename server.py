import socket
import threading
import os
import signal
import sys


def signal_handler(sig, frame):
    global server
    del server  # Got SIGINT
    print("Server has been shutdown")
    sys.exit(0)


class MultiThreadCopy:
    def __init__(self, csocket_):
        self.max_chunk_size = 1024
        self.transfer_end = threading.Condition()
        self.finished_threads = 0
        self.client_socket = csocket_

    def run(self):
        self.thread_cnt, self.file_path = self.recive_req(self.client_socket)
        self.check_exists()
        if self.file_exists == False:  # running process of data transfering
            return 0
        self.send_file(self.client_socket, self.thread_cnt, self.file_path)
        return 1

    def check_exists(self):
        self.file_exists = os.path.exists(
            self.file_path
        )                                 # check if file exists and send status to client
        self.client_socket.send(bytes(str(int(self.file_exists)), "utf-8"))

    def recive_req(self, socket_):
        req = (
            (socket_.recv(1024)).decode("utf-8").split(":", 1)
        )                           # getting file_name and thread_count
        return (int(req[0]), req[1])

    def send_chank(self, clientsocket, file_path, ptr, size_, len_of_file_):
        file = open(file_path, "rb")
        file.seek(ptr)
        dev, rem = size_ // (self.max_chunk_size), size_ % (self.max_chunk_size)
        data_chunk_size = (
            self.max_chunk_size + len_of_file_ + 2
        )                                      # in each thread we are dividing data into chunks

        for i in range(dev):
            chunk = file.read(self.max_chunk_size)
            pos = ptr + i * self.max_chunk_size                  # sending whole chunks
            valid_data = ":" + str(pos) + ":" + chunk.decode("utf-8")
            clientsocket.send(
                bytes('0' * (data_chunk_size - len(valid_data)) + valid_data, "utf-8")
            )

        if rem:
            chunk = file.read(rem)
            pos = ptr + dev * self.max_chunk_size
            valid_data = (
                ":" + str(pos) + ":" + chunk.decode("utf-8")
            )                                                    # sending tail chunk
            clientsocket.send(
                bytes('0' * (data_chunk_size - len(valid_data)) + valid_data, "utf-8")
            )

        file.close()

        self.transfer_end.acquire()
        self.finished_threads += 1                     # notifying that job of current thread is done.
        self.transfer_end.notify()
        self.transfer_end.release()

    def send_file_info(self, clientsocket, file_size):
        clientsocket.send(
            bytes(str(file_size), "utf-8")
        )                               # Sending file size to client, to compute how many packages would be sent.

    def send_file(self, clientsocket, thread_cnt, file_path):
        file_size = os.stat(file_path).st_size
        dev, rem = file_size // (self.max_chunk_size), file_size % (self.max_chunk_size)
        chunk_for_one_thread = dev // thread_cnt + (1 if dev % thread_cnt else 0)
        self.send_file_info(clientsocket, file_size)
        threads_ = []
        ptr = 0                                    # dividing data between threads
        self.transfer_end.acquire()
        for i in range(thread_cnt):

            if (
                (ptr + chunk_for_one_thread * self.max_chunk_size) <= file_size
                and chunk_for_one_thread
                and i != thread_cnt - 1                        # threads with full chunks
            ):
                thread_trasfer_data_size = chunk_for_one_thread * self.max_chunk_size
            else:
                thread_trasfer_data_size = file_size - ptr                     # thread with leftovers
            thread = threading.Thread(
                target=self.send_chank,
                args=(
                    clientsocket,
                    file_path,
                    ptr,
                    thread_trasfer_data_size,
                    len(str(file_size)),
                ),
            )
            ptr += thread_trasfer_data_size
            thread.daemon = True
            thread.start()
            threads_.append(thread)
            if ptr == file_size:                    # if whole data was distibuted
                break
        while self.finished_threads != len(threads_):
            self.transfer_end.wait()                     # waiting threads to finish their jobs
        self.transfer_end.release()


class MultiThreadServer:
    def __init__(self):
        self.HOST = socket.gethostname()
        self.PORT = 1234
        self.WORKING_THREAD_CNT = 4
        self.threads_ = []
        self.shutdowned_ = False

    def __del__(self):
        self.shutdowned_ = True
        self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()

    def run(self):
        self.server_socket = self.create_server()
        self.create_listening_threads()

    def create_server(self):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_.bind((self.HOST, self.PORT))                        # creating server
        socket_.listen()
        return socket_

    def worker(self):
        while self.shutdowned_ == False:
            clientsocket, address = self.server_socket.accept()
            print(f"Connection with {address[0]} has been established.")
            mt = MultiThreadCopy(clientsocket)
            success_ = mt.run()
            if success_:          # Body of working thread, each thread will work with one clinet, untill job is done
                print(f"Happy client left ({address[0]})!!")
            else:
                print(f"Unhappy client left ({address[0]})!!")
            clientsocket.shutdown(socket.SHUT_RDWR)
            clientsocket.close()

    def create_listening_threads(self):
        for i in range(self.WORKING_THREAD_CNT):
            thread = threading.Thread(
                target=self.worker
            )                                   # creating working threads, to distribute clients
            thread.daemon = True
            thread.start()
            self.threads_.append(thread)


signal.signal(signal.SIGINT, signal_handler)
server = MultiThreadServer()
server.run()
signal.pause()
