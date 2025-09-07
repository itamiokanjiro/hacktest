import paramiko
import socket
import os
import threading
from paramiko import Transport, SFTPServer, SFTPServerInterface, ServerInterface

# 设置工作目录（这里设置为C盘根目录）
os.chdir('C:/')
print(f"工作目录设置为: {os.getcwd()}")

# 设置账号密码
USERNAME = "user"
PASSWORD = "pass"

class SimpleSFTPServer(SFTPServerInterface):
    """简单的SFTP服务器实现"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SimpleServer(ServerInterface):
    """认证服务器"""
    def check_auth_password(self, username, password):
        """验证用户名和密码"""
        print(f"认证尝试: 用户名={username}, 密码={password}")
        if username == USERNAME and password == PASSWORD:
            print("认证成功!")
            return paramiko.AUTH_SUCCESSFUL
        else:
            print("认证失败!")
            return paramiko.AUTH_FAILED
    
    def get_allowed_auths(self, username):
        """允许的认证方式"""
        return "password"

def handle_client(client, addr):
    """处理客户端连接"""
    try:
        print(f"新的连接来自: {addr}")
        transport = Transport(client)
        # 生成RSA密钥
        host_key = paramiko.RSAKey.generate(2048)
        transport.add_server_key(host_key)
        
        # 设置SFTP处理器
        transport.set_subsystem_handler('sftp', SFTPServer, SimpleSFTPServer)
        
        # 启动服务器
        server = SimpleServer()
        transport.start_server(server=server)
        
        print(f"SFTP会话已建立: {addr}")
        
        # 保持连接
        while transport.is_active():
            import time
            time.sleep(1)
            
    except Exception as e:
        print(f"处理客户端时出错: {e}")
    finally:
        try:
            client.close()
        except:
            pass

def start_sftp_server():
    """启动SFTP服务器"""
    sock = None
    try:
        # 创建socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # 绑定到所有接口的22端口
        sock.bind(('0.0.0.0', 22))
        sock.listen(5)
        
        print("=" * 50)
        print("SFTP服务器已启动!")
        print(f"监听端口: 22")
        print(f"用户名: {USERNAME}")
        print(f"密码: {PASSWORD}")
        print(f"根目录: C:/")
        print("=" * 50)
        print("等待客户端连接...")
        print("按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        while True:
            client, addr = sock.accept()
            # 在新线程中处理每个客户端
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client, addr),
                daemon=True
            )
            client_thread.start()
            
    except PermissionError:
        print("\n错误: 需要管理员权限来绑定22端口!")
        print("请以管理员身份运行此脚本")
    except OSError as e:
        if e.errno == 10048:
            print("\n错误: 端口22已被其他程序占用!")
            print("请关闭占用22端口的程序或使用其他端口")
        else:
            print(f"\n网络错误: {e}")
    except Exception as e:
        print(f"\n服务器错误: {e}")
    finally:
        if sock:
            sock.close()
        print("服务器已停止")

if __name__ == '__main__':
    # 检查paramiko是否安装
    try:
        import paramiko
    except ImportError:
        print("错误: 请先安装paramiko: pip install paramiko")
        exit(1)
    
    start_sftp_server()