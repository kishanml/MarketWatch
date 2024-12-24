import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:5000');  // Connect to Flask server

function WebSocketTest() {
  const [data, setData] = useState([]);
  const [input, setInput] = useState('');  // Input to send to server
  const [input2, setInput2] = useState('');  // Input to send to server

  useEffect(() => {
    socket.on('stock_data', (newData) => {
      if (newData) {
        console.log("Received data:", newData);
        setData(newData); // Store the string directly if desired
      }
    });

    return () => {
      // Cleanup on component unmount
      socket.off('stock_data');
    };
  }, []);
  // Function to handle data sending
  const sendDataToServer = () => {
    socket.emit('send_data', { instrument: input, type: input2 });
  };

  return (
    <div>
      <h1>Stock Data from Server:</h1>
      {data}
     
      <input 
        type="text" 
        value={input} 
        onChange={(e) => setInput(e.target.value)} 
        placeholder="Enter data to send"
      />
      <input 
        type="text" 
        value={input2} 
        onChange={(e) => setInput2(e.target.value)} 
        placeholder="Enter strike type"
      />
      <button onClick={sendDataToServer}>Send Data to Server</button>
    </div>
  );
}

export default WebSocketTest;
