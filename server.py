import socket
import struct
import random
import time
import json

def create_packet(payload, sequence_number):
    version = 2
    padding = 0
    extension = 0
    csrc_count = 0
    marker = 0
    payload_type = 96  
    timestamp = int(time.time())
    ssrc = random.randint(0, 0xFFFFFFFF)

    header = (
        (version << 30) | 
        (padding << 29) | 
        (extension << 28) | 
        (csrc_count << 24) | 
        (marker << 23) | 
        (payload_type << 16) | 
        sequence_number
    )
    
    packet = struct.pack('!II', header, timestamp) + struct.pack('!I', ssrc) + payload

    return packet

def generate_stock_data():
    stocks = {
        'SBIN': round(random.uniform(500, 901), 2),
        'MRF': round(random.uniform(120000, 122200), 2),
        'RTNPWR': round(random.uniform(10, 14), 2),
        'YESBANK': round(random.uniform(18, 22), 2)
    }
    return json.dumps(stocks).encode()

def start_server(host = '0.0.0.0', port = 5004):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    
    print(f"Stock Price Server running on {host}:{port}")
    sequence_number = 0
    
    try:
        while True:
            stock_data = generate_stock_data()
            rtp_packet = create_packet(stock_data, sequence_number)
            server_socket.sendto(rtp_packet, ('127.0.0.1', 5005))
            
            sequence_number = (sequence_number + 1) % 65536
            time.sleep(1)  
            
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        server_socket.close()

start_server()   