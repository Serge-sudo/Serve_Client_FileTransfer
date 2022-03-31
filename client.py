import socket
import sys
import threading


class Client_:
    def __init__(self):

        self.HOST = socket.gethostname()
        self.PORT = 1234
        self.max_chunk_size = 1024
        self.file_pos_len = 0
        self.threads_ = []
        self.transfer_end = threading.Condition()
        self.notified_ = False
        self.req_cnt = 0
        self.connected_ = False

    def __del__(self):
        if self.connected_:
            self.socket_.shutdown(socket.SHUT_RDWR)
            self.socket_.close()

    def run(self, sever_t_cnt, server_file_, client_t_cnt, client_file_):
        self.socket_ = self.connect_to_server()
        self.send_req(self.socket_, sever_t_cnt, server_file_)
        self.recive_file_status(self.socket_)              # running data transfer
        file_size_ = self.get_file_info(self.socket_)
        self.create_empty_file(client_file_, file_size_)
        self.get_req(self.socket_, client_t_cnt, client_file_)
        self.success()

    def success(self):
        print("File was successfully copied!")

    def connect_to_server(self):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        error_flag = False
        try:
            socket_.connect(
                (self.HOST, self.PORT)
            )                             # Connecting to server, raising exception if server is down.
        except Exception as e:
            error_flag = True
        if error_flag == True:
            raise Exception("Server is not working!!!")
        self.connected_ = True
        return socket_

    def send_req(self, socket_, thread_cnt, file_name):
        socket_.send(
            bytes(thread_cnt + ":" + file_name, "utf-8")
        )                               # sending file_name and server-thred_count to Server

    def recive_file_status(self, socket_):
        status = int(
            socket_.recv(1).decode("utf-8")
        )                # checking file status, raising error if file wasn't found
        if status == 0:
            raise Exception("File wasn't found")

    def get_chunk(self, socket_, new_file_name):

        file = open(new_file_name, "r+")
        while True:
            self.transfer_end.acquire()
            if self.req_cnt > 0:
                self.req_cnt -= 1
                self.transfer_end.release()
            elif self.notified_ == False:
                self.notified_ = True
                self.transfer_end.notify()
                self.transfer_end.release()     # getting chunks of file content and placing it into new_file
                break
            else:
                self.transfer_end.release()
                break
            try:
                trash, ptr, data = (
                    (socket_.recv(self.file_pos_len + 2 + self.max_chunk_size))
                    .decode("utf-8")
                    .split(":", 2)
                )
            except:
                continue
            file.seek(int(ptr))
            file.write(data)
        file.close()

    def get_file_info(self, socket_):

        file_size = int(socket_.recv(self.max_chunk_size).decode("utf-8"))
        self.file_pos_len = len(
            str(file_size)
        )                           # receiving file size and computing how may packages of data we need to wait for
        self.req_cnt = file_size // self.max_chunk_size + (
            1 if file_size % self.max_chunk_size else 0
        )

        return file_size

    def get_req(self, socket_, thread_cnt, new_file_name):
        self.transfer_end.acquire()
        for i in range(int(thread_cnt)):
            thread = threading.Thread(                  # creating threads to recive data faster
                target=self.get_chunk, args=(socket_, new_file_name)
            )
            thread.daemon = False
            thread.start()
            self.threads_.append(thread)
        self.transfer_end.wait()
        self.transfer_end.release()

    def create_empty_file(self, file_name, file_size):
        with open(file_name, "w") as out:
            pass


if __name__ == "__main__":

    if sys.argv[1] == "0" or sys.argv[1] == "0":
        raise Exception("Can't work without Threads")
    clinet = Client_()
    clinet.run(*sys.argv[1:])
