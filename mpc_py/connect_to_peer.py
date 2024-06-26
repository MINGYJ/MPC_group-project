import socket
import threading
from color_output import *
import os
import glob

class connect_to_peer:

    def __init__(self,command,client) -> None:
        # Breaks the thread if needed
        self.break_thread=False
        # Retrieves local client information
        self.command=command
        client=client.getsockname()
        self.host = client[0]
        # Port is the share port, we use port+1 to avoid conflict
        self.port = client[1]+1
        # Merge port is the port to send the merged data to, we use port+2 to avoid conflict
        self.merge_port = client[1]+2
        # Create the TCP socket and begin listening for incoming connections
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        print("Peer Server is listening on",self.host,":",self.port)

        self.merge_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.merge_server.bind((self.host, self.merge_port))
        self.merge_server.listen()
        print("Peer Merge Server is listening on",self.host,":",self.merge_port)

        # Keeps track of the current client list.
        self.client_list=[]

        # Start sending and receving at same time to reduce runtime
        # The main method will call send when needed

        threading.Thread(target=self.receive).start()
        threading.Thread(target=self.merge_receive).start()



    def receive(self):
        while True:
            if self.break_thread==True:
                print("Breaking thread")
                break
            try:
                # Ability to accept connections.
                client, address = self.server.accept()
                print(f"Connected to {str(address)}")

                # Add to list of active clients and starts a new thread.
                self.client_list.append(client)
                threading.Thread(target=self.handle, args=(client,)).start()
            except Exception as e:
                print("Error receiving connection: ", e)


    def handle(self,client):
        try: 
            calc, stats = self.command[1], self.command[2]
            file_name=str(calc)+"_"+str(stats)+"_"+len(self.client_list)+".txt"
            with open('../share_received/'+file_name,'w+') as f:
                while (l):
                    l = client.recv(1024)
                    f.write(l.decode('ascii'))
            prCyan("Done receiving.")
        except Exception as e:
            print("Error in handling client data:", e)
        finally:
            client.close()


    def send(self,merge=False):
        peer_lists = self.command[3]  # List of peers to send data to
        for peer in peer_lists:
            send_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
            try:
                if merge:
                    peer[1]=peer[1]+1
                    # Merge port is the share port plus 1, server port plus 2

                send_client.connect((peer[0], peer[1]))
                # Print statement for peer connection clarification
                print(f"Connected to peer {peer[0]} on port {peer[1]}")
                
                file_name = "./share_to_send/" + str(self.command[1]) + "_" + str(self.command[2]) + "*.txt"
                file_to_send = glob.glob(file_name)
                if file_to_send:
                    with open(file_to_send[0]) as f:
                        print("Currently sending file: ", file_to_send)
                        l = f.read(1024)
                        while (l):
                            send_client.send(l.encode('ascii'))
                            l = f.read(1024)
                    os.remove(file_to_send[0])
            except Exception as e:
                print("Failed to send file.", e)   
            finally:
                send_client.close()
        prCyan("Done Sending All Shares")


    

    def merge_receive(self):
        while True:
            if self.break_thread==True:
                break
            try:
                # Ability to accept connections
                client, address = self.merge_server.accept()
                print(f"Connected to {str(address)}")

                threading.Thread(target=self.merge_handle, args=(client,)).start()
            except Exception as e:
                print("Error receiving connection: ", e)


    def merge_handle(self,client):
        try: 
            calc, stats = self.command[1], self.command[2]
            file_name="merge_"+str(calc)+"_"+str(stats)+"_"+len(self.client_list)+".txt"
            with open('../ready_to_merge/'+file_name,'w+') as f:
                while (l):
                    l = client.recv(1024)
                    f.write(l.decode('ascii'))
            prCyan("Done receiving merge file.")
        except Exception as e:
            print("Error in handling client data:", e)
        finally:
            client.close()


                

