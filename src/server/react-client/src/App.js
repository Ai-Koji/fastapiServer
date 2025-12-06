import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import Terminal from './components/Terminal';
import './css/App.css';

const API_BASE_URL = 'http://144.31.73.100:4545';
const WS_SERVER_URL = 'http://144.31.73.100:4546';

function App() {
  const [sessionId, setSessionId] = useState('');
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [devices, setDevices] = useState([]);
  const [connectedDevices, setConnectedDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [notifications, setNotifications] = useState([]);
  const [terminalLogs, setTerminalLogs] = useState([]);
  const [terminalPaused, setTerminalPaused] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  
  const socketRef = useRef(null);

  // Уведомления
  const addNotification = (title, message, type = 'info') => {
    const newNotification = {
      id: Date.now(),
      title,
      message,
      type,
      time: new Date().toLocaleTimeString()
    };
    setNotifications(prev => [newNotification, ...prev].slice(0, 10));
  };

  // Терминал сервера
  const addTerminalLog = (message, type = 'info') => {
    if (terminalPaused) return;
    const newLog = {
      id: Date.now(),
      message,
      type,
      time: new Date().toLocaleTimeString()
    };
    setTerminalLogs(prev => [...prev, newLog]);
  };

  // Подключение к WebSocket
  const connectWebSocket = () => {
    if (socketRef.current) {
      socketRef.current.disconnect();
    }

    socketRef.current = io(WS_SERVER_URL, {
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    socketRef.current.on('connect', () => {
      addTerminalLog('WebSocket connection established', 'connection');
      setConnectionStatus('connected');
      
      if (currentUser) {
        socketRef.current.emit('client-login', currentUser);
      }
    });

    socketRef.current.on('login-success', (data) => {
      addTerminalLog('Authentication successful', 'success');
      addNotification('Login Successful', 'Connected to server successfully', 'success');
    });

    socketRef.current.on('disconnect', () => {
      addTerminalLog('Disconnected from server', 'error');
      setConnectionStatus('disconnected');
      addNotification('Disconnected', 'Lost connection to server', 'error');
    });

    socketRef.current.on('connect_error', (error) => {
      addTerminalLog('Connection error: ' + error.message, 'error');
      setConnectionStatus('disconnected');
    });

    socketRef.current.on('devices-update', (devices) => {
      const filteredDevices = devices.filter(d => d.type === 'device');
      setConnectedDevices(filteredDevices);
      addTerminalLog(`Devices update: ${filteredDevices.length} devices`, 'info');
    });

    socketRef.current.on('device-connected', (data) => {
      addTerminalLog(`Device connected: ${data.deviceId}`, 'connection');
      addNotification('Device Connected', `New device: ${data.deviceId}`, 'info');
    });

    socketRef.current.on('device-disconnected', (data) => {
      addTerminalLog(`Device disconnected: ${data.deviceId}`, 'warning');
      addNotification('Device Disconnected', `Device ${data.deviceId} disconnected`, 'warning');
    });

    socketRef.current.on('device-ip-received', (data) => {
      addTerminalLog(`Device ${data.deviceId} reported IP: ${data.ip}`, 'success');
      addNotification('Device IP Received', `Device ${data.deviceId} is ready at ${data.ip}`, 'success');
    });

    socketRef.current.on('command-sent', (data) => {
      addTerminalLog(`Command sent: ${data.message}`, 'success');
      addNotification('Command Sent', data.message, 'success');
    });

    socketRef.current.on('error', (error) => {
      addTerminalLog(`Server error: ${error}`, 'error');
      addNotification('Error', error, 'error');
    });
  };

  // Авторизация
  const handleLogin = async (e) => {
    e.preventDefault(); 
    try {
      const response = await axios.post(`${API_BASE_URL}/client/auth/login`, {
        login,
        password
      });
      
      setSessionId(response.data.session_id);
      
      const user = {
        username: login,
        id: login,
        role: login === 'admin' ? 'admin' : 'user'
      };
      
      setCurrentUser(user);
      
      if (user.role === 'admin') {
        setIsLoggedIn(true);
        setConnectionStatus('connecting');
        addTerminalLog('Authentication successful', 'success');
        
        // Подключаемся к WebSocket
        connectWebSocket();
        
        // Загружаем устройства из FastAPI
        fetchDevices();
      } else {
        addTerminalLog('Access denied: Admin privileges required', 'error');
        alert('Access denied. Only admin can access this panel.');
      }
      
    } catch (error) {
      addTerminalLog('Login failed: ' + (error.response?.data?.detail || error.message), 'error');
      alert('Login failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Получение устройств из FastAPI
  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/device/process/listDevices`, {
        headers: { Authorization: sessionId }
      });
      
      const devicesList = Object.entries(response.data).map(([id, device]) => ({
        id: parseInt(id),
        ...device,
        status: device.commands && device.commands.length > 0 ? 'ready' : 'connected',
        ipAddress: device.ipAddress || 'Not available'
      }));
      
      setDevices(devicesList);
      
    } catch (error) {
      addTerminalLog('Failed to fetch FastAPI devices: ' + (error.response?.data?.detail || error.message), 'error');
    }
  };

  // Отправка команды через FastAPI
  const sendCommand = async (deviceId, command) => {
    try {
      await axios.post(`${API_BASE_URL}/device/process/addCommand`, {
        device_id: deviceId,
        command: command
      }, {
        headers: { Authorization: sessionId }
      });
      
      addTerminalLog(`Command sent to device ${deviceId}`, 'success');
      fetchDevices();
      
    } catch (error) {
      addTerminalLog('Failed to send command: ' + (error.response?.data?.detail || error.message), 'error');
    }
  };

  // Отправка START команды через WebSocket
  const sendStartCommand = () => {
    if (!selectedDevice) return;
    
    const wsDevice = connectedDevices.find(d => d.deviceId === selectedDevice.deviceId);
    
    if (!wsDevice || !socketRef.current) {
      addTerminalLog('Device not connected via WebSocket', 'error');
      return;
    }
    
    addTerminalLog(`Sending START command to device: ${wsDevice.deviceId}`, 'command');
    
    socketRef.current.emit('start-command', {
      deviceId: wsDevice.deviceId,
      timestamp: new Date().toISOString()
    });
  };

  // Выход
  const handleLogout = () => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
    
    setSessionId('');
    setIsLoggedIn(false);
    setCurrentUser(null);
    setDevices([]);
    setConnectedDevices([]);
    setSelectedDevice(null);
    setConnectionStatus('disconnected');
    setNotifications([]);
    setTerminalLogs([]);
  };

  const clearTerminal = () => {
    setTerminalLogs([{
      id: Date.now(),
      message: 'Terminal cleared',
      type: 'info',
      time: new Date().toLocaleTimeString()
    }]);
  };

  const clearNotifications = () => {
    setNotifications([{
      id: Date.now(),
      title: 'Welcome',
      message: 'Notifications cleared',
      type: 'info',
      time: new Date().toLocaleTimeString()
    }]);
  };

  // Эффекты
  useEffect(() => {
    if (isLoggedIn) {
      const interval = setInterval(fetchDevices, 5000);
      return () => clearInterval(interval);
    }
  }, [isLoggedIn, sessionId]);

  useEffect(() => {
    addTerminalLog('Client started', 'info');
  }, []);

  // Рендер экранов
  if (!isLoggedIn) {
    return (
      <div className="screen active">
        <div className="login-container">
          <div className="login-card">
            <div className="login-header">
              <h1>Device Control Client</h1>
              <p>Sign in to manage devices</p>
            </div>
            
            <form onSubmit={handleLogin}>
              <div className="input-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  placeholder="Enter username"
                  value={login}
                  onChange={(e) => setLogin(e.target.value)}
                  required
                />
              </div>
              
              <div className="input-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              
              <button type="submit" className="login-btn">Sign In</button>
            </form>
            
            <div className="demo-accounts">
              <h3>Demo Accounts</h3>
              <div className="account admin">
                <strong>admin</strong> / admin123 <em>(Full access)</em>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="screen active">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <h1>Device Control Panel <span className="user-role role-admin">ADMIN</span></h1>
            <div className="user-info">
              Welcome, <span>{currentUser?.username || 'User'}</span>
            </div>
          </div>
          <div className="header-right">
            <div className="connection-status">
              <span className={`status-indicator ${connectionStatus}`}></span>
              <span>{connectionStatus.charAt(0).toUpperCase() + connectionStatus.slice(1)}</span>
            </div>
            <button className="logout-btn" onClick={handleLogout}>Sign Out</button>
          </div>
        </div>
      </header>

      <div className="admin-dashboard-content">
        {/* Devices Panel */}
        <div className="panel">
          <div className="panel-header">
            <h2>Connected Devices</h2>
            <span className="device-count">{connectedDevices.length} devices</span>
          </div>
          <div className="panel-content">
            <div className="devices-list">
              {connectedDevices.length === 0 ? (
                <div className="no-devices">No devices connected</div>
              ) : (
                connectedDevices.map(device => (
                  <div
                    key={device.deviceId}
                    className={`device-item ${device.status} ${selectedDevice?.deviceId === device.deviceId ? 'selected' : ''}`}
                    onClick={() => setSelectedDevice(device)}
                  >
                    <div className="device-header">
                      <div className="device-id">{device.deviceId}</div>
                      <div className={`device-status status-${device.status}`}>
                        {device.status.toUpperCase()}
                      </div>
                    </div>
                    <div className="device-info">
                      <strong>Name:</strong> {device.name || 'N/A'} | 
                      <strong> Type:</strong> {device.type} | 
                      <strong> Since:</strong> {new Date(device.registeredAt).toLocaleTimeString()}
                    </div>
                    {device.ipAddress && (
                      <div className="device-ip">{device.ipAddress}</div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Control Panel */}
        <div className="panel">
          <div className="panel-header">
            <h2>Device Control</h2>
          </div>
          <div className="panel-content">
            <div className="control-section">
              <h3>Send Command to Selected Device</h3>
              
              {selectedDevice && (
                <div className="selected-device-info">
                  <h4>Selected Device</h4>
                  <div>
                    <strong>ID:</strong> {selectedDevice.deviceId}<br/>
                    <strong>Name:</strong> {selectedDevice.name || 'N/A'}<br/>
                    <strong>Status:</strong> {selectedDevice.status}<br/>
                    <strong>IP:</strong> {selectedDevice.ipAddress || 'Not available'}<br/>
                    <strong>Connected:</strong> {new Date(selectedDevice.registeredAt).toLocaleString()}
                  </div>
                </div>
              )}
              
              <button 
                className="start-btn" 
                onClick={sendStartCommand}
                disabled={!selectedDevice}
              >
                🚀 Send START Command
              </button>
            </div>
            
            <div className="control-section">
              <h3>Quick Actions</h3>
              <button 
                className="start-btn" 
                style={{background: '#f39c12'}}
                onClick={() => connectedDevices.forEach(device => {
                  if (socketRef.current) {
                    socketRef.current.emit('start-command', {
                      deviceId: device.deviceId,
                      timestamp: new Date().toISOString()
                    });
                  }
                })}
                disabled={connectedDevices.length === 0}
              >
                ⚡ Start All Devices
              </button>
            </div>
          </div>
        </div>

        {/* Notifications Panel */}
        <div className="panel">
          <div className="panel-header">
            <h2>Activity Log</h2>
            <button className="terminal-btn clear" onClick={clearNotifications}>Clear</button>
          </div>
          <div className="panel-content">
            <div className="notifications-list">
              {notifications.length === 0 ? (
                <div className="notification info">
                  <div className="notification-title">Welcome, Administrator</div>
                  <div className="notification-message">You have full access to device management</div>
                  <div className="notification-time">{new Date().toLocaleTimeString()}</div>
                </div>
              ) : (
                notifications.map(notification => (
                  <div key={notification.id} className={`notification ${notification.type}`}>
                    <div className="notification-title">{notification.title}</div>
                    <div className="notification-message">{notification.message}</div>
                    <div className="notification-time">{notification.time}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Server Terminal Panel */}
        <div className="panel">
          <div className="panel-header">
            <h2>Server Terminal</h2>
            <div style={{display: 'flex', gap: '8px'}}>
              <button className="terminal-btn" onClick={clearTerminal}>Clear</button>
              <button className="terminal-btn" onClick={() => setTerminalPaused(!terminalPaused)}>
                {terminalPaused ? 'Resume' : 'Pause'}
              </button>
            </div>
          </div>
          <div className="panel-content">
            <div className="terminal">
              {terminalLogs.map(log => (
                <div key={log.id} className={`log-entry log-${log.type}`}>
                  <span className="log-time">[{log.time}]</span> {log.message}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* NEW: Device Terminal Panel */}
        <Terminal 
          selectedDevice={selectedDevice}
          socket={socketRef.current}
          onTerminalLog={(message, type) => addTerminalLog(message, type)}
        />
      </div>
    </div>
  );
}

export default App;