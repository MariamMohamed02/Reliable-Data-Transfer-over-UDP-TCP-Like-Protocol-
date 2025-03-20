##  **Description**  
This project implements a **TCP-like reliable data transfer protocol over UDP** in Python. The protocol simulates **TCP’s three-way handshake, packet segmentation, ACK-based acknowledgment, retransmission handling, and connection termination** while using UDP for communication.  

The project consists of three main components:  
- **Client (`client.py`)** – Initiates a connection, sends HTTP-style requests, receives responses, and ensures ordered data delivery.  
- **Server (`server.py`)** – Listens for connections, processes requests, and sends responses with proper sequencing and reliability.  
- **TCP/UDP Converter (`udptcpconverter.py`)** – Defines **custom TCP-like packets**, checksum validation, and packet verification functions.  

The system simulates **packet loss, checksum corruption, and retransmissions**, demonstrating how reliable data transfer can be achieved over an unreliable transport like UDP.  

---

## **Project Structure**  
| File                 | Description |
|----------------------|------------|
| `client.py`         | Implements the client-side communication, sending requests and handling responses. |
| `server.py`         | Implements the server-side logic, receiving requests and sending responses. |
| `udptcpconverter.py` | Defines the TCP-like packet structure, checksum functions, and utility methods. |
| `udptcpconverter.cpython-310.pyc` | Compiled Python file for `udptcpconverter.py` (can be ignored). |

---

##  **How It Works**  

### **1️⃣ Connection Establishment (Handshake)**
- The client starts a **three-way handshake**:
  1. **Client → Server:** Sends a **SYN** packet to initiate a connection.  
  2. **Server → Client:** Responds with **SYN-ACK**.  
  3. **Client → Server:** Sends an **ACK**, confirming the connection.  

### **2️⃣ Data Transfer**
- The client sends an **HTTP-like request** (e.g., `GET /website/page.html HTTP/1.0`).  
- The server processes the request and sends responses in **packets**, each containing:  
  - **Sequence numbers** for order tracking.  
  - **Checksums** to verify integrity.  
  - **ACKs** to confirm receipt.  

### **3️⃣ Error Handling**
- **Simulated Packet Loss** – If a packet is lost, the client **waits for retransmission**.  
- **Checksum Verification** – Ensures data integrity; corrupted packets are discarded.  
- **In-Order Delivery** – Ensures packets arrive in the correct order.  

### **4️⃣ Connection Termination**
- The client or server can initiate a **FIN** (Finish) signal to close the connection gracefully.


-------------------------------------------------------------------------------


##  **How to Run the Project**  

### **1️⃣ Install Python Dependencies**  
Ensure you have Python installed. Then install any required dependencies:  
```bash
pip install json socket zlib
```

### **2️⃣ Start the Server**  
Run the server first so it can listen for incoming connections.  
```bash
python server.py
```

### **3️⃣ Start the Client**  
Once the server is running, start the client.  
```bash
python client.py
```

### **4️⃣ Send a Request**  
When prompted, enter an HTTP-like request, such as:  
```bash
GET /website/page.html HTTP/1.0
```

##  **Screenshots From a Sample Run** 
![image](https://github.com/user-attachments/assets/e7a72734-7e75-4591-8f3b-879d604310be)
![image](https://github.com/user-attachments/assets/ebe65cce-d5a7-4862-9fdc-742350cb622a)
![image](https://github.com/user-attachments/assets/71425205-2dc2-464e-b540-7b11dda46b72)



