import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Styles/App.css';
import accountRecovery from './Images/Recovery.png';
import bar from './Images/NotigatherBar.png'

function AccountRecovery(){
    const [email, setEmail] = useState('');
    const navigate = useNavigate();
    const [errorMessage, setErrorMessage] = useState('')

    function handleEmailChange(event){
      setErrorMessage('');
      setEmail(event.target.value);
    }

    function handleSubmit(event) {
        event.preventDefault();

        if(email === '' ){
          setErrorMessage('Please provide an email')
          return;
        }
    
        setErrorMessage('')
        
        const formData = {
          email: email,
        };
    
        fetch('http://127.0.0.1:5000/account_recovery', {
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
              alert('Recovery Failed');
          }
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
            <img src={accountRecovery} alt='Account Recovery'></img>
            <img src={bar} alt='bar'></img>
          </div>
          <div className="app-container">
            <div className="App">
                <h1>Recover Account</h1>
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
                  {errorMessage && <p className="error">{errorMessage}</p>}
                  <button type="submit">Send Email</button>
                </form>
            </div>
          </div>
        </div>
      </>
    );
}

export default AccountRecovery;