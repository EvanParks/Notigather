import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Styles/App.css';
import accountRecovery from './Images/Recovery.png';
import bar from './Images/NotigatherBar.png'

function RecoverAccount(){
    const [username, setUsername] = useState('');
    const [newPassword, setPassword] = useState('');
    const navigate = useNavigate();
    const location = useLocation();
    const [token, setToken] = useState(null);
    const specialCharPattern = /[^a-zA-Z0-9]/;
    const [errorMessage, setErrorMessage] = useState('')


    function handleUsernameChange(event){
      setErrorMessage('');
      setUsername(event.target.value);
    }

    function handlePasswordChange(event){
      setErrorMessage('');
      setPassword(event.target.value);
    }

    useEffect(() => {
      const values = new URLSearchParams(location.search);
      const token = values.get('token');

      setToken(token);

      if (!token) {
          navigate('/');
      }
    }, [navigate, location.search]);

    function handleSubmit(event) {
        event.preventDefault();

        if(!specialCharPattern.test(newPassword)){
          setErrorMessage('Passwords must include a special character');
          return; 
        }
    
        if(newPassword.length < 8){
          setErrorMessage('Passwords must be at least 8 characters long');
          return;
        }
    
        if(newPassword === '' ){
          setErrorMessage('Please provide a password')
          return;
        }
    
        setErrorMessage('')
        
        const formData = {
          username : username,
          newPassword : newPassword, 
          token : token
        };
    
        fetch('http://127.0.0.1:5000/update_password', {
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
              navigate('/');
          } else {
            setErrorMessage('Invalid username or the link has expired')
          }
          setUsername('');
          setPassword('');
        })
        .catch(error => {
          console.error('There was a problem:', error);
          navigate('/');
        });
      }

    return (
      <>
        <div className="background"></div>
        <div className="main-container">
          <div className="notigather">
            <img src={accountRecovery} alt='Account Recovery'></img>
            <img src={bar} alt='bar'></img>
          </div>
          <div className="app-container">
            <div className="App">
                <h1>Update Password</h1>
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
                          value={newPassword} 
                          placeholder='New Password'
                          onChange={handlePasswordChange} 
                          required 
                      />
                  </div>
                  {errorMessage && <p className="error">{errorMessage}</p>}
                  <button type="submit">Submit</button>
                </form>
            </div>
          </div>
        </div>
      </>
    );
}

export default RecoverAccount;