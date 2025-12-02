const express = require('express');
const http = require('http');
const path = require('path');

const app = express();
const server = http.createServer(app);
const PORT = process.env.PORT || 3001;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));


app.get('/socket.io/socket.io.js', (req, res) => {
    res.sendFile(path.resolve(__dirname, 'node_modules', 'socket.io-client', 'dist', 'socket.io.js'));
});


app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});


app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'running', 
        service: 'client-web-interface',
        port: PORT,
        timestamp: new Date().toISOString()
    });
});

server.listen(PORT, () => {
    console.log('========================================');
    console.log('Client Web Interface running on port', PORT);
    console.log('========================================');
    console.log('Access the client at: http://localhost:' + PORT);
    console.log('Connecting to server:http://144.31.73.100:4546');
    console.log('Ready for user connections...');
    console.log('============================================');
});