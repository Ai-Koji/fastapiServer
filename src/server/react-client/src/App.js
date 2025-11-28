import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './css/App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [sessionId, setSessionId] = useState('');
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [notifications, setNotifications] = useState([]);
  const [terminalLogs, setTerminalLogs] = useState([]);
  const [terminalPaused, setTerminalPaused] = useState(false);

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

  // Терминал
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

  // Авторизация
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE_URL}/client/auth/login`, {
        login,
        password
      });
      
      setSessionId(response.data.session_id);
      setIsLoggedIn(true);
      setConnectionStatus('connected');
      addTerminalLog('Authentication successful', 'success');
      addNotification('Login Successful', 'Connected to server successfully', 'success');
      
    } catch (error) {
      addTerminalLog('Login failed: ' + (error.response?.data?.detail || error.message), 'error');
      alert('Login failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Получение устройств
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
      addTerminalLog(`Devices updated: ${devicesList.length} devices`, 'info');
      
    } catch (error) {
      addTerminalLog('Failed to fetch devices: ' + (error.response?.data?.detail || error.message), 'error');
    }
  };

  // Отправка команды
  const sendCommand = async (deviceId, command) => {
    try {
      await axios.post(`${API_BASE_URL}/device/process/addCommand`, {
        device_id: deviceId,
        command: command
      }, {
        headers: { Authorization: sessionId }
      });
      
      addTerminalLog(`Command sent to device ${deviceId}`, 'success');
      addNotification('Command Sent', `Command sent to device ${deviceId}`, 'success');
      fetchDevices();
      
    } catch (error) {
      addTerminalLog('Failed to send command: ' + (error.response?.data?.detail || error.message), 'error');
    }
  };

  // Выход
  const handleLogout = () => {
    setSessionId('');
    setIsLoggedIn(false);
    setDevices([]);
    setSelectedDevice(null);
    setConnectionStatus('disconnected');
    setNotifications([]);
    setTerminalLogs([]);
    addTerminalLog('Client disconnected', 'info');
  };

  // Эффекты
  useEffect(() => {
    if (isLoggedIn) {
      fetchDevices();
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
              <h3>Demo Account</h3>
              <div className="account admin">
                <strong>admin</strong> / admin
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
              Welcome, <span>admin</span>
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
            <span className="device-count">{devices.length} devices</span>
          </div>
          <div className="panel-content">
            <div className="devices-list">
              {devices.length === 0 ? (
                <div className="no-devices">No devices connected</div>
              ) : (
                devices.map(device => (
                  <div
                    key={device.id}
                    className={`device-item ${device.status} ${selectedDevice?.id === device.id ? 'selected' : ''}`}
                    onClick={() => setSelectedDevice(device)}
                  >
                    <div className="device-header">
                      <div className="device-id">Device {device.id}</div>
                      <div className={`device-status status-${device.status}`}>
                        {device.status.toUpperCase()}
                      </div>
                    </div>
                    <div className="device-info">
                      <strong>Session:</strong> {device.sessionID?.substring(0, 8)}... | 
                      <strong> Commands:</strong> {device.commands?.length || 0}
                    </div>
                    {device.ipAddress && device.ipAddress !== 'Not available' && (
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
                    <strong>ID:</strong> {selectedDevice.id}<br/>
                    <strong>Status:</strong> {selectedDevice.status}<br/>
                    <strong>IP:</strong> {selectedDevice.ipAddress}<br/>
                    <strong>Commands:</strong> {selectedDevice.commands?.length || 0}
                  </div>
                </div>
              )}
              
              <button 
                className="start-btn" 
                onClick={() => selectedDevice && sendCommand(selectedDevice.id, { type: "start", programId: 1 })}
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
                onClick={() => devices.forEach(device => sendCommand(device.id, { type: "start", programId: 1 }))}
                disabled={devices.length === 0}
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

        {/* Terminal Panel */}
        <div className="panel">
          <div className="panel-header">
            <h2>Connection Terminal</h2>
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
      </div>
    </div>
  );
}

export default App;