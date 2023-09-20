// import axios from 'axios';
import React, { useEffect, useState } from 'react';
import ProgressBar from "./ProgressBar";

function Test()  {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [socket, setSocket] = useState(null);
  const [FarmState, setFarmState] = useState({
    "light": 'loading..',
    "pump": 'loading..',
    "humidity": 'loading..',
    "temperature": 'loading..',
    "water_presence": 'loading..',
    "co2": 'loading..',
  })
  const [plantGrowthPercentage, setPlantGrowthPercentage] = useState(10);
  const [totalLeaves, setTotalLeaves] = useState(7)

  useEffect(() => {

    console.log("useeFFECT TRIGGERERD!")
    // Establish a WebSocket connection when the component mounts
    const newSocket = new WebSocket('ws://localhost:8000/ws'); // Replace with your WebSocket server address

    newSocket.addEventListener('open', (event) => {
      console.log('WebSocket connection opened:', event);

      // You can send an initial message if needed
      newSocket.send('new_connection|key:pair');
    });

    newSocket.addEventListener('message', (event) => {
      // Handle incoming messages from the server
      const message = event.data;
      // setMessages((prevMessages) => [...prevMessages, message]);

      console.log("Received message from server:", message)

      var command = message.split('|')[0]
      
      if(command == 'broadcast'){

        var body = message.split('|')[1]
        var parsed_body = JSON.parse(body)


        console.log('command:', command, " body:", body, " parsed_body:", typeof(parsed_body))

        setFarmState((prevState) => ({
            ...prevState,
            ...parsed_body,
          }));
      }

    });

    newSocket.addEventListener('close', (event) => {
      console.log('WebSocket connection closed:', event);

      // You can attempt to reconnect here if needed
      setSocket(null);
    });

    setSocket(newSocket);

    // Clean up the WebSocket when the component unmounts
    return () => {
      if (newSocket.readyState === 1) {
        newSocket.close();
      }
    };
  }, []);

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
  };

  const sendMessage = () => {
    if (socket && inputMessage) {
      socket.send(inputMessage);
      setInputMessage('');
    }
  };

  const handleStatusSwitch = (e) => {
    // console.log(e.target.value)
    if (socket) {
      var state_name = e.target.value
      let curr_status = FarmState[e.target.value]
      let changed_status
      
      if(curr_status === 'on'){changed_status = 'off'}
      if(curr_status === 'off'){changed_status = 'on'}

      try {
       
        console.log("Sending switch request: "+ `update|${state_name}:${changed_status}`)
        socket.send(`update|${state_name}:${changed_status}`);
      
        setFarmState(prevState => {
          return {
            ...prevState, [state_name]:changed_status
          }
        }) 
      } catch (error) {
        console.log('Update not sent to server!')
      }

    }
  }

  // return (
  //   <div className="App">
  //     <h1>WebSocket Chat App</h1>
  //     <div className="chat-container">
  //       <div className="message-box">
  //         {messages.map((message, index) => (
  //           <div key={index} className="message">
  //             {message}
  //           </div>
  //         ))}
  //       </div>
  //       <div className="input-box">
  //         <input
  //           type="text"
  //           placeholder="Type your message..."
  //           value={inputMessage}
  //           onChange={handleInputChange}
  //         />
  //         <button onClick={sendMessage}>Send</button>
  //       </div>
  //     </div>
  //   </div>
  // );
  return (
    <div id="viewport" className="bg-gray-800 h-screen w-full p-4 lg:p-0 md:p-0 lg:flex">
      {/* sidebar code */}
    <div id="sidebar" className="bg-gray-900 w-full lg:w-64 lg:min-h-screen lg:fixed">
        <div className="bg-gray-900 text-white py-20 pl-10 pr-20 lg:h-full lg:flex lg:flex-col sm:hide">
            <div id="sidebar-top">
              <h3 className="font-bold text-lg lg:text-3xl bg-gradient-to-br from-green-200 to-green-800 bg-clip-text text-transparent">Terra</h3>
              <ul className="mt-4 lg:mt-8">
                    <li className="flex font-bold">
                      <p>Dashboard</p>
                        {/* <a href="/admin/source">Sources</a> */}
                    </li>
                    <li className="flex mt-4 font-light">
                      <p>Settings</p>
                        {/* <a href="/admin/category">Categories</a> */}
                    </li>
                    <li className="flex mt-4 font-light">
                      <p>Documentation</p>
                        {/* <a href="/admin/category">Categories</a> */}
                    </li>
              </ul> 
            </div>
            {/* <div className="flex items-center lg:absolute bottom-10">
                <a href="/logout" className="px-3 py-1 ml-2 text-xs uppercase bg-gray-300 rounded-lg hover:bg-primary hover:text-white">logout</a>
            </div> */}
        </div>
    </div>
    {/* main body */}
    <div id="content" className= "px-2 py-2 w-full h-full lg:ml-64">
      {/* Farm Progress */}
      <div className="bg-gray-900 flex flex-col m-2 p-4 rounded-lg border-2 border-gray-800">
        <div className='text-white'>Farm Progress</div>
        <div className="px-2 py-2 justify-center">
          <div className='text-white px-2'>
            <ProgressBar percentage={plantGrowthPercentage} totalLeaves={totalLeaves}/>
          </div>
        </div>
      </div>
      <div className='lg:flex'>
        {/* Light Status */}
        <div className=" lg:w-1/2 bg-gray-900 flex flex-col m-2 p-4 rounded-lg border-2 border-gray-800">
          <div className='text-white'>Light Status</div>
          <h3 className="text-white my-2 text-m">{FarmState['light']}</h3>
          <button
            onClick={handleStatusSwitch} value = 'light'
            className={`w-1/2 py-2 px-4 rounded ${
              FarmState['light'] === 'off' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
            }`}>
            {FarmState['light'] === 'off' ?  'turn on ': 'turn off'}
          </button>
        </div>
        {/* Water Status */}
        <div className="lg:w-1/2 bg-gray-900 flex flex-col m-2 p-4 rounded-lg border-2 border-gray-800">
          <div className='text-white'>Water Status</div>
          <h3 className="text-white my-2 text-m">{FarmState['pump']}</h3>
          <button
            onClick={handleStatusSwitch} value = 'pump'
            className={`w-1/2 py-2 px-4 rounded ${
              FarmState['pump'] === 'off' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
            }`}>
            {FarmState['pump'] === 'off' ?  'turn on ': 'turn off'}
          </button>
        </div>
      </div>
      <div className='lg:flex text-white'>
        <div className="lg:w-1/3 bg-gray-900 flex flex-col m-2 p-4 rounded-lg border-2 border-gray-800">
            <div className='text-white'>Temperature Status:</div>
            <h4 className=''> Top: {FarmState['temperature'][0]} °C</h4>
            <h4 className=''> Middle: {FarmState['temperature'][1]} °C</h4>
            <h4 className=''> Bottom: {FarmState['temperature'][2]} °C</h4>
        </div>
        <div className="lg:w-1/3 bg-gray-900 flex flex-col m-2 p-4 rounded-lg border-2 border-gray-800">
            <div className='text-white'>CO2 Status: </div>
            <h4>{FarmState['co2']} ppm</h4>
        </div>
        <div className="lg:w-1/3 bg-gray-900 flex flex-col m-2 p-4 rounded-lg border-2 border-gray-800">
            <div className='text-white'>Humidity Status: </div>
            <h4 className=''> Top: {FarmState['humidity'][0]} %</h4>
            <h4 className=''> Middle: {FarmState['humidity'][1]} %</h4>
            <h4 className=''> Bottom: {FarmState['humidity'][2]} %</h4>
        </div>
        {/* <h3 className="my-2 text-m font-normal">Water Presence Status: {FarmState['water_presence']} (0 = No Water)</h3> */}
      </div>
      </div>
</div>
); 
}
export default Test
