import React, { useState, useEffect, useRef } from 'react';
import './Terminal.css';

const Terminal = ({ selectedDevice, socket, onTerminalLog }) => {
  const [command, setCommand] = useState('');
  const [terminalLogs, setTerminalLogs] = useState([]);
  const [terminalPaused, setTerminalPaused] = useState(false);
  const terminalRef = useRef(null);
  const inputRef = useRef(null);

  // Инициализация терминала
  useEffect(() => {
    addTerminalLog('Terminal ready. Select a device and enter commands.', 'system');
  }, []);

  // Авто-скролл при новых логах
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalLogs]);

  // Фокусировка на input при выборе устройства
  useEffect(() => {
    if (selectedDevice && inputRef.current) {
      inputRef.current.focus();
    }
  }, [selectedDevice]);

  // Обработка ответов от сервера
  useEffect(() => {
    if (!socket) return;

    const handleTerminalResponse = (data) => {
      const deviceName = data.deviceName || data.deviceId;
      addTerminalLog(`[${deviceName}] ${data.response}`, 'response');
      if (onTerminalLog) {
        onTerminalLog(`Device ${deviceName}: ${data.response}`, 'response');
      }
    };

    const handleTerminalError = (error) => {
      addTerminalLog(`Error: ${error}`, 'error');
    };

    socket.on('terminal-response', handleTerminalResponse);
    socket.on('terminal-error', handleTerminalError);

    return () => {
      socket.off('terminal-response', handleTerminalResponse);
      socket.off('terminal-error', handleTerminalError);
    };
  }, [socket, onTerminalLog]);

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

  const executeCommand = () => {
    if (!selectedDevice) {
      addTerminalLog('Please select a device first', 'error');
      return;
    }

    const cmd = command.trim();
    if (!cmd) {
      addTerminalLog('Please enter a command', 'error');
      return;
    }

    addTerminalLog(`$ ${cmd}`, 'command');
    
    if (socket && selectedDevice) {
      socket.emit('terminal-command', {
        deviceId: selectedDevice.deviceId,
        command: cmd
      });
    }

    setCommand('');
  };

  const clearTerminal = () => {
    setTerminalLogs([{
      id: Date.now(),
      message: 'Terminal cleared',
      type: 'system',
      time: new Date().toLocaleTimeString()
    }]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      executeCommand();
    } else if (e.ctrlKey && e.key === 'l') {
      e.preventDefault();
      clearTerminal();
    } else if (e.ctrlKey && e.key === 'c') {
      addTerminalLog('^C', 'command');
      setCommand('');
    }
  };

  const quickCommands = [
    { cmd: 'help', label: 'help' },
    { cmd: 'status', label: 'status' },
    { cmd: 'info', label: 'info' },
    { cmd: 'ls', label: 'ls' },
    { cmd: 'pwd', label: 'pwd' },
    { cmd: 'python --version', label: 'python' },
    { cmd: 'echo Hello', label: 'echo' },
    { cmd: 'date', label: 'date' }
  ];

  return (
    <div className="terminal-container">
      <div className="terminal-header">
        <h3>Device Terminal</h3>
        <div className="terminal-controls">
          <button className="terminal-btn" onClick={clearTerminal}>Clear</button>
          <button 
            className="terminal-btn" 
            onClick={() => setTerminalPaused(!terminalPaused)}
          >
            {terminalPaused ? 'Resume' : 'Pause'}
          </button>
        </div>
      </div>

      <div className="terminal-content">
        <div className="device-info">
          {selectedDevice ? (
            <div className="device-selected">
              <strong>Connected to:</strong> {selectedDevice.deviceId} - {selectedDevice.name || 'Device'} ({selectedDevice.status})
            </div>
          ) : (
            <div className="device-not-selected">
              <span className="warning-icon">⚠</span> No device selected. Please select a device from the list above.
            </div>
          )}
        </div>

        <div className="terminal-output" ref={terminalRef}>
          {terminalLogs.map(log => (
            <div key={log.id} className={`terminal-log terminal-log-${log.type}`}>
              <span className="log-time">[{log.time}]</span> {log.message}
            </div>
          ))}
        </div>

        <div className="quick-commands">
          {quickCommands.map((quick, index) => (
            <button
              key={index}
              className="quick-command-btn"
              onClick={() => {
                setCommand(quick.cmd);
                inputRef.current.focus();
              }}
              title={quick.cmd}
            >
              {quick.label}
            </button>
          ))}
        </div>

        <div className="terminal-input-container">
          <span className="terminal-prompt">
            {selectedDevice ? `PS ${selectedDevice.deviceId}>` : 'PS>'}
          </span>
          <input
            ref={inputRef}
            type="text"
            className="terminal-input"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Enter command (e.g., help, ls, echo hello)"
            disabled={!selectedDevice}
          />
          <button 
            className="terminal-send-btn"
            onClick={executeCommand}
            disabled={!selectedDevice || !command.trim()}
          >
            Send
          </button>
        </div>

        <div className="terminal-hints">
          <small>
            <strong>Tips:</strong> Press <kbd>Enter</kbd> to send • <kbd>Ctrl+L</kbd> to clear • <kbd>Ctrl+C</kbd> to cancel
          </small>
        </div>
      </div>
    </div>
  );
};

export default Terminal;