import React, { useState } from 'react';

function App() {
  const [match, setMatch] = useState('');
  const [result, setResult] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:5000/process_match', {
        method: 'POST',
        body: JSON.stringify({ match: match }),
      }); 
      // console.log("hey")

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data.result);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="App">
      <form onSubmit={handleSubmit}>
        <label>
          Match:
          <input 
            type="text" 
            value={match} 
            onChange={(e) => setMatch(e.target.value)} 
          />
        </label>
        <button type="submit">Submit</button>
      </form>
      {result && <p>Result: {result}</p>}
    </div>
  );
}

export default App;
