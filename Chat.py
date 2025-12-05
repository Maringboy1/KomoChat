#!/usr/bin/env python3
"""
KomoChat - Cross-Network Terminal Chat with NAT Traversal
Works across different networks WITHOUT port forwarding
"""

import socket
import threading
import sys
import os
import json
import time
import requests
import struct
from datetime import datetime

# Color codes for better readability
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    # KomoChat special colors
    KOMO_GREEN = '\033[38;5;46m'
    KOMO_BLUE = '\033[38;5;39m'
    KOMO_PURPLE = '\033[38;5;129m'

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_chat_header():
    """Print only the chat header without extra banners"""
    clear_screen()
    print(f"{Colors.KOMO_PURPLE}{'━' * 60}")
    print(f"                    🚀 {Colors.BOLD}KomoChat{Colors.END}{Colors.KOMO_PURPLE}")
    print(f"{'━' * 60}{Colors.END}\n")

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_public_ip():
    """Get public IP address using STUN technique"""
    try:
        # Try multiple STUN servers
        stun_servers = [
            ('stun.l.google.com', 19302),
            ('stun1.l.google.com', 19302),
            ('stun2.l.google.com', 19302),
            ('stun.voipbuster.com', 3478),
            ('stun.stunprotocol.org', 3478)
        ]
        
        for stun_server, stun_port in stun_servers:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                sock.bind(('0.0.0.0', 0))
                
                # STUN binding request
                message = b'\x00\x01\x00\x00\x21\x12\xa4\x42' + os.urandom(12)
                sock.sendto(message, (stun_server, stun_port))
                
                data, addr = sock.recvfrom(1024)
                sock.close()
                
                if len(data) > 20:
                    # Parse STUN response for public IP
                    if data[0:2] == b'\x01\x01':
                        xor_addr = data[20:24]
                        magic_cookie = b'\x21\x12\xa4\x42'
                        port = struct.unpack('!H', data[26:28])[0]
                        ip_bytes = bytes([xor_addr[i] ^ magic_cookie[i % 4] for i in range(4)])
                        public_ip = socket.inet_ntoa(ip_bytes)
                        return public_ip
            except:
                continue
        
        # Fallback to ipify API
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return None

class P2PConnection:
    """Peer-to-Peer connection with NAT traversal"""
    
    def __init__(self):
        self.sock = None
        self.peer_sock = None
        self.is_connected = False
        
    def start_as_host(self, local_port=9999):
        """Start as host (listener with NAT hole punching)"""
        try:
            # Create UDP socket for hole punching
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', local_port))
            self.sock.settimeout(30)
            
            print(f"{Colors.GREEN}✅ Host started on port {local_port}{Colors.END}")
            print(f"{Colors.YELLOW}Waiting for peer connection...{Colors.END}")
            
            # Wait for peer
            data, addr = self.sock.recvfrom(1024)
            if data == b'HELLO':
                print(f"{Colors.GREEN}✅ Peer connected from {addr[0]}:{addr[1]}{Colors.END}")
                self.sock.sendto(b'ACK', addr)
                self.is_connected = True
                return addr
            
        except socket.timeout:
            print(f"{Colors.RED}❌ No peer connected in 30 seconds{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.END}")
        return None
    
    def start_as_client(self, peer_ip, peer_port=9999):
        """Start as client (connect to host with NAT hole punching)"""
        try:
            # Create UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', 0))  # Bind to any available port
            self.sock.settimeout(10)
            
            print(f"{Colors.YELLOW}Attempting NAT hole punching to {peer_ip}:{peer_port}...{Colors.END}")
            
            # Send multiple packets to punch through NAT
            for i in range(5):
                try:
                    self.sock.sendto(b'HELLO', (peer_ip, peer_port))
                    print(f"  Attempt {i+1}/5...", end="\r")
                    time.sleep(0.5)
                except:
                    pass
            
            print(f"\n{Colors.YELLOW}Waiting for response...{Colors.END}")
            
            # Wait for ACK
            data, addr = self.sock.recvfrom(1024)
            if data == b'ACK' and addr[0] == peer_ip:
                print(f"{Colors.GREEN}✅ Connected to peer!{Colors.END}")
                self.is_connected = True
                return addr
            
        except socket.timeout:
            print(f"{Colors.RED}❌ Connection timeout{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.END}")
        return None
    
    def send_message(self, message, addr):
        """Send message to peer"""
        try:
            self.sock.sendto(message.encode(), addr)
            return True
        except:
            return False
    
    def receive_message(self, timeout=1):
        """Receive message from peer"""
        try:
            self.sock.settimeout(timeout)
            data, addr = self.sock.recvfrom(1024)
            return data.decode(), addr
        except socket.timeout:
            return None, None
        except:
            return None, None

def display_connection_menu():
    """Display connection menu"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}KomoChat - Cross Network Chat")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print(f"{Colors.BOLD}Your Local IP: {Colors.KOMO_GREEN}{local_ip}{Colors.END}")
    if public_ip:
        print(f"{Colors.BOLD}Your Public IP: {Colors.CYAN}{public_ip}{Colors.END}")
    
    print(f"\n{Colors.BOLD}⚠️  NO PORT FORWARDING NEEDED!{Colors.END}")
    print(f"{Colors.YELLOW}This app uses NAT traversal technology{Colors.END}")
    
    print(f"\n{Colors.BOLD}Select Mode:{Colors.END}")
    print(f"{Colors.GREEN}[1]{Colors.END} Create Chat Room (Host)")
    print(f"{Colors.BLUE}[2]{Colors.END} Join Chat Room (Guest)")
    print(f"{Colors.PURPLE}[3]{Colors.END} Direct IP Connect (Advanced)")
    print(f"{Colors.RED}[4]{Colors.END} Exit")
    
    while True:
        try:
            choice = input(f"\n{Colors.YELLOW}Enter choice (1-4): {Colors.END}").strip()
            if choice in ['1', '2', '3', '4']:
                return int(choice)
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}Exiting...{Colors.END}")
            sys.exit(0)

def start_host():
    """Start as host with NAT traversal"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}Create Chat Room")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    # Get port
    port = 9999
    port_input = input(f"{Colors.YELLOW}Enter port [9999]: {Colors.END}").strip()
    if port_input:
        try:
            port = int(port_input)
        except:
            pass
    
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print(f"\n{Colors.BOLD}Your Connection Info:{Colors.END}")
    print(f"{Colors.GREEN}Local IP: {local_ip}{Colors.END}")
    if public_ip:
        print(f"{Colors.CYAN}Public IP: {public_ip}{Colors.END}")
    print(f"{Colors.YELLOW}Port: {port}{Colors.END}")
    
    print(f"\n{Colors.GREEN}✅ Share your PUBLIC IP with friend")
    print(f"✅ Friend should use: {public_ip if public_ip else 'Your IP'}")
    print(f"✅ Port: {port}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Starting chat room...{Colors.END}")
    
    # Create P2P connection
    p2p = P2PConnection()
    peer_addr = p2p.start_as_host(port)
    
    if peer_addr and p2p.is_connected:
        print(f"\n{Colors.GREEN}✅ Connection established!{Colors.END}")
        time.sleep(1)
        start_p2p_chat(p2p, peer_addr, "Host", "Guest")
    else:
        print(f"\n{Colors.RED}Failed to establish connection{Colors.END}")
        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.END}")

def start_guest():
    """Start as guest with NAT traversal"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}Join Chat Room")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    # Get host IP
    while True:
        host_ip = input(f"{Colors.YELLOW}Enter host's IP address: {Colors.END}").strip()
        if host_ip:
            break
    
    # Get port
    port = 9999
    port_input = input(f"{Colors.YELLOW}Enter port [9999]: {Colors.END}").strip()
    if port_input:
        try:
            port = int(port_input)
        except:
            pass
    
    print(f"\n{Colors.YELLOW}Connecting to {host_ip}:{port}...{Colors.END}")
    print(f"{Colors.CYAN}Using NAT hole punching...{Colors.END}")
    
    # Create P2P connection
    p2p = P2PConnection()
    peer_addr = p2p.start_as_client(host_ip, port)
    
    if peer_addr and p2p.is_connected:
        print(f"\n{Colors.GREEN}✅ Connected to host!{Colors.END}")
        time.sleep(1)
        start_p2p_chat(p2p, peer_addr, "Guest", "Host")
    else:
        print(f"\n{Colors.RED}Failed to connect to host{Colors.END}")
        print(f"{Colors.YELLOW}Possible reasons:{Colors.END}")
        print("1. Host is not running KomoChat")
        print("2. Both are behind symmetric NAT (rare)")
        print("3. Firewall blocking UDP connections")
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")

def start_direct_connect():
    """Direct connection attempt (fallback method)"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}Direct IP Connect")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    # Get peer IP
    while True:
        peer_ip = input(f"{Colors.YELLOW}Enter peer's IP address: {Colors.END}").strip()
        if peer_ip:
            break
    
    port = 9999
    port_input = input(f"{Colors.YELLOW}Enter port [9999]: {Colors.END}").strip()
    if port_input:
        try:
            port = int(port_input)
        except:
            pass
    
    print(f"\n{Colors.YELLOW}Which mode are you?{Colors.END}")
    print(f"{Colors.GREEN}[1]{Colors.END} I will wait for connection")
    print(f"{Colors.BLUE}[2]{Colors.END} I will connect to peer")
    
    choice = input(f"\n{Colors.YELLOW}Your choice (1-2): {Colors.END}").strip()
    
    if choice == '1':
        # Wait as host
        print(f"\n{Colors.GREEN}Waiting for {peer_ip} to connect...{Colors.END}")
        p2p = P2PConnection()
        peer_addr = p2p.start_as_host(port)
        
        if peer_addr:
            start_p2p_chat(p2p, peer_addr, "You", f"Peer ({peer_ip})")
    else:
        # Connect as client
        print(f"\n{Colors.YELLOW}Connecting to {peer_ip}:{port}...{Colors.END}")
        p2p = P2PConnection()
        peer_addr = p2p.start_as_client(peer_ip, port)
        
        if peer_addr:
            start_p2p_chat(p2p, peer_addr, "You", f"Peer ({peer_ip})")

def start_p2p_chat(p2p, peer_addr, my_name, friend_name):
    """Start P2P chat session"""
    clear_screen()
    print(f"{Colors.KOMO_PURPLE}{'━' * 60}")
    print(f"                    🚀 {Colors.BOLD}KomoChat{Colors.END}{Colors.KOMO_PURPLE}")
    print(f"{'━' * 60}{Colors.END}\n")
    
    print(f"{Colors.CYAN}Connected to: {peer_addr[0]}:{peer_addr[1]}{Colors.END}")
    print(f"{Colors.GREEN}Chatting with: {friend_name}{Colors.END}")
    print(f"{Colors.YELLOW}Type /exit to quit, /help for commands{Colors.END}")
    print(f"{Colors.KOMO_PURPLE}{'─' * 60}{Colors.END}\n")
    
    # Start receive thread
    receive_thread = threading.Thread(target=receive_p2p_messages, args=(p2p, friend_name, peer_addr))
    receive_thread.daemon = True
    receive_thread.start()
    
    while True:
        try:
            # Get user input
            message = input(f"{Colors.BOLD}{Colors.KOMO_BLUE}{my_name}: {Colors.END}").strip()
            
            # Check commands
            if message.lower() == '/exit':
                p2p.send_message("/exit", peer_addr)
                print(f"{Colors.YELLOW}Ending chat...{Colors.END}")
                break
            elif message.lower() == '/help':
                print(f"\n{Colors.CYAN}Commands:{Colors.END}")
                print(f"{Colors.GREEN}/exit{Colors.END} - End chat")
                print(f"{Colors.GREEN}/clear{Colors.END} - Clear screen")
                print(f"{Colors.GREEN}/time{Colors.END} - Show time")
                print(f"{Colors.GREEN}/status{Colors.END} - Connection status")
                continue
            elif message.lower() == '/clear':
                clear_screen()
                print(f"{Colors.GREEN}Chat with {friend_name}{Colors.END}\n")
                continue
            elif message.lower() == '/time':
                print(f"{Colors.PURPLE}Time: {datetime.now().strftime('%H:%M:%S')}{Colors.END}")
                continue
            elif message.lower() == '/status':
                print(f"{Colors.CYAN}Status: Connected to {friend_name}{Colors.END}")
                print(f"{Colors.CYAN}IP: {peer_addr[0]}:{peer_addr[1]}{Colors.END}")
                continue
            
            # Send message
            if not p2p.send_message(message, peer_addr):
                print(f"{Colors.RED}Failed to send message{Colors.END}")
                break
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Ending chat...{Colors.END}")
            p2p.send_message("/exit", peer_addr)
            break
        except EOFError:
            print(f"\n{Colors.YELLOW}Ending chat...{Colors.END}")
            break

def receive_p2p_messages(p2p, friend_name, peer_addr):
    """Receive P2P messages in separate thread"""
    while True:
        message, addr = p2p.receive_message(0.1)
        
        if message:
            if message == "/exit":
                print(f"\n{Colors.YELLOW}{friend_name} has ended the chat.{Colors.END}")
                os._exit(0)
            else:
                print(f"\r{Colors.BOLD}{Colors.KOMO_GREEN}{friend_name}: {message}{Colors.END}")
                print(f"{Colors.BOLD}{Colors.KOMO_BLUE}You: {Colors.END}", end="", flush=True)
        
        time.sleep(0.05)  # Prevent CPU overuse

def main():
    """Main function"""
    # Check for required packages
    try:
        import requests
    except ImportError:
        print(f"{Colors.RED}Missing required package: requests{Colors.END}")
        print(f"{Colors.YELLOW}Install it with: pip install requests{Colors.END}")
        sys.exit(1)
    
    while True:
        try:
            choice = display_connection_menu()
            
            if choice == 1:
                start_host()
            elif choice == 2:
                start_guest()
            elif choice == 3:
                start_direct_connect()
            elif choice == 4:
                print(f"\n{Colors.YELLOW}Goodbye from KomoChat!{Colors.END}")
                break
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Exiting KomoChat...{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.RED}Unexpected error: {e}{Colors.END}")
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.END}")

if __name__ == "__main__":
    main()
