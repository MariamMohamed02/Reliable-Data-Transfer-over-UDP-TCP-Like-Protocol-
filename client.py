import socket
from udptcpconverter import TCPSegment, receive_packet, Request, Response, verify_checksum
import json
import time

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --------------------HANDSHAKE ----------------------------------
# --------------------HANDSHAKE ----------------------------------
# -------------------send SYN =1----------------------------------
handshake = TCPSegment(SYN=1, ACK=0, FIN=0, SEQ=0, ACKNUM=0, Checksum=0, Data=" ")
handshake_data = json.dumps(handshake.__dict__)
client.sendto(handshake_data.encode('utf-8'), ("127.0.0.1", 12345))
# --------------------Wait for SYN=1 ACK=1-------------------------
print("Waiting for response from server...")
handshake_segment = receive_packet(client)
print(handshake_segment)
print("Received TCPSegment:", handshake_segment)

if handshake_segment.SYN and handshake_segment.ACK:
    handshake_segment.SYN = 0
    data = json.dumps(handshake_segment.__dict__)
    client.sendto(data.encode('utf-8'), ("127.0.0.1", 12345))
    print("Connection Established")
else:
    print("Could Not Establish Connection")

print("---------------------------------------------------------------")

#  ----------------CONNECTION ESTABLISHED -----------------------
expected_acknum = 1
while True:
    # ----------------Client Create Request-------------------------
    user_input = input("Enter your request (e.g., GET /website/page.html HTTP/1.0): ")
    if user_input.lower() == "close":
        request = Request(reqLine="", host="", connection="close", userAgent="", accLang="", entityBody="", method="", url="", version="")
        print("The Close request is made:")
        print(request)
        print("---------------------------------------------------------------")
        # ----------------Client Sends Request to Server-------------------------
        close_data = json.dumps(request.__dict__)
        close_packet = TCPSegment(SYN=0, ACK=0, FIN=1, SEQ=500, ACKNUM=0, Checksum=0, Data=close_data)
        
        client.sendto(json.dumps(close_packet.__dict__).encode('utf-8'), ("127.0.0.1", 12345))
        print("Sending to server: ", close_packet)

        close_ack = receive_packet(client)
        print("Received from server: ", close_ack)

        close_ack.ACK = 1
        close_ack.ACKNUM = close_ack.ACKNUM + 1
        client.sendto(json.dumps(close_ack.__dict__).encode('utf-8'), ("127.0.0.1", 12345))
        print("Client TIME WAIT to close connection")
        time.sleep(5)
        print("Client Close Connection")
        client.close()
        break
        

    req_line = user_input.strip()

        # Set other attributes
    host = ""
    connection = "keep-alive"
    user_agent = ""
    accepted_language = ""
    entity_body = ""

    # Create a new instance of the Request class
    request = Request(reqLine=req_line, host=host, connection=connection, userAgent=user_agent, accLang=accepted_language, entityBody=entity_body, method="", url="", version="")
    print("The following Request is created and sent to server:")
    print(request)
    print("---------------------------------------------------------------")

    # ----------------Client Sends Request to Server-------------------------
    request_json = json.dumps(request.__dict__)
    request_tcp = TCPSegment(SYN=0, ACK=1, FIN=0, SEQ=0, ACKNUM=0, Checksum=0, Data=request_json)
    # request_tcp.Checksum = request_tcp.calculate_checksum()  # Calculate checksum
    client.sendto(json.dumps(request_tcp.__dict__).encode('utf-8'), ("127.0.0.1", 12345))

    # ----------------Receive Response from the server-------------------------
    response_tcp = receive_packet(client)
    firstchecksum=response_tcp.Checksum
    response_json = json.loads(response_tcp.Data)
    response = Response(**response_json)
    # expected_acknum = 1
    buffer=[None] * 1000
    import random
    checksumError = 3
    packetLossError= 8

    if response.statLine == "HTTP/1.0 404 NOT FOUND":
        # Code to close connection
        print("404 Response Received")
        
    else:
        if verify_checksum(response_tcp):
            print("-------------------------------------------------------------------------------")
            print(response.statLine, response.data)
            print("checksum is: ", firstchecksum)
            ack_packet = TCPSegment(SYN=0, ACK=1, FIN=0, SEQ=0, ACKNUM=expected_acknum, Checksum=0, Data="")
            # ack_packet.Checksum = ack_packet.calculate_checksum()  # Calculate checksum
            client.sendto(json.dumps(ack_packet.__dict__).encode('utf-8'), ("127.0.0.1", 12345))
            print("ACK sent to server with ACKNUM:", expected_acknum)
            size=response.length
            currentSize=1
            buffer[1]=response_tcp

            expected_acknum += 1
            while currentSize<size:
                # Receive next packet from server
                response_tcp = receive_packet(client)
                response_json = json.loads(response_tcp.Data)
                response = Response(**response_json)

                # Check if packet is not a duplicate
                if response_tcp.SEQ == expected_acknum:
                    # GENERATE RANDOM ERROR AT ONE OF THE RECIEVED PACKETS FOR CHECKSUM
                    if response_tcp.SEQ==checksumError:
                        response_tcp.Checksum=response_tcp.Checksum*1000
                        checksumError=0

                    if packetLossError==response_tcp.SEQ:
                        lose = receive_packet(client)
                        packetLossError=0
                        print("Client is waiting for retransmission, packet lost")
                        continue
                        
                    print("-------------------------------------------------------------------------------")
                    # Checksum verification
                    print("checksum is: ",response_tcp.Checksum)
                    if verify_checksum(response_tcp):

                        print(response.statLine, response.data)
                        # print("checksum is: ",response_tcp.Checksum)
                        # Send ACK
                        ack_packet = TCPSegment(SYN=0, ACK=1, FIN=0, SEQ=0, ACKNUM=expected_acknum, Checksum=0, Data="")
                        # ack_packet.Checksum = ack_packet.calculate_checksum()  # Calculate checksum
                        client.sendto(json.dumps(ack_packet.__dict__).encode('utf-8'), ("127.0.0.1", 12345))
                        print("ACK sent to server with ACKNUM:", expected_acknum)
                        currentSize+=1
                        # print(currentSize)
                        buffer[currentSize]=response_tcp
                        # print("Put in buffer",buffer[currentSize])

                        expected_acknum += 1
                    else:
                        print("Checksum is incorrect. Discarding packet.")
                        
                else:
                    print("Duplicate packet received. Discarding packet.")
        else:
            print("Checksum is incorrect. Discarding packet.")


    print("-------------------------------------------------------------------------------")
    #

