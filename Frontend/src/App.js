import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { NavLink } from 'react-router-dom'; 
import './Styles/App.css';
import notigather from './Images/NotigatherText.png';
import notigatheradditionaltext from './Images/NotigatherAdditionalText.png';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState('')

  function handleUsernameChange(event) {
    setErrorMessage('');
    setUsername(event.target.value);
  }

  function handlePasswordChange(event) {
    setErrorMessage('');
    setPassword(event.target.value);
  }

  function handleSubmit(event) {
    event.preventDefault();

    if(username === '' ){
      setErrorMessage('Please provide a username')
      return
    }

    if(password === '' ){
      setErrorMessage('Please provide a password')
      return
    }

    setErrorMessage('')
    
    const formData = {
      username: username,
      password: password
    };

    fetch('http://127.0.0.1:5000/verify', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Response not ok');
      }
      return response.json();
    })
    .then(data => {
      if (data.message === true) {
          navigate('/dashboard');
      } else {
          setErrorMessage('Invalid Username or Password');
      }
      setUsername('');
      setPassword('');
    })
    .catch(error => {
      console.error('There was a problem:', error);
    });
  }

  return (
  <>
    <div className="background"></div>
    <div className="main-container">
      <div className="notigather">
        <img src={notigather} alt='Notigather'></img>
        <img src={notigatheradditionaltext} alt='Notigather'></img>
      </div>
      <div className="app-container">
        <div className="App">
          <h1>Login</h1>
          <form onSubmit={handleSubmit}>
            <div>
              <input 
                type="text" 
                id="username" 
                value={username} 
                placeholder='Username'
                onChange={handleUsernameChange} 
                required 
              />
            </div>
            <div>
              <input 
                type="password" 
                id="password" 
                value={password}
                placeholder='Password' 
                onChange={handlePasswordChange} 
                required 
              />
            </div>
            <button type="submit">Sign In</button>
            {errorMessage && <div className="error">{errorMessage}</div>}
            <NavLink to="/accountrecovery" style={{ color: 'blue', textAlign: "center", textDecoration: 'underline' }}>
                Forgot Password?
            </NavLink>
            <div className="createaccount">
              <p>Don't have an account?</p>
              <button onClick={() => navigate('/createaccount')}>Create Account</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </>
  );
}

export default App;