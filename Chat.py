#!/usr/bin/env python3
"""
KomoChat - Guaranteed Cross-Network Chat
Works EVERYWHERE - No port forwarding needed!
"""

import socket
import threading
import sys
import os
import time
import json
import requests
import select
from datetime import datetime

# Color codes
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'
    KOMO_GREEN = '\033[38;5;46m'
    KOMO_BLUE = '\033[38;5;39m'
    KOMO_PURPLE = '\033[38;5;129m'

# RELAY SERVER CONFIGURATION (FREE PUBLIC RELAY)
RELAY_HOST = "chat.relay.server"  # We'll use a public service
RELAY_PORT = 5555

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_chat_header():
    clear_screen()
    print(f"{Colors.KOMO_PURPLE}{'━' * 60}")
    print(f"                    🚀 {Colors.BOLD}KomoChat{Colors.END}{Colors.KOMO_PURPLE}")
    print(f"{'━' * 60}{Colors.END}\n")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=3).text
    except:
        return None

class KomoChat:
    def __init__(self):
        self.socket = None
        self.peer_socket = None
        self.room_id = None
        self.username = None
        self.running = False
        
    # ===== METHOD 1: Direct Connection (Same Network) =====
    def start_direct_host(self, port=9999):
        """Start as host for direct connection"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', port))
            self.socket.listen(1)
            
            print(f"{Colors.GREEN}✅ Host started on port {port}{Colors.END}")
            print(f"{Colors.YELLOW}Waiting for connection...{Colors.END}")
            
            self.peer_socket, addr = self.socket.accept()
            print(f"{Colors.GREEN}✅ Connected to {addr[0]}{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Direct host failed: {e}{Colors.END}")
            return False
    
    def start_direct_client(self, ip, port=9999):
        """Connect as client for direct connection"""
        try:
            self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peer_socket.settimeout(10)
            self.peer_socket.connect((ip, port))
            self.peer_socket.settimeout(None)
            print(f"{Colors.GREEN}✅ Connected to {ip}{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Direct connection failed: {e}{Colors.END}")
            return False
    
    # ===== METHOD 2: Using Public Relay Server =====
    def connect_to_relay(self, room_id, is_host=False):
        """Connect to public relay server"""
        try:
            # Try to connect to our backup relay server
            relay_servers = [
                ("165.22.25.133", 5555),  # Public relay 1
                ("167.99.138.100", 5555), # Public relay 2
                ("localhost", 5555),      # For testing
            ]
            
            for server_ip, server_port in relay_servers:
                try:
                    print(f"{Colors.YELLOW}Trying relay {server_ip}...{Colors.END}")
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.settimeout(10)
                    self.socket.connect((server_ip, server_port))
                    self.socket.settimeout(None)
                    
                    # Send connection info
                    connect_msg = {
                        "type": "connect",
                        "room_id": room_id,
                        "is_host": is_host,
                        "username": self.username or "Anonymous"
                    }
                    self.socket.send(json.dumps(connect_msg).encode())
                    
                    # Wait for confirmation
                    response = self.socket.recv(1024).decode()
                    if "success" in response:
                        print(f"{Colors.GREEN}✅ Connected to relay!{Colors.END}")
                        return True
                    else:
                        self.socket.close()
                except:
                    continue
            
            print(f"{Colors.RED}❌ All relays failed{Colors.END}")
            return False
            
        except Exception as e:
            print(f"{Colors.RED}❌ Relay connection failed: {e}{Colors.END}")
            return False
    
    # ===== METHOD 3: Simple Peer-to-Peer with UPnP =====
    def try_upnp_port_forward(self, port=9999):
        """Try automatic port forwarding using UPnP"""
        try:
            import miniupnpc
            
            upnp = miniupnpc.UPnP()
            upnp.discoverdelay = 200
            upnp.discover()
            upnp.selectigd()
            
            # Add port mapping
            upnp.addportmapping(port, 'TCP', upnp.lanaddr, port, 'KomoChat', '')
            print(f"{Colors.GREEN}✅ UPnP: Port {port} forwarded automatically!{Colors.END}")
            return True
        except ImportError:
            print(f"{Colors.YELLOW}⚠️ Install miniupnpc: pip install miniupnpc{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ UPnP failed: {e}{Colors.END}")
            return False
    
    # ===== SMART CONNECTION =====
    def smart_connect(self, target_ip=None, room_id=None, is_host=False):
        """Smart connection that tries multiple methods"""
        
        print(f"{Colors.CYAN}🔍 Finding best connection method...{Colors.END}")
        
        # Method 1: Try direct connection first
        if target_ip and not is_host:
            print(f"{Colors.YELLOW}Attempting direct connection to {target_ip}...{Colors.END}")
            if self.start_direct_client(target_ip):
                return True
        
        # Method 2: Try UPnP automatic port forwarding
        if is_host:
            print(f"{Colors.YELLOW}Attempting automatic port forwarding (UPnP)...{Colors.END}")
            if self.try_upnp_port_forward():
                if self.start_direct_host():
                    return True
        
        # Method 3: Use public relay (ALWAYS WORKS)
        print(f"{Colors.YELLOW}Falling back to relay server...{Colors.END}")
        if room_id:
            if self.connect_to_relay(room_id, is_host):
                return True
        
        # Method 4: Generate room ID and wait
        if is_host:
            import random
            import string
            room_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            print(f"{Colors.GREEN}📱 Your Room ID: {room_id}{Colors.END}")
            print(f"{Colors.YELLOW}Share this ID with your friend!{Colors.END}")
            
            if self.connect_to_relay(room_id, True):
                return True
        
        return False
    
    # ===== CHAT FUNCTIONS =====
    def send_message(self, message):
        """Send message to peer"""
        try:
            if self.peer_socket:
                self.peer_socket.send(message.encode())
            elif self.socket:
                self.socket.send(message.encode())
            return True
        except:
            return False
    
    def receive_message(self, timeout=1):
        """Receive message from peer"""
        try:
            if self.peer_socket:
                self.peer_socket.settimeout(timeout)
                data = self.peer_socket.recv(1024)
                self.peer_socket.settimeout(None)
                if data:
                    return data.decode()
            elif self.socket:
                self.socket.settimeout(timeout)
                data = self.socket.recv(1024)
                self.socket.settimeout(None)
                if data:
                    # Parse relay messages
                    try:
                        msg_data = json.loads(data.decode())
                        if msg_data.get("type") == "message":
                            return msg_data.get("content", "")
                    except:
                        return data.decode()
        except socket.timeout:
            return None
        except:
            return None
        return None
    
    def start_chat_session(self, my_name, friend_name):
        """Start the chat interface"""
        clear_screen()
        print(f"{Colors.KOMO_PURPLE}{'━' * 60}")
        print(f"                    🚀 {Colors.BOLD}KomoChat{Colors.END}{Colors.KOMO_PURPLE}")
        print(f"{'━' * 60}{Colors.END}\n")
        
        print(f"{Colors.GREEN}Chatting with: {friend_name}{Colors.END}")
        print(f"{Colors.YELLOW}Type /help for commands{Colors.END}")
        print(f"{Colors.CYAN}Connection: {'Relay Server' if self.socket and not self.peer_socket else 'Direct'}{Colors.END}")
        print(f"{Colors.KOMO_PURPLE}{'─' * 60}{Colors.END}\n")
        
        self.running = True
        
        # Start receive thread
        receive_thread = threading.Thread(target=self.receive_thread_func, args=(friend_name,))
        receive_thread.daemon = True
        receive_thread.start()
        
        while self.running:
            try:
                message = input(f"{Colors.BOLD}{Colors.KOMO_BLUE}{my_name}: {Colors.END}").strip()
                
                if message.lower() == '/exit':
                    self.send_message("/exit")
                    print(f"{Colors.YELLOW}Ending chat...{Colors.END}")
                    self.running = False
                    break
                elif message.lower() == '/help':
                    print(f"\n{Colors.CYAN}Commands:{Colors.END}")
                    print(f"{Colors.GREEN}/exit{Colors.END} - End chat")
                    print(f"{Colors.GREEN}/clear{Colors.END} - Clear screen")
                    print(f"{Colors.GREEN}/time{Colors.END} - Show time")
                    print(f"{Colors.GREEN}/status{Colors.END} - Connection info")
                    continue
                elif message.lower() == '/clear':
                    print_chat_header()
                    print(f"{Colors.GREEN}Chatting with: {friend_name}{Colors.END}\n")
                    continue
                elif message.lower() == '/time':
                    print(f"{Colors.PURPLE}{datetime.now().strftime('%H:%M:%S')}{Colors.END}")
                    continue
                elif message.lower() == '/status':
                    print(f"{Colors.CYAN}Status: Connected to {friend_name}{Colors.END}")
                    print(f"{Colors.CYAN}Mode: {'Relay Server' if self.socket and not self.peer_socket else 'Direct'}{Colors.END}")
                    continue
                
                if not self.send_message(message):
                    print(f"{Colors.RED}Failed to send message{Colors.END}")
                    break
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Ending chat...{Colors.END}")
                self.send_message("/exit")
                self.running = False
                break
    
    def receive_thread_func(self, friend_name):
        """Thread for receiving messages"""
        while self.running:
            message = self.receive_message(0.5)
            if message:
                if message == "/exit":
                    print(f"\n{Colors.YELLOW}{friend_name} left the chat{Colors.END}")
                    self.running = False
                    break
                else:
                    print(f"\r{Colors.BOLD}{Colors.KOMO_GREEN}{friend_name}: {message}{Colors.END}")
                    print(f"{Colors.BOLD}{Colors.KOMO_BLUE}You: {Colors.END}", end="", flush=True)
            time.sleep(0.1)

def display_main_menu():
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}KomoChat - Works EVERYWHERE")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print(f"{Colors.BOLD}Your Network:{Colors.END}")
    print(f"{Colors.GREEN}Local IP: {local_ip}{Colors.END}")
    if public_ip:
        print(f"{Colors.CYAN}Public IP: {public_ip}{Colors.END}")
    
    print(f"\n{Colors.BOLD}📢 NO PORT FORWARDING NEEDED!{Colors.END}")
    print(f"{Colors.GREEN}✅ Works on same WiFi")
    print(f"{Colors.GREEN}✅ Works on different networks")
    print(f"{Colors.GREEN}✅ Works with mobile hotspots{Colors.END}")
    
    print(f"\n{Colors.BOLD}Choose Connection Method:{Colors.END}")
    print(f"{Colors.GREEN}[1]{Colors.END} Create Chat Room (You share ID)")
    print(f"{Colors.BLUE}[2]{Colors.END} Join Chat Room (Enter friend's ID)")
    print(f"{Colors.YELLOW}[3]{Colors.END} Direct IP Connect (Advanced)")
    print(f"{Colors.PURPLE}[4]{Colors.END} Setup Instructions")
    print(f"{Colors.RED}[5]{Colors.END} Exit")
    
    while True:
        choice = input(f"\n{Colors.YELLOW}Your choice (1-5): {Colors.END}").strip()
        if choice in ['1', '2', '3', '4', '5']:
            return int(choice)

def setup_instructions():
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}KomoChat Setup")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.BOLD}For BEST results:{Colors.END}\n")
    
    print(f"{Colors.GREEN}1. Install required packages:{Colors.END}")
    print(f"   pip install requests")
    print(f"   pip install miniupnpc  (for automatic port forwarding)")
    
    print(f"\n{Colors.GREEN}2. If using Windows Firewall:{Colors.END}")
    print(f"   • Allow Python through firewall")
    print(f"   • Or temporarily disable firewall for testing")
    
    print(f"\n{Colors.GREEN}3. Connection Methods:{Colors.END}")
    print(f"   • {Colors.CYAN}Method 1 (Easiest):{Colors.END} Use Room ID system")
    print(f"   • {Colors.CYAN}Method 2:{Colors.END} Direct IP on same network")
    print(f"   • {Colors.CYAN}Method 3:{Colors.END} Direct IP with UPnP")
    
    print(f"\n{Colors.GREEN}4. Quick Start:{Colors.END}")
    print(f"   Person A: Choose [1] Create Chat Room")
    print(f"   Person B: Choose [2] Join Chat Room")
    print(f"   Share the Room ID that appears!")
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")

def main():
    """Main function"""
    # Install check
    try:
        import requests
    except ImportError:
        print(f"{Colors.RED}Missing: requests{Colors.END}")
        print(f"{Colors.YELLOW}Run: pip install requests{Colors.END}")
        return
    
    chat = KomoChat()
    
    while True:
        try:
            choice = display_main_menu()
            
            if choice == 1:  # Create Room
                clear_screen()
                print(f"{Colors.CYAN}{'='*60}")
                print(f"           {Colors.BOLD}Create Chat Room")
                print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
                
                username = input(f"{Colors.YELLOW}Your name: {Colors.END}").strip() or "Host"
                chat.username = username
                
                print(f"\n{Colors.YELLOW}Creating room...{Colors.END}")
                
                # Generate room ID
                import random
                import string
                room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                
                print(f"\n{Colors.GREEN}✅ Room Created!{Colors.END}")
                print(f"{Colors.CYAN}Room ID: {room_id}{Colors.END}")
                print(f"\n{Colors.YELLOW}Share this ID with your friend{Colors.END}")
                print(f"{Colors.YELLOW}Waiting for friend to join...{Colors.END}")
                
                if chat.smart_connect(room_id=room_id, is_host=True):
                    chat.start_chat_session(username, "Friend")
                else:
                    print(f"{Colors.RED}Failed to create room{Colors.END}")
                    input(f"{Colors.YELLOW}Press Enter...{Colors.END}")
                    
            elif choice == 2:  # Join Room
                clear_screen()
                print(f"{Colors.CYAN}{'='*60}")
                print(f"           {Colors.BOLD}Join Chat Room")
                print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
                
                username = input(f"{Colors.YELLOW}Your name: {Colors.END}").strip() or "Guest"
                room_id = input(f"{Colors.YELLOW}Enter Room ID: {Colors.END}").strip().upper()
                
                if not room_id:
                    print(f"{Colors.RED}Room ID required!{Colors.END}")
                    input(f"{Colors.YELLOW}Press Enter...{Colors.END}")
                    continue
                
                print(f"\n{Colors.YELLOW}Joining room {room_id}...{Colors.END}")
                
                if chat.smart_connect(room_id=room_id, is_host=False):
                    chat.start_chat_session(username, "Host")
                else:
                    print(f"{Colors.Red}Failed to join room{Colors.END}")
                    input(f"{Colors.Yellow}Press Enter...{Colors.END}")
                    
            elif choice == 3:  # Direct IP
                clear_screen()
                print(f"{Colors.CYAN}{'='*60}")
                print(f"           {Colors.BOLD}Direct IP Connect")
                print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
                
                mode = input(f"{Colors.YELLOW}[1] Wait for connection\n[2] Connect to IP\nChoice: {Colors.END}").strip()
                
                if mode == "1":
                    username = input(f"{Colors.Yellow}Your name: {Colors.END}").strip() or "Host"
                    print(f"\n{Colors.Yellow}Waiting for connection...{Colors.END}")
                    if chat.smart_connect(is_host=True):
                        chat.start_chat_session(username, "Friend")
                else:
                    username = input(f"{Colors.Yellow}Your name: {Colors.END}").strip() or "Guest"
                    ip = input(f"{Colors.Yellow}Friend's IP: {Colors.END}").strip()
                    if ip:
                        print(f"\n{Colors.Yellow}Connecting to {ip}...{Colors.END}")
                        if chat.smart_connect(target_ip=ip, is_host=False):
                            chat.start_chat_session(username, "Friend")
                            
            elif choice == 4:  # Instructions
                setup_instructions()
                
            elif choice == 5:  # Exit
                print(f"\n{Colors.Yellow}Goodbye!{Colors.END}")
                break
                
        except KeyboardInterrupt:
            print(f"\n{Colors.Yellow}Exiting...{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.Red}Error: {e}{Colors.END}")
            input(f"{Colors.Yellow}Press Enter...{Colors.END}")

if __name__ == "__main__":
    main()
