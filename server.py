#!/usr/bin/env python3
"""
KomoChat Server - Run this FIRST on any computer
Acts as the middleman for all chats
"""
import socket
import threading
import time
import sys

# Colors for terminal
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def get_local_ip():
    """Get the server's IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

class ChatServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.clients = []  # List of connected clients
        self.nicknames = []  # List of client nicknames
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def start(self):
        """Start the chat server"""
        try:
            self.server.bind((self.host, self.port))
            self.server.listen()
            
            local_ip = get_local_ip()
            
            print(f"{Colors.CYAN}{'═'*50}")
            print(f"     {Colors.BOLD}KOMOCHAT SERVER STARTED!{Colors.END}{Colors.CYAN}")
            print(f"{'═'*50}{Colors.END}")
            print(f"{Colors.GREEN}✓ Server IP: {local_ip}")
            print(f"✓ Port: {self.port}")
            print(f"✓ Status: Waiting for connections...{Colors.END}")
            print(f"\n{Colors.YELLOW}Share this IP with your friends!")
            print("They need to connect to this IP{Colors.END}\n")
            
            # Start accepting connections
            self.accept_connections()
            
        except Exception as e:
            print(f"{Colors.RED}Error starting server: {e}{Colors.END}")
            input("Press Enter to exit...")
    
    def accept_connections(self):
        """Accept incoming client connections"""
        while True:
            try:
                client, address = self.server.accept()
                print(f"{Colors.GREEN}✓ New connection from {address[0]}{Colors.END}")
                
                # Ask for nickname
                client.send("NICK".encode('utf-8'))
                nickname = client.recv(1024).decode('utf-8')
                
                self.clients.append(client)
                self.nicknames.append(nickname)
                
                print(f"{Colors.CYAN}✓ {address[0]} joined as '{nickname}'{Colors.END}")
                
                # Send welcome message
                client.send(f"Connected to KomoChat Server!\nUsers online: {len(self.clients)}".encode('utf-8'))
                
                # Broadcast new user joined
                self.broadcast(f"🎉 {nickname} joined the chat!", client)
                
                # Start thread for this client
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()
                
            except Exception as e:
                print(f"{Colors.RED}Connection error: {e}{Colors.END}")
                break
    
    def broadcast(self, message, sender_client=None):
        """Send message to all connected clients"""
        for client in self.clients:
            try:
                if client != sender_client:  # Don't send to sender
                    client.send(message.encode('utf-8'))
            except:
                # Remove disconnected client
                self.remove_client(client)
    
    def handle_client(self, client):
        """Handle messages from a client"""
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                
                if not message:
                    # Client disconnected
                    self.remove_client(client)
                    break
                
                # Get client index
                index = self.clients.index(client)
                nickname = self.nicknames[index]
                
                print(f"{Colors.CYAN}[{nickname}]: {message}{Colors.END}")
                
                # Broadcast message to all other clients
                broadcast_msg = f"[{nickname}]: {message}"
                self.broadcast(broadcast_msg, client)
                
            except:
                self.remove_client(client)
                break
    
    def remove_client(self, client):
        """Remove a disconnected client"""
        if client in self.clients:
            index = self.clients.index(client)
            nickname = self.nicknames[index]
            
            self.clients.remove(client)
            self.nicknames.remove(nickname)
            
            client.close()
            
            print(f"{Colors.YELLOW}✗ {nickname} disconnected{Colors.END}")
            
            # Broadcast user left
            self.broadcast(f"👋 {nickname} left the chat")

def main():
    print(f"{Colors.CYAN}{'═'*50}")
    print(f"     {Colors.BOLD}KOMOCHAT - TERMINAL CHAT SERVER{Colors.END}{Colors.CYAN}")
    print(f"{'═'*50}{Colors.END}")
    
    # Get port
    port = input(f"{Colors.YELLOW}Enter port [9999]: {Colors.END}").strip()
    if not port:
        port = 9999
    else:
        try:
            port = int(port)
        except:
            port = 9999
    
    # Start server
    server = ChatServer(port=port)
    server.start()

if __name__ == "__main__":
    main()
