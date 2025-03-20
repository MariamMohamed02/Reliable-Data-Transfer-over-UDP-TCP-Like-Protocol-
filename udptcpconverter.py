import json
import socket
import zlib

class TCPSegment:
    def __init__(self, SYN: int, ACK: int, FIN: int, SEQ: int, ACKNUM: int, Checksum: int, Data: str):
        self.SYN = SYN
        self.ACK = ACK
        self.FIN = FIN
        self.SEQ = SEQ
        self.ACKNUM = ACKNUM
        self.Checksum = Checksum
        self.Data = Data

    def calculate_checksum(self):
        responseTCPByte = json.dumps(self.__dict__)
        checksum=zlib.crc32(responseTCPByte.encode('utf-8'))
        self.Checksum=checksum
        print("Calculated checksum:", checksum)

    def __str__(self):
        return f"SYN: {self.SYN}, ACK: {self.ACK}, FIN: {self.FIN}, SEQ: {self.SEQ}, ACKNUM: {self.ACKNUM}, Checksum: {self.Checksum}, Data: {self.Data}"


# def receive_packet(socket):
#     data, address = socket.recvfrom(1024)
#     packet_data = json.loads(data.decode('utf-8'))
#     packet = TCPSegment(**packet_data)
#     return packet

def verify_checksum(packetRespone):
    sentChecksum=packetRespone.Checksum
    packetRespone.Checksum=0
    responseTCPByte = json.dumps(packetRespone.__dict__)
    calculated_checksum=zlib.crc32(responseTCPByte.encode('utf-8'))
    return calculated_checksum == sentChecksum

def simulate_false_checksum(packet):
    packet.Checksum = packet.Checksum + 1  # Simulating a false checksum by incrementing it


class Request:
    def __init__(self, reqLine: str, host: str, connection: str, userAgent: str, accLang: str, entityBody: str, method:str, url:str,version:str):
        self.reqLine = reqLine
        self.host = host
        self.connection = connection
        self.userAgent = userAgent
        self.accLang = accLang
        self.entityBody = entityBody
        self.method=method
        self.url=url
        self.version=version
        
        # Parse reqLine into method, url, and version
        parts = reqLine.split()
        self.method = parts[0] if parts else ""
        self.url = ""
        self.version = parts[-1] if parts else ""

        # Check if method is GET or POST, adjust url and entityBody accordingly
        if self.method == "GET":
            self.url = ' '.join(parts[1:-1]) if len(parts) > 2 else ""
        elif self.method == "POST":
            self.entityBody = ' '.join(parts[1:-1]) if len(parts) > 2 else ""

    def __str__(self):
        return f"Method: {self.method}, URL: {self.url}, Version: {self.version}, Host: {self.host}, Connection: {self.connection}, User-Agent: {self.userAgent}, Accept-Language: {self.accLang}, Entity-Body: {self.entityBody}"


class Response:
    def __init__(self, statLine: str, connection: str, date: str, server: str, lastMod: str, length: int, type: str, data: str):
        self.statLine = statLine
        self.connection = connection
        self.date = date
        self.server = server
        self.lastMod = lastMod
        self.length = length
        self.type = type
        self.data = data

    def __str__(self):
        return f"Status Line: {self.statLine}, Connection: {self.connection}, Date: {self.date}, Server: {self.server}, Last Modified: {self.lastMod}, Length: {self.length}, Type: {self.type}, Data: {self.data}"



def receive_packet(socket):
    data, address = socket.recvfrom(1024)
    packet_data = json.loads(data.decode('utf-8'))
    packet = TCPSegment(**packet_data)
    return packet


def receive_packetRES(socket):
    request_data, address = socket.recvfrom(1024)
    request_data = json.loads(request_data.decode('utf-8'))
    requestTCP=TCPSegment(**request_data)
    request_json = json.loads(request_data['Data'])  # Deserialize the data field
    request = Request(**request_json)
    return request



