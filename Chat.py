#!/usr/bin/env python3
"""
KomoChat Client - Terminal Chat Application
Connect to server and chat with everyone
"""
import socket
import threading
import sys
import os
import time

# Colors for terminal
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print chat header"""
    print(f"{Colors.PURPLE}{'━'*60}")
    print(f"                   {Colors.BOLD}KOMOCHAT TERMINAL{Colors.END}{Colors.PURPLE}")
    print(f"{'━'*60}{Colors.END}\n")

class ChatClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""
        self.running = True
        
    def connect(self, host, port=9999):
        """Connect to chat server"""
        try:
            print(f"{Colors.YELLOW}Connecting to {host}:{port}...{Colors.END}")
            self.client.connect((host, port))
            
            # Get nickname
            self.nickname = input(f"{Colors.YELLOW}Enter your nickname: {Colors.END}").strip()
            if not self.nickname:
                self.nickname = "Anonymous"
            
            # Send nickname to server
            self.client.send(self.nickname.encode('utf-8'))
            
            # Receive welcome message
            welcome = self.client.recv(1024).decode('utf-8')
            print(f"{Colors.GREEN}{welcome}{Colors.END}")
            
            return True
            
        except ConnectionRefusedError:
            print(f"{Colors.RED}❌ Cannot connect to server!{Colors.END}")
            print(f"{Colors.YELLOW}Make sure server is running on {host}:{port}{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}Connection error: {e}{Colors.END}")
            return False
    
    def receive_messages(self):
        """Receive messages from server"""
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message:
                    # Don't print if it's our own message
                    if not message.startswith(f"[{self.nickname}]:"):
                        print(f"\r{Colors.CYAN}{message}{Colors.END}")
                        print(f"{Colors.BLUE}You: {Colors.END}", end="", flush=True)
            except:
                print(f"\n{Colors.RED}❌ Lost connection to server{Colors.END}")
                self.running = False
                break
    
    def send_message(self, message):
        """Send message to server"""
        try:
            self.client.send(message.encode('utf-8'))
            return True
        except:
            return False
    
    def start_chat(self):
        """Start the chat interface"""
        clear_screen()
        print_header()
        
        print(f"{Colors.GREEN}Connected as: {self.nickname}{Colors.END}")
        print(f"{Colors.YELLOW}Type your messages below")
        print(f"Type '/exit' to quit")
        print(f"{Colors.PURPLE}{'─'*60}{Colors.END}\n")
        
        # Start receiving thread
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        while self.running:
            try:
                # Print prompt
                message = input(f"{Colors.BLUE}You: {Colors.END}").strip()
                
                if message.lower() == '/exit':
                    print(f"{Colors.YELLOW}Disconnecting...{Colors.END}")
                    self.running = False
                    break
                elif message.lower() == '/clear':
                    clear_screen()
                    print_header()
                    print(f"{Colors.GREEN}Connected as: {self.nickname}{Colors.END}\n")
                    continue
                elif message.lower() == '/help':
                    print(f"\n{Colors.CYAN}Commands:{Colors.END}")
                    print(f"{Colors.GREEN}/exit{Colors.END} - Quit chat")
                    print(f"{Colors.GREEN}/clear{Colors.END} - Clear screen")
                    print(f"{Colors.GREEN}/users{Colors.END} - Show online users")
                    print(f"{Colors.GREEN}/nick{Colors.END} - Change nickname")
                    continue
                elif message.lower() == '/users':
                    self.send_message("/users")
                    continue
                elif message.lower() == '/nick':
                    new_nick = input(f"{Colors.YELLOW}New nickname: {Colors.END}").strip()
                    if new_nick:
                        self.send_message(f"/nick {new_nick}")
                        self.nickname = new_nick
                        print(f"{Colors.GREEN}Nickname changed to {new_nick}{Colors.END}")
                    continue
                
                if message:  # Don't send empty messages
                    if not self.send_message(message):
                        print(f"{Colors.RED}Failed to send message{Colors.END}")
                        break
                        
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Disconnecting...{Colors.END}")
                self.running = False
                break
            except EOFError:
                print(f"\n{Colors.YELLOW}Disconnecting...{Colors.END}")
                self.running = False
                break
        
        # Cleanup
        try:
            self.client.close()
        except:
            pass

def main():
    clear_screen()
    print(f"{Colors.CYAN}{'═'*50}")
    print(f"     {Colors.BOLD}KOMOCHAT - TERMINAL CHAT CLIENT{Colors.END}{Colors.CYAN}")
    print(f"{'═'*50}{Colors.END}\n")
    
    # Get server info
    print(f"{Colors.YELLOW}Enter Server Information{Colors.END}")
    print(f"{Colors.CYAN}Someone must run 'server.py' first{Colors.END}\n")
    
    host = input(f"{Colors.YELLOW}Server IP address: {Colors.END}").strip()
    if not host:
        print(f"{Colors.RED}IP address required!{Colors.END}")
        return
    
    port = input(f"{Colors.YELLOW}Port [9999]: {Colors.END}").strip()
    if not port:
        port = 9999
    else:
        try:
            port = int(port)
        except:
            port = 9999
    
    # Create client and connect
    client = ChatClient()
    if client.connect(host, port):
        client.start_chat()
    
    print(f"\n{Colors.YELLOW}Press Enter to exit...{Colors.END}")
    input()

if __name__ == "__main__":
    main()
