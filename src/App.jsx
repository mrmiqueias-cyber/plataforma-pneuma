import React, { useState } from 'react';
import Login from './Login';
import Chat from './Chat';

function App() {
  const [appState, setAppState] = useState('login');

  return (
    <>
      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        body {
          font-family: Arial, sans-serif;
        }
      `}</style>
      {appState === 'login' ? (
        <Login setAppState={setAppState} />
      ) : (
        <Chat />
      )}
    </>
  );
}

export default App;
