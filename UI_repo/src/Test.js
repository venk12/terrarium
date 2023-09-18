import React from 'react'
import { useState } from 'react';
import axios from 'axios';

function Test()  {
  const [data, setData] = useState(null);

  const fetchData = () => {
    // Define the FastAPI endpoint URL
    const apiUrl = 'http://localhost:8000/test'; // Replace with your actual FastAPI URL

    // Make a GET request to the FastAPI endpoint using Axios
    axios.get(apiUrl)
      .then((response) => {
        setData(response.data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  return (
    <div className="App">
      <h1>FastAPI GET Request Example with Axios</h1>
      <button onClick={fetchData}>Fetch Data</button>
      {data ? (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      ) : (
        <p>Click the button to fetch data</p>
      )}
    </div>
  );
}

export default Test
