import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';
import Email from './Messages.js';
import './Styles/App.css';
import './Styles/Dashboard.css';
import googleLogo from './Images/googleImage.webp';
import slackLogo from './Images/slackImage.png';
import outlookLogo from './Images/outlookImage.webp';

function Dashboard() {
  const [emails, setEmails] = useState([]);
  const navigate = useNavigate();
  const [sources, setSources] = useState(['Google', 'Outlook', 'Slack']);
  const [isTabFocused, setIsTabFocused] = useState(true);
  const [oldMessages, setOldMessages] = useState([]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsTabFocused(!document.hidden);
      if (!document.hidden) {
        document.title = "Notigather";
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  useEffect(() => {
    if (!isTabFocused && emails.length > 0 && emails[0].messageId) {
      const oldMessageIds = oldMessages.map(email => email.messageId);
      if (!oldMessageIds.includes(emails[0].messageId)) {
        document.title = "Notigather - New Messages!";
      }
    }

    setOldMessages(emails);
  }, [emails, isTabFocused, oldMessages]);

  const handleCheckboxChange = (event) => {
    const {name, checked} = event.target;
  
    if (checked) {
      setSources((sources) => [...sources, name]);
    }
    else {
      setSources((sources) => sources.filter(source => source !== name));
    }
  }

  const signOut = useCallback(async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/signout', { 
        method: 'POST',
        credentials: 'include', 
      });
      
      if(!response.ok) {
        throw new Error('Response not ok')
      }
      navigate('/');
    } catch (error) {
      console.error('There was a problem:', error);
    }
  }, [navigate]);

  const refreshTokens = useCallback(async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get_new_tokens', {
        method: 'POST',
        credentials: 'include',
      }); 
        
      if (!response.ok) {
        throw new Error('Response not ok');
      }
      return response.json();
    } catch (error) {
      console.error('There was a problem:', error);
    }
  }, []); 

  const handleSlackLogin = async () => {
    let number_of_retries = 2;

    while (number_of_retries > 0) {
      try {
          const response = await fetch('http://127.0.0.1:5000/slackoauth2call', { 
            method: 'GET',
            credentials: 'include', 
          });

          if (!response.ok) {
            throw new Error('Response not ok');
          }
          const data = await response.json();

          if (data.token_status === 'Logout') {
              signOut(); 
              number_of_retries = 0;
              return; 
          } else if (data.token_status === undefined) {
              signOut();
              return;
          } else if (data.token_status === 'Refresh') {
              await refreshTokens(); 
              number_of_retries--; 
          } else if (data.token_status === '') {
              let authorization_url = data.url;
              window.location.href = authorization_url;
              handleRefresh();  
              return; 
          }
      } catch (error) {
        console.error('There was a problem:', error);
        number_of_retries--; 
      }
    }
    signOut();
  };

  const handleOutlookLogin = async () => {
    let number_of_retries = 2;

    while (number_of_retries > 0) {
      try {
          const response = await fetch('http://127.0.0.1:5000/outlookoauth2call', { 
            method: 'GET',
            credentials: 'include', 
          });

          if (!response.ok) {
            throw new Error('Response not ok');
          }
          const data = await response.json();

          if (data.token_status === 'Logout') {
              signOut(); 
              number_of_retries = 0; 
              return;
          } else if (data.token_status === undefined) {
              signOut();
              return;
          } else if (data.token_status === 'Refresh') {
              await refreshTokens(); 
              number_of_retries--; 
          } else if (data.token_status === '') {
              let authorization_url = data.url;
              window.location.href = authorization_url; 
              handleRefresh(); 
              return; 
          }
      } catch (error) {
        console.error('There was a problem:', error);
        number_of_retries--; 
      }
    }
    signOut();
  };

  const handleGoogleLogin = async () => {
    let number_of_retries = 2;

    while (number_of_retries > 0) {
      try {
          const response = await fetch('http://127.0.0.1:5000/oauth2call', { 
            method: 'GET',
            credentials: 'include', 
          });

          if (!response.ok) {
            throw new Error('Response not ok');
          }

          const data = await response.json();

          if (data.token_status === 'Logout') {
              signOut(); 
              number_of_retries = 0;
              return; 
          } else if (data.token_status === undefined) {
              signOut();
              return;
          } else if (data.token_status === 'Refresh') {
              await refreshTokens(); 
              number_of_retries--; 
          } else if (data.token_status === '') {
              let authorization_url = data.url;
              window.location.href = authorization_url; 
              handleRefresh(); 
              return; 
          }
      } catch (error) {
        console.error('There was a problem:', error);
        number_of_retries--; 
      }
    }
    signOut();
  };

  const handleRefresh = useCallback(async () => {
    console.log('Handling Refresh');
    let number_of_retries = 2;

    while (number_of_retries > 0) {
      console.log('In loop'); 
      try {
          const response = await fetch('http://127.0.0.1:5000/get_messages', {
            method: 'GET',
            credentials: 'include',
          });

          if (!response.ok) {
            throw new Error('Response not ok');
          }

          const data = await response.json();

          if (data.token_status === 'Logout') {
              signOut();
              number_of_retries = 0; 
              return;
          } else if (data.token_status === 'Refresh') {
              await refreshTokens();
              number_of_retries--; 
          } else {
              setEmails(data); 
              return; 
          }
      } catch (error) {
        console.error('There was a problem:', error);
        number_of_retries--; 
      }
    }
    signOut(); 
  }, [signOut, refreshTokens]); 

  useEffect(() => {
    handleRefresh();

    const interval = setInterval(handleRefresh, 300000);

    return () => clearInterval(interval)
  }, [handleRefresh]);

  return (
    <div>
      <div className="header-container">
        <div className="header">
          <div className="header-title">Notification Center</div>
          <div className="signout-button-container">
            <button onClick={signOut}>Sign Out</button>
          </div>
        </div>
      </div>
      <div className="button-container">
        <button onClick={handleGoogleLogin}><img src={googleLogo} alt="Google" /></button>
        <button onClick={handleSlackLogin}><img src={slackLogo} alt="Slack" /></button>
        <button onClick={handleOutlookLogin}><img src={outlookLogo} alt="Teams" /></button>
      </div>
      <div className="refresh-button-container">
        <button onClick={handleRefresh}>Refresh</button>
      </div>
      <div className="email-container">
        <div className="filter-container">
          <label>
            <input
              type="checkbox"
              name="Google"
              defaultChecked={true}
              onChange={handleCheckboxChange}
            />
            Gmail
          </label>
          <label>
            <input
              type="checkbox"
              name="Slack"
              defaultChecked={true}
              onChange={handleCheckboxChange}
            />
            Slack
          </label>
          <label>
            <input
              type="checkbox"
              name="Outlook"
              defaultChecked={true}
              onChange={handleCheckboxChange}
            />
            Outlook
          </label>
        </div>
        {emails.map((email, index) => (
          <Email key={index} email={email} sources={sources} setEmails={setEmails} />
        ))}
      </div>
    </div>
  );
}

export default Dashboard;