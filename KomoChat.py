#!/usr/bin/env python3
"""
KomoChat - Cross-Network Terminal Chat Application by Komo Moko
"""

import socket
import threading
import sys
import os
import json
import time
import requests
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
    """Get public IP address"""
    try:
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        try:
            return requests.get('https://api64.ipify.org', timeout=5).text
        except:
            return None

def is_valid_ip(ip):
    """Check if IP address is valid"""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def test_port(ip, port, timeout=3):
    """Test if a port is open on a remote host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def scan_common_ports(ip):
    """Scan common chat ports"""
    common_ports = [9999, 8888, 7777, 12345, 5555, 2222, 9998, 9997]
    open_ports = []
    
    print(f"\n{Colors.YELLOW}Scanning common ports on {ip}...{Colors.END}")
    for port in common_ports:
        print(f"  Port {port}...", end="\r")
        if test_port(ip, port, 1):
            open_ports.append(port)
            print(f"  Port {port}: {Colors.GREEN}OPEN{Colors.END}")
        else:
            print(f"  Port {port}: {Colors.RED}CLOSED{Colors.END}")
    return open_ports

def display_network_info():
    """Display network information"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}Network Information")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print(f"{Colors.BOLD}Local IP: {Colors.KOMO_GREEN}{local_ip}{Colors.END}")
    if public_ip:
        print(f"{Colors.BOLD}Public IP: {Colors.CYAN}{public_ip}{Colors.END}")
    else:
        print(f"{Colors.BOLD}Public IP: {Colors.RED}Could not determine{Colors.END}")
    
    # Show network type
    print(f"\n{Colors.BOLD}Network Status:{Colors.END}")
    if local_ip.startswith("192.168.") or local_ip.startswith("10.") or local_ip.startswith("172.16."):
        print(f"  {Colors.YELLOW}⚠️  You are behind a NAT/Router{Colors.END}")
        print(f"  {Colors.YELLOW}  For incoming connections: Forward port 9999 on your router{Colors.END}")
    elif local_ip == "127.0.0.1":
        print(f"  {Colors.RED}❌ No network connection detected{Colors.END}")
    else:
        print(f"  {Colors.GREEN}✅ Direct internet connection{Colors.END}")
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")

def display_connection_menu():
    """Display only connection menu - no banners"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}KomoChat Connection Setup")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print(f"{Colors.BOLD}Your Local IP: {Colors.KOMO_GREEN}{local_ip}{Colors.END}")
    if public_ip:
        print(f"{Colors.BOLD}Your Public IP: {Colors.CYAN}{public_ip}{Colors.END}")
    
    print(f"\n{Colors.BOLD}Select Mode:{Colors.END}")
    print(f"{Colors.GREEN}[1]{Colors.END} Connect to a friend (Client)")
    print(f"{Colors.BLUE}[2]{Colors.END} Wait for connection (Server)")
    print(f"{Colors.PURPLE}[3]{Colors.END} Network Diagnostics")
    print(f"{Colors.YELLOW}[4]{Colors.END} Scan for open ports")
    print(f"{Colors.RED}[5]{Colors.END} Exit KomoChat")
    
    while True:
        try:
            choice = input(f"\n{Colors.YELLOW}Enter choice (1-5): {Colors.END}").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            else:
                print(f"{Colors.RED}Please enter 1-5{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}Exiting...{Colors.END}")
            sys.exit(0)

def start_sender():
    """Start as sender/client with cross-network support"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*60}")
    print(f"           {Colors.BOLD}Connect to Friend")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    # Get receiver's IP
    while True:
        receiver_ip = input(f"{Colors.YELLOW}Enter friend's IP address (or domain): {Colors.END}").strip()
        if receiver_ip:
            if is_valid_ip(receiver_ip) or '.' in receiver_ip:
                break
            else:
                print(f"{Colors.RED}Please enter a valid IP address or domain{Colors.END}")
    
    # Try to resolve domain if not IP
    try:
        if not is_valid_ip(receiver_ip):
            print(f"{Colors.YELLOW}Resolving {receiver_ip}...{Colors.END}")
            receiver_ip = socket.gethostbyname(receiver_ip)
            print(f"{Colors.GREEN}Resolved to: {receiver_ip}{Colors.END}")
    except:
        print(f"{Colors.RED}Cannot resolve {receiver_ip}{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
        return
    
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
    
    # Test connection first
    print(f"\n{Colors.YELLOW}Testing connection to {receiver_ip}:{port}...{Colors.END}")
    
    if test_port(receiver_ip, port):
        print(f"{Colors.GREEN}✅ Port {port} is open!{Colors.END}")
    else:
        print(f"{Colors.RED}❌ Port {port} is closed or unreachable{Colors.END}")
        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.END}")
        print("1. Make sure friend is running KomoChat in Receiver mode")
        print("2. Friend needs to forward port {port} on their router")
        print("3. Friend's firewall must allow incoming connections")
        
        retry = input(f"\n{Colors.YELLOW}Try anyway? (y/n): {Colors.END}").strip().lower()
        if retry != 'y':
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
            return
    
    # Try to connect
    print(f"\n{Colors.GREEN}Connecting to {receiver_ip}:{port}...{Colors.END}")
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect((receiver_ip, port))
        client_socket.settimeout(None)  # Reset timeout
        
        print(f"{Colors.GREEN}✅ Connected successfully!{Colors.END}")
        time.sleep(1)
        
        # Show only chat interface
        chat_session(client_socket, "You", "Friend", receiver_ip)
        
    except socket.timeout:
        print(f"\n{Colors.RED}❌ Connection timeout")
        print("Make sure the remote server is running and port is forwarded{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
    except ConnectionRefusedError:
        print(f"\n{Colors.RED}❌ Connection refused")
        print("The server is not running on that port{Colors.END}")
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
    """Start as receiver/server with cross-network support"""
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
    
    # Show network information
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print(f"\n{Colors.BOLD}Connection Information:{Colors.END}")
    print(f"{Colors.GREEN}Local IP: {local_ip}{Colors.END}")
    if public_ip:
        print(f"{Colors.CYAN}Public IP: {public_ip}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}⚠️  For cross-network chat:{Colors.END}")
    print(f"{Colors.YELLOW}1. Forward port {port} on your router{Colors.END}")
    print(f"{Colors.YELLOW}2. Allow port {port} in firewall{Colors.END}")
    print(f"{Colors.YELLOW}3. Share your {Colors.CYAN}Public IP{Colors.YELLOW} with friend{Colors.END}")
    
    print(f"\n{Colors.GREEN}Waiting for connection on port {port}...{Colors.END}")
    
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(1)
        server_socket.settimeout(3600)  # 1 hour timeout
        
        print(f"{Colors.GREEN}✅ Server is listening...{Colors.END}")
        print(f"{Colors.YELLOW}(Press Ctrl+C to cancel){Colors.END}")
        
        client_socket, client_address = server_socket.accept()
        print(f"\n{Colors.GREEN}✅ Connected to {client_address[0]}{Colors.END}")
        time.sleep(1)
        
        # Show only chat interface
        chat_session(client_socket, "You", f"Friend ({client_address[0]})", "")
        
    except socket.timeout:
        print(f"\n{Colors.YELLOW}⏰ No connection received in 1 hour{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Server stopped by user{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
    finally:
        try:
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
                start_sender()
            elif choice == 2:
                start_receiver()
            elif choice == 3:
                display_network_info()
            elif choice == 4:
                # Simple port scanner
                clear_screen()
                ip = input(f"{Colors.YELLOW}Enter IP to scan: {Colors.END}").strip()
                if ip:
                    scan_common_ports(ip)
                    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
            elif choice == 5:
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
