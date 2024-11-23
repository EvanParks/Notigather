import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Styles/App.css';
import accountCreation from './Images/AccountCreation.png';
import bar from './Images/NotigatherBar.png'

function CreateAccount() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const navigate = useNavigate();
  const specialCharPattern = /[^a-zA-Z0-9]/;
  const [errorMessage, setErrorMessage] = useState('')

  function handleUsernameChange(event) {
    setErrorMessage('');
    setUsername(event.target.value);
  }

  function handlePasswordChange(event) {
    setErrorMessage('');
    setPassword(event.target.value);
  }

  function handleEmailChange(event) {
    setErrorMessage('');
    setEmail(event.target.value);
  }

  function handleSubmit(event) {
    event.preventDefault();

    if(!specialCharPattern.test(password)){
      setErrorMessage('Passwords must include a special character');
      return; 
    }

    if(password.length < 8){
      setErrorMessage('Passwords must be at least 8 characters long');
      return;
    }

    if(username === '' ){
      setErrorMessage('Please provide a username')
      return; 
    }

    if(password === '' ){
      setErrorMessage('Please provide a password')
      return;
    }

    if(email === '' ){
      setErrorMessage('Please provide an email address')
      return; 
    }

    setErrorMessage('')

    const formData = {
      email: email,
      username: username,
      password: password
    };

    fetch('http://127.0.0.1:5000/register', {
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
          alert('Account Created');
          navigate('/');
      } else {
        setErrorMessage('Username or email already exists');
      }
      setUsername('');
      setPassword('');
      setEmail('');
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
          <img src={accountCreation} alt='Account Creation'></img>
          <img src={bar} alt='bar'></img>
        </div>
        <div className="app-container">
          <div className="App">
            <h1>Create Account</h1>
            <form onSubmit={handleSubmit}>
              <div>
                <input 
                  type="text" 
                  id="email" 
                  value={email} 
                  placeholder='Email'
                  onChange={handleEmailChange} 
                  required 
                />
              </div>
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
              {errorMessage && <p className="error">{errorMessage}</p>}
              <button className="createaccount" type="submit">Create Account</button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}

export default CreateAccount;