#!/usr/bin/env python3
"""
KomoChat - Terminal Chat Application by Komo Moko
"""

import socket
import threading
import sys
import os
import json
import time
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

def display_connection_menu():
    """Display only connection menu - no banners"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}KomoChat Connection Setup")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Your IP Address: {Colors.KOMO_GREEN}{get_local_ip()}{Colors.END}")
    print(f"\n{Colors.BOLD}Select Mode:{Colors.END}")
    print(f"{Colors.GREEN}[1]{Colors.END} Connect to a friend (Sender)")
    print(f"{Colors.BLUE}[2]{Colors.END} Wait for connection (Receiver)")
    print(f"{Colors.RED}[3]{Colors.END} Exit KomoChat")
    
    while True:
        try:
            choice = input(f"\n{Colors.YELLOW}Enter choice (1-3): {Colors.END}").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            else:
                print(f"{Colors.RED}Please enter 1, 2, or 3{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}Exiting...{Colors.END}")
            sys.exit(0)

def start_sender():
    """Start as sender/client - minimal setup"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}Connect to Friend")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    # Get receiver's IP
    while True:
        receiver_ip = input(f"{Colors.YELLOW}Enter friend's IP address: {Colors.END}").strip()
        if receiver_ip:
            break
        print(f"{Colors.RED}IP address cannot be empty!{Colors.END}")
    
    # Get port number
    while True:
        port_input = input(f"{Colors.YELLOW}Enter port [9999]: {Colors.END}").strip()
        if not port_input:
            port = 9999
            break
        try:
            port = int(port_input)
            if 1 <= port <= 65535:
                break
            else:
                print(f"{Colors.RED}Port must be between 1 and 65535{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Please enter a valid number{Colors.END}")
    
    # Try to connect
    print(f"\n{Colors.GREEN}Connecting to {receiver_ip}:{port}...{Colors.END}")
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((receiver_ip, port))
        print(f"{Colors.GREEN}Connected successfully!{Colors.END}")
        time.sleep(1)
        
        # Show only chat interface
        chat_session(client_socket, "You", "Friend", receiver_ip)
        
    except ConnectionRefusedError:
        print(f"\n{Colors.RED}❌ Connection refused.")
        print(f"Make sure your friend is running KomoChat in Receiver mode{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
    finally:
        try:
            client_socket.close()
        except:
            pass

def start_receiver():
    """Start as receiver/server - minimal setup"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}Wait for Connection")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    # Get port number
    while True:
        port_input = input(f"{Colors.YELLOW}Enter port to listen on [9999]: {Colors.END}").strip()
        if not port_input:
            port = 9999
            break
        try:
            port = int(port_input)
            if 1 <= port <= 65535:
                break
            else:
                print(f"{Colors.RED}Port must be between 1 and 65535{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Please enter a valid number{Colors.END}")
    
    print(f"\n{Colors.GREEN}Waiting for connection on port {port}...{Colors.END}")
    print(f"{Colors.YELLOW}Share this with your friend:{Colors.END}")
    print(f"{Colors.CYAN}IP: {get_local_ip()}")
    print(f"Port: {port}{Colors.END}")
    print(f"\n{Colors.GREEN}⏳ Waiting for friend to connect...{Colors.END}")
    
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(1)
        
        client_socket, client_address = server_socket.accept()
        print(f"\n{Colors.GREEN}✅ Connected to {client_address[0]}{Colors.END}")
        time.sleep(1)
        
        # Show only chat interface
        chat_session(client_socket, "You", f"Friend ({client_address[0]})", "")
        
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
    finally:
        try:
            client_socket.close()
            server_socket.close()
        except:
            pass

def chat_session(sock, my_name, friend_name, friend_ip):
    """Handle the chat session - Clean interface only"""
    # Clear screen and show chat header
    print_chat_header()
    
    # Show connection info only once
    if friend_ip:
        print(f"{Colors.CYAN}Connected to: {friend_ip}{Colors.END}")
    print(f"{Colors.GREEN}Chatting with: {friend_name}{Colors.END}")
    print(f"{Colors.YELLOW}Type {Colors.BOLD}/help{Colors.END}{Colors.YELLOW} for commands{Colors.END}")
    print(f"{Colors.KOMO_PURPLE}{'─' * 60}{Colors.END}\n")
    
    # Start receiving thread
    receive_thread = threading.Thread(target=receive_messages, args=(sock, friend_name))
    receive_thread.daemon = True
    receive_thread.start()
    
    while True:
        try:
            # Get user input with clean prompt
            message = input(f"{Colors.BOLD}{Colors.KOMO_BLUE}{my_name}: {Colors.END}").strip()
            
            # Check for commands
            if message.lower() == '/exit':
                print(f"{Colors.YELLOW}Ending chat...{Colors.END}")
                sock.send(b"/exit")
                break
            elif message.lower() == '/clear':
                print_chat_header()
                print(f"{Colors.CYAN}Connected to: {friend_ip}{Colors.END}" if friend_ip else "")
                print(f"{Colors.GREEN}Chatting with: {friend_name}{Colors.END}")
                print(f"{Colors.YELLOW}Type {Colors.BOLD}/help{Colors.END}{Colors.YELLOW} for commands{Colors.END}")
                print(f"{Colors.KOMO_PURPLE}{'─' * 60}{Colors.END}\n")
                continue
            elif message.lower() == '/help':
                print(f"\n{Colors.CYAN}{'─' * 40}")
                print(f"{Colors.BOLD}KomoChat Commands:{Colors.END}")
                print(f"{Colors.GREEN}/exit{Colors.END}  - End chat session")
                print(f"{Colors.GREEN}/clear{Colors.END} - Clear screen")
                print(f"{Colors.GREEN}/help{Colors.END}  - Show this help")
                print(f"{Colors.GREEN}/time{Colors.END}  - Show current time")
                print(f"{Colors.GREEN}/emoji{Colors.END} - Show emojis")
                print(f"{Colors.GREEN}/status{Colors.END} - Connection status")
                print(f"{Colors.CYAN}{'─' * 40}{Colors.END}\n")
                continue
            elif message.lower() == '/time':
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{Colors.PURPLE}Current time: {current_time}{Colors.END}")
                continue
            elif message.lower() == '/emoji':
                print(f"{Colors.YELLOW}😀 😃 😄 😁 😆 😅 😂 🤣 😊 😇 🙂 🙃 😉 😌 😍 🥰 😘 😗 😙 😚 😋 😛 😝 😜 🤪 🤨 🧐 🤓 😎{Colors.END}")
                continue
            elif message.lower() == '/status':
                print(f"{Colors.CYAN}Status: Connected to {friend_name}{Colors.END}")
                continue
            
            # Send message
            try:
                sock.send(message.encode())
            except:
                print(f"{Colors.RED}Failed to send message. Connection lost.{Colors.END}")
                break
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Ending chat...{Colors.END}")
            try:
                sock.send(b"/exit")
            except:
                pass
            break
        except EOFError:
            print(f"\n{Colors.YELLOW}Ending chat...{Colors.END}")
            break

def receive_messages(sock, friend_name):
    """Receive messages in separate thread"""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print(f"\n{Colors.RED}Connection closed by {friend_name}{Colors.END}")
                break
            
            message = data.decode()
            
            if message == "/exit":
                print(f"\n{Colors.YELLOW}{friend_name} has ended the chat.{Colors.END}")
                break
            else:
                print(f"\r{Colors.BOLD}{Colors.KOMO_GREEN}{friend_name}: {message}{Colors.END}")
                print(f"{Colors.BOLD}{Colors.KOMO_BLUE}You: {Colors.END}", end="", flush=True)
                
        except ConnectionResetError:
            print(f"\n{Colors.RED}Connection lost with {friend_name}{Colors.END}")
            break
        except:
            break

def main():
    """Main function - Simple loop"""
    while True:
        try:
            choice = display_connection_menu()
            
            if choice == 1:
                start_sender()
            elif choice == 2:
                start_receiver()
            elif choice == 3:
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
