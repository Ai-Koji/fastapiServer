import React, { useState } from 'react';
import axios from 'axios';
import './css/App.css';

const API_BASE_URL = 'http://localhost:7070'; // Adjust if server runs on different port

function App() {
  const [sessionId, setSessionId] = useState('');
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [command, setCommand] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // authtorization
  const handleLogin = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/client/auth/login`, {
        login,
        password
      });
      setSessionId(response.data.session_id);
      setIsLoggedIn(true);
    } catch (error) {
      alert('Login failed: ' + error.response?.data?.detail || error.message);
    }
  };

  // get devices info
  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/device/process/listDevices`, {
        headers: { Authorization: sessionId }
      });
      setDevices(response.data);
    } catch (error) {
      alert('Failed to fetch devices: ' + error.response?.data?.detail || error.message);
    }
  };

  // add comand
  const addCommand = async () => {
    if (!selectedDevice || !command) {
      alert('Please select a device and enter a command');
      return;
    }
    try {
      await axios.post(`${API_BASE_URL}/device/process/addCommand`, {
        device_id: parseInt(selectedDevice),
        command: JSON.parse(command) // Assuming command is JSON string
      }, {
        headers: { Authorization: sessionId }
      });
      alert('Command added successfully');
      fetchDevices(); // Refresh devices
    } catch (error) {
      alert('Failed to add command: ' + error.response?.data?.detail || error.message);
    }
  };
  
  const loginPage = () => {
    return (
          <div>
            <input
              type="text"
              placeholder="Login"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button onClick={handleLogin}>Login</button>
          </div>
    )
  }

  const startProcessForm = () => {
    return (
      <div>
        {/* Add select program */}
        <input
          type="text"
          placeholder='Command (e.g. {"type": "start", "programId": 1})'
          value={command}
          onChange={(e) => setCommand(e.target.value)}/>
        <button onClick={addCommand}>start process</button>
      </div>
    )
  }
  const stopProcessForm = () => {
    return (
      <div>
        {/* TODO */}
      </div>
    )
  }
  const showProcessOutput = () => {
    return (
      <div>
        {/* TODO */}
      </div>
    )
  }
  const showProcesses = () => {
    return (
      <div>
        {/* TODO */}
      </div>
    )
  }

  const commandPage = () => {
    return (
          <div className="main-menu">
            <section className="devices-section">
              <button onClick={fetchDevices}>Reload</button>
              <h2>Devices</h2>
              {devices.map(device => (
                <div key={device.id}>
                  <h3>Device {device.id}</h3>
                  <ul>
                    {device.commands.map((cmd, index) => (
                      <li key={index}>{JSON.stringify(cmd)}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </section>
            <section className="command-form">
              <div className="actionType">

              </div>
              <select value={selectedDevice} onChange={(e) => setSelectedDevice(e.target.value)}>
                <option value="">Select Device</option>
                {devices.map(device => (
                  <option key={device.id} value={device.id}>Device {device.id}</option>
                ))}
              </select>

              {/* TODO: good form right here */}
              {
                startProcessForm()
              }
            </section>
          </div>
        )
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Device Management Client</h1>
        {!isLoggedIn ? (loginPage()) : (commandPage())}
      </header>
    </div>
  );
}

export default App;
