import React, { useEffect, useState } from 'react';
import ProgressBar from "./ProgressBar";

const Dashboard = () => {
  const [FarmState, setFarmState] = useState({
    "light": 'loading..',
    "pump": 'loading..',
    "humidity": 'loading..',
    "temperature": 'loading..',
    "water_presence": 'loading..',
    "co2": 'loading..',
  })
  const [socket, setSocket] = useState(null);
  const [plantGrowthPercentage, setPlantGrowthPercentage] = useState(10);
  const [totalLeaves, setTotalLeaves] = useState(7)
  // const [ph_progress, set_ph_progress] = useState(50)

  useEffect(() => {

    // Establish WebSocket connection
    console.log('Establishing Socket Connection...')
    const socket = new WebSocket('ws://localhost:3389/ws');
    // const socket = new WebSocket('https://terraserver-1-n5851173.deta.app/ws');
    setSocket(socket);

    // Handle incoming messages from the WebSocket server
    socket.onmessage = (event) => {
      console.log(event.data)
      try {
        var command = event.data.split('|')[0]
        var body = event.data.split('|')[1]

        if(command==='broadcast'){
          var curr_status = JSON.parse(body)
          setFarmState(curr_status)
        }

      } catch (error) {
        
      }
      // JSON.parse()
      // const sensor = data[0];
      // setFarmState(data)
      // const status = data[1];
      // if (sensor === 'light') {
      //   setLightStatus(status);
      // } else if (sensor === 'pump') {
      //   setPumpStatus(status);
      // } else if (sensor === 'temperature') {
      //   setPumpStatus(status);
      // }
    };

    // Clean up WebSocket connection on component unmount
    return () => {
      socket.close();
    };

    // For refreshing the dashboard every 10 seconds
    // const interval = setInterval(() => {
    //   // fetchGraphData();
    //  },60*1000);
    //  return () => clearInterval(interval);
  }, []);

  const handleStatusSwitch = (e) => {
    var changed_status
    // console.log(e.target.value)
    if (socket) {
      var state_name = e.target.value
      let curr_status = FarmState[e.target.value]
      if(curr_status === 'on'){changed_status = 'off'}
      if(curr_status === 'off'){changed_status = 'on'}

      try {
        // socket.send(`update|${state_name}:${changed_status}`);
        // socket.send('light:off')
        

      } catch (error) {
        console.log('Update not sent to server!')
      }
          
      setFarmState(prevState => {
        return {
          ...prevState, [state_name]:changed_status
        }
      }) 

      }
  }
// };
  // const handleTogglePump = () => {
  //   if (socket) {
  //     const newStatus = !pumpStatus;
  //     setPumpStatus(newStatus);
  //     socket.send(`${newStatus ? 'pump:on' : 'pump:off'}`);
  //   }
  // };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Dashboard</h2>
      {/* <div>{JSON.stringify(FarmState)}</div> */}

      <div className="my-2">
        <div className="px-2 py-2 flex">
          
        <h3 className='font-bold'>Growth Progress: </h3>
          <div className='px-2'>
            <ProgressBar percentage={plantGrowthPercentage} totalLeaves={totalLeaves}/>
          </div>
        </div>
        
        <h3 className="my-2 text-m font-bold">Light Status: {FarmState['light']}</h3>
        <button
          onClick={handleStatusSwitch} value = 'light'
          className={`py-2 px-4 rounded ${
            FarmState['light'] === 'off' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
          }`}>
          {FarmState['light'] === 'off' ?  'turn on ': 'turn off'}
        </button>


        <h3 className="my-2 text-m font-bold">Pump Status: {FarmState['pump']}</h3>
        <button
          onClick={handleStatusSwitch} value = 'pump'
          className={`py-2 px-4 rounded ${
            FarmState['pump'] === 'off' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
          }`}>
          {FarmState['pump'] === 'off' ?  'turn on ': 'turn off'}
        </button>
          
        <h3 className="font-bold my-2 text-m font-normal">Temperature Status:</h3>
        <h4 className=''> Top: {FarmState['temperature'][0]} °C</h4>
        <h4 className=''> Middle: {FarmState['temperature'][1]} °C</h4>
        <h4 className=''> Bottom: {FarmState['temperature'][2]} °C</h4>

        <h3 className="font-bold my-2 text-m font-normal">CO2 Status: </h3>
        <h4>{FarmState['co2']} ppm</h4>

        <h3 className="font-bold my-2 text-m font-normal">Humidity Status: </h3>
        <h4 className=''> Top: {FarmState['humidity'][0]} %</h4>
        <h4 className=''> Middle: {FarmState['humidity'][1]} %</h4>
        <h4 className=''> Bottom: {FarmState['humidity'][2]} %</h4>


        <h3 className="my-2 text-m font-normal">Water Presence Status: {FarmState['water_presence']} (0 = No Water)</h3>

      </div>
      {/* <div className="mb-4">
        <h3 className="text-lg font-semibold">Light Status: {lightStatus ? lightStatus : 'Loading...'}</h3>
        <button
          onClick={handleToggleLight}
          className={`py-2 px-4 rounded ${
            lightStatus ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
          }`}
        >
          {lightStatus === 'on' ?  'turn off ': 'turn on'}
        </button>
      </div> */}
      {/* <div>
        <h3 className="text-lg font-semibold">Pump Status: {pumpStatus ? pumpStatus : 'Loading...'}</h3>
        <button
          onClick={handleTogglePump}
          className={`py-2 px-4 rounded ${
            pumpStatus ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
          }`}
        >
          {pumpStatus === 'on' ?  'turn off ': 'turn on'}
        </button>
      </div> */}
    </div>
  );
};

export default Dashboard;
