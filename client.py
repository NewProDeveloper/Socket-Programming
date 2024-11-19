import socket
import struct
import json
import tkinter as tk
from tkinter import ttk
import threading

def parse_packet(packet):
    header, timestamp = struct.unpack('!II', packet[:8])
    sequence_number = header & 0xFFFF
    payload = packet[12:] 
    return sequence_number, timestamp, payload

class Client:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Stock Prices")
        self.root.geometry("600x400")
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        style = ttk.Style()
        style.configure("Stock.TLabel", font=('Helvetica', 12))
        style.configure("Price.TLabel", font=('Helvetica', 12, 'bold'))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))
        
        ttk.Label(main_frame, text="Stock Name", style="Header.TLabel").grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(main_frame, text="Current Price", style="Header.TLabel").grid(row=0, column=1, padx=10, pady=10)
        ttk.Label(main_frame, text="Change", style="Header.TLabel").grid(row=0, column=2, padx=10, pady=10)
        
        self.stock_labels = {}
        self.price_labels = {}
        self.change_labels = {}
        self.previous_prices = {}
        
        stocks = ['SBIN', 'MRF', 'RTNPWR', 'YESBANK']
        for idx, stock in enumerate(stocks, 1):
            self.stock_labels[stock] = ttk.Label(main_frame, text=stock, style="Stock.TLabel")
            self.stock_labels[stock].grid(row=idx, column=0, padx=10, pady=5)
            
            self.price_labels[stock] = ttk.Label(main_frame, text="--", style="Price.TLabel")
            self.price_labels[stock].grid(row=idx, column=1, padx=10, pady=5)
            
            self.change_labels[stock] = ttk.Label(main_frame, text="--", style="Price.TLabel")
            self.change_labels[stock].grid(row=idx, column=2, padx=10, pady=5)
            
            self.previous_prices[stock] = None
        
        self.status_var = tk.StringVar(value="Connecting...")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=len(stocks)+1, column=0, columnspan=3, pady=20)
        
        self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
        self.receive_thread.start()
    
    def update_price(self, stock, price):
        self.price_labels[stock].configure(text=f"₹{price:.2f}")
        
        if self.previous_prices[stock] is not None:
            change = price - self.previous_prices[stock]
            change_text = f"{'+' if change >= 0 else ''}{change:.2f}"
            color = 'green' if change >= 0 else 'red'
            self.change_labels[stock].configure(text=change_text, foreground=color)
        
        self.previous_prices[stock] = price
    
    def receive_data(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.bind(('0.0.0.0', 5005))
        
        self.status_var.set("Connected - Receiving Updates")
        
        while True:
            try:
                packet, _ = client_socket.recvfrom(1024)
                _, _, payload = parse_packet(packet)
                
                stock_data = json.loads(payload.decode())
                
                for stock, price in stock_data.items():
                    self.root.after(0, self.update_price, stock, price)
                    
            except Exception as e:
                self.status_var.set(f"Error: {str(e)}")
                break

def start_client():
    root = tk.Tk()
    app = Client(root)
    root.mainloop()

start_client()