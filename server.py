import socket
from udptcpconverter import TCPSegment, Request, Response, verify_checksum
import json
import time
from queue import Queue

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("127.0.0.1", 12345))

# Global variables
availableWebsite = "/website/page.html"
timeout_period = 5
sequence_number = 1  # Starting sequence number
response_queue = Queue()


def generatePackets():
    for i in range(1, 16):
        data = f"this is data for packet {i}"
        response = Response(statLine="HTTP/1.0 200 OK", connection="keep-alive", date="", server="", lastMod="", length=15, type="", data=data)
        response_queue.put(response)



def receive_ack(client_socket):
    try:
        client_socket.settimeout(timeout_period)
        data, address = client_socket.recvfrom(1024)
        ack_packet = json.loads(data.decode('utf-8'))
        return ack_packet
    except socket.timeout:
        return None

# Handshake
data, address = server.recvfrom(1024)
packet_data = json.loads(data.decode('utf-8'))
handshake_segment = TCPSegment(**packet_data)   
if (handshake_segment.SYN):
    handshake_segment.ACK=1
    handshake_data = json.dumps(handshake_segment.__dict__)

    print("Server sending  TCPSegment:", handshake_segment)
    server.sendto(handshake_data.encode('utf-8'),address)     
else:
    print("Could Not Establish Connection 1")    
    
data2, address2 = server.recvfrom(1024)
packet_data2 = json.loads(data2.decode('utf-8'))
confirm_segment = TCPSegment(**packet_data2)
print(confirm_segment)
if (confirm_segment.ACK == 1 and confirm_segment.SYN==0):
    print("Connection Established")


# Loop for handling requests
while True:
    generatePackets()
   
    # Receive request
    request_data, address = server.recvfrom(1024)
    request_data = json.loads(request_data.decode('utf-8'))
    request_tcp = TCPSegment(**request_data)
    request_json = json.loads(request_data['Data'])
    request = Request(**request_json)

    if request.connection=="close":
        close_tcp=request_tcp
        break


    # Process request
    website = request.url if request.method == "GET" else request.entityBody
    if website == availableWebsite and (request.method!="GET" or request.method!="POST"):
        # Process response
        while not response_queue.empty():
            response = response_queue.get()
            print("-------------------------------------------------------------------------------")
            
            responseTCP = TCPSegment(SYN=987, ACK=0, FIN=0, SEQ=sequence_number, ACKNUM=0, Checksum=0, Data=json.dumps(response.__dict__))  
            responseTCPByte=responseTCP.calculate_checksum()
            server.sendto(json.dumps(responseTCP.__dict__).encode('utf-8'), address)
            print("Sequence Number Sent: ", responseTCP.SEQ)
            
            # Wait for acknowledgment
            ack_received = False
            while not ack_received:

                ack_packet = receive_ack(server)    
                if ack_packet and ack_packet["ACKNUM"] == sequence_number:
                    print("Recieved ACK: ", ack_packet["ACKNUM"] )
                    ack_received = True
                else:
                    # responseTCPByte=responseTCP.calculate_checksum()
                    print("Retransmitting Packet with Sequence NUmber: " ,responseTCP.SEQ)
                    server.sendto(json.dumps(responseTCP.__dict__).encode('utf-8'), address)

            # Increment sequence number for next packet
            sequence_number += 1

        print("All Responses Sent")
        time.sleep(10)
        
    else:

        response = Response(statLine="HTTP/1.0 404 NOT FOUND",connection="keep-alive",date="", server="", lastMod="",length=0,type="",data="")  # Empty data field
        responseTCP = TCPSegment(SYN=0, ACK=0, FIN=0, SEQ=0, ACKNUM=0, Checksum=0, Data=json.dumps(response.__dict__))
        server.sendto(json.dumps(responseTCP.__dict__).encode('utf-8'), address)
        print("The response: " + response.statLine + " is sent to client")
        



print("-------------------------------------------------------------------------------")
# CLOSE CONNECTION
# close_data, address = server.recvfrom(1024)
# close_data = json.loads(close_data.decode('utf-8'))
# close_tcp = TCPSegment(**close_data)
close_tcp.ACK = 1
close_tcp.SEQ =0
close_tcp.SEQ = close_tcp.SEQ + 1
server.sendto(json.dumps(close_tcp.__dict__).encode('utf-8'), address)
print("Sending to client: ", close_tcp)

close_packet = TCPSegment(SYN=0, ACK=0, FIN=1, SEQ=600, ACKNUM=0, Checksum=0, Data=" ")
close_data = json.dumps(close_packet.__dict__)
server.sendto(close_data.encode('utf-8'), address)
print("Sending to client: ", close_packet)

close_ack, address = server.recvfrom(1024)
close_ack = json.loads(close_ack.decode('utf-8'))
close_ack_tcp = TCPSegment(**close_ack)
print("Server Closed Connection")

server.close()
