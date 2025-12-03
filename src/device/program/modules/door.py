from modules.module import Module
from time import sleep
import socketio
import requests
import psutil
import time
import json
import sys
import signal
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('device.log')
    ]
)

logger = logging.getLogger(__name__)

class Door(Module):
    def __init__(self, id, programId, server_url="http://144.31.73.100:4546", device_name=None):
        super().__init__(id, programId)
        self.server_url = server_url
        self.device_name = device_name or f"PythonDevice-{self.get_hostname()}"
        self.device_id = None
        self.is_connected = False
        
        self.sio = socketio.Client(
            reconnection=True,
            reconnection_attempts=10,
            reconnection_delay=1000,
            reconnection_delay_max=5000
        )
        
        self.setup_event_handlers()
    
    def get_hostname(self):
        """Получаем имя хоста устройства"""
        try:
            return socket.gethostname()
        except:
            return "unknown"
    
    def get_device_info(self):
        """Собираем информацию об устройстве"""
        try:
            hostname = self.get_hostname()
            ip_address = self.get_ip_address()
            
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            device_info = {
                "hostname": hostname,
                "ip_address": ip_address,
                "platform": sys.platform,
                "python_version": sys.version,
                "cpu_count": cpu_count,
                "memory_total": f"{memory.total / (1024**3):.2f} GB",
                "memory_available": f"{memory.available / (1024**3):.2f} GB",
                "disk_total": f"{disk.total / (1024**3):.2f} GB",
                "disk_free": f"{disk.free / (1024**3):.2f} GB",
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
            }
            return device_info
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            return {"error": str(e)}
    
    def get_ip_address(self):
        """Получаем IP адрес устройства"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            try:
                hostname = socket.gethostname()
                return socket.gethostbyname(hostname)
            except:
                return "127.0.0.1"
    
    def setup_event_handlers(self):
        """Настраиваем обработчики событий Socket.IO"""
        
        @self.sio.event
        def connect():
            self.is_connected = True
            logger.info(f"Connected to server {self.server_url}")
            logger.info(f"Socket ID: {self.sio.sid}")
            
            self.register_device()
        
        @self.sio.event
        def disconnect():
            self.is_connected = False
            self.device_id = None
            logger.info("Disconnected from server")
        
        @self.sio.event
        def connect_error(data):
            logger.error(f"Connection failed: {data}")
        
        @self.sio.on('device-registered')
        def on_device_registered(data):
            self.device_id = data.get('deviceId')
            logger.info(f"Device registered with ID: {self.device_id}")
            logger.info(f"Device IP: {self.get_ip_address()}")
        
        @self.sio.on('start-device')
        def on_start_device(data):
            logger.info("START command received:")
            logger.info(f"   From: {data.get('from', 'Unknown')}")
            logger.info(f"   Client: {data.get('clientSocketId', 'Unknown')}")
            logger.info(f"   Time: {data.get('timestamp', 'Unknown')}")
            
            self.send_ip_address()
            self.simulate_device_activity()
        
        @self.sio.on('device-ip-received')
        def on_device_ip_received(data):
            logger.info(f"IP confirmed by server: {data.get('message')}")
        
        @self.sio.on('welcome')
        def on_welcome(data):
            logger.info(f"Server welcome: {data.get('message')}")
        
        @self.sio.on('devices-update')
        def on_devices_update(data):
            device_count = len([d for d in data if d.get('type') == 'device'])
            logger.info(f"Devices update: {device_count} devices connected")
        
        @self.sio.on('error')
        def on_error(data):
            logger.error(f"Server error: {data}")
        
        # NEW: Terminal command handler
        @self.sio.on('terminal-command')
        def on_terminal_command(data):
            command = data.get('command', '')
            from_user = data.get('from', 'Unknown')
            client_socket_id = data.get('clientSocketId', '')
            timestamp = data.get('timestamp', '')
            
            logger.info(f"Terminal command received: {command}")
            logger.info(f"   From: {from_user}")
            logger.info(f"   Client socket: {client_socket_id}")
            
            # Process the command
            try:
                result = self.execute_terminal_command(command)
                
                # Send response back
                response_data = {
                    "clientSocketId": client_socket_id,
                    "response": result,
                    "timestamp": datetime.now().isoformat()
                }
                
                if self.is_connected:
                    self.sio.emit('terminal-response', response_data)
                    logger.info(f"Command response sent: {result[:50]}...")
                    
            except Exception as e:
                logger.error(f"Error executing command: {e}")
                
                error_response = {
                    "clientSocketId": client_socket_id,
                    "response": f"ERROR: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                
                if self.is_connected:
                    self.sio.emit('terminal-response', error_response)
    
    def execute_terminal_command(self, command):
        """Execute a terminal command and return result"""
        import subprocess
        import platform
        
        logger.info(f"Executing command: {command}")
        
        # Handle special commands
        if command.strip() == "help":
            return """Available commands:
• help - Show this help
• status - Show device status
• info - Show device information
• date - Show current date and time
• echo <text> - Echo back text
• python - Check Python version
• sysinfo - Show system information
• ls [dir] - List directory contents
• pwd - Show current directory
• Any system command (will be executed on device)"""
        
        elif command.strip() == "status":
            status = self.get_status()
            return json.dumps(status, indent=2)
        
        elif command.strip() == "info":
            info = self.get_device_info()
            return json.dumps(info, indent=2)
        
        elif command.strip() == "date":
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        elif command.startswith("echo "):
            return command[5:]
        
        elif command.strip() == "python":
            import sys
            return f"Python {sys.version}"
        
        elif command.strip() == "sysinfo":
            import platform, psutil
            info = {
                "system": platform.system(),
                "release": platform.release(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB"
            }
            return json.dumps(info, indent=2)
        
        elif command.startswith("ls"):
            import os
            parts = command.split()
            directory = parts[1] if len(parts) > 1 else "."
            try:
                files = os.listdir(directory)
                return "\n".join(files)
            except Exception as e:
                return f"Error: {str(e)}"
        
        elif command.strip() == "pwd":
            import os
            return os.getcwd()
        
        else:
            # Execute as system command
            try:
                # Determine shell based on platform
                shell = platform.system() == "Windows"
                
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                
                output = ""
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}"
                if result.stderr:
                    output += f"\nSTDERR:\n{result.stderr}"
                if result.returncode != 0:
                    output += f"\nExit code: {result.returncode}"
                
                return output if output else "Command executed (no output)"
                
            except subprocess.TimeoutExpired:
                return "ERROR: Command timed out after 10 seconds"
            except Exception as e:
                return f"ERROR: {str(e)}"
    
    def register_device(self):
        """Регистрируем устройство на сервере"""
        if not self.is_connected:
            logger.error("Cannot register: not connected to server")
            return
        
        device_data = {
            "name": self.device_name,
            "type": "python-device",
            "version": "1.0.0",
            "capabilities": ["start-command", "ip-sharing", "python-runtime", "terminal-commands"],
            "hostname": self.get_hostname(),
            "platform": sys.platform,
            "python_version": sys.version.split()[0]
        }
        
        logger.info(f"Registering device: {device_data['name']}")
        self.sio.emit('device-register', device_data)
    
    def send_ip_address(self):
        """Отправляем IP адрес на сервер"""
        if not self.is_connected:
            logger.error("Cannot send IP: not connected to server")
            return
        
        ip_data = {
            "ip": self.get_ip_address(),
            "timestamp": datetime.now().isoformat(),
            "deviceId": self.device_id
        }
        
        logger.info(f"Sending IP address: {ip_data['ip']}")
        self.sio.emit('device-ip', ip_data)
    
    def simulate_device_activity(self):
        """Симулируем работу устройства после команды START"""
        logger.info("Simulating device activity...")
        
        for i in range(3):
            time.sleep(1)
            logger.info(f"   Processing... {i+1}/3")
        
        logger.info("Device activity completed")
        
        if self.is_connected and self.device_id:
            completion_data = {
                "deviceId": self.device_id,
                "activity": "start-command",
                "result": "success",
                "timestamp": datetime.now().isoformat(),
                "details": "Python device processing completed successfully"
            }
            self.sio.emit('device-activity-complete', completion_data)
    
    def connect(self):
        """Подключаемся к серверу"""
        try:
            logger.info(f"Connecting to server: {self.server_url}")
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Отключаемся от сервера"""
        if self.is_connected:
            self.sio.disconnect()
            logger.info("🔌 Disconnected from server")
    
    def get_status(self):
        """Получаем статус устройства"""
        return {
            "connected": self.is_connected,
            "device_id": self.device_id,
            "server_url": self.server_url,
            "device_name": self.device_name,
            "socket_id": self.sio.sid if self.is_connected else None,
            "device_info": self.get_device_info()
        }
    
    def wait_for_events(self):
        """Ожидаем события (блокирующий вызов)"""
        try:
            self.sio.wait()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.disconnect()

    def execute_script(self):
        """Основной метод выполнения скрипта (реализация абстрактного метода)"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("Python Device Controller - Door Module")
        print("=" * 40)
        
        try:
            if self.connect():
                print("Device started successfully!")
                print("Press Ctrl+C to stop the device")
                print("=" * 40)
                
                self.wait_for_events()
            else:
                print("Failed to connect to server")
                
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    def signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        logger.info("Shutdown signal received")
        self.disconnect()
        sys.exit(0)