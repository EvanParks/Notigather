import React, { useState } from 'react';
import DOMPurify from 'dompurify';
import { useNavigate } from 'react-router-dom'; 
import './Styles/Messages.css';
import googleLogo from './Images/googleImage.webp';
import outlookLogo from './Images/outlookImage.webp';
import slackLogo from './Images/slackImage.png';

const Email = ({ email, sources, setEmails }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const navigate = useNavigate();

  if (!sources.includes(email.source)){
    return null;
  }

  const toggleDetails = () => {
    setIsExpanded(!isExpanded);
  };

  const formatDateTime = (dateTimeString) => {
    const dateObj = new Date(dateTimeString);
    const today = new Date();
    const options = { 
      weekday: 'short', 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    };
    const additionalOptions = {
      month: 'short',
      day: 'numeric'
    }
    const dateFormatted = dateObj.toLocaleDateString('en-US', options);
    const shortDateFormatted = dateObj.toLocaleDateString('en-US', additionalOptions);
    const timeFormatted = dateObj.toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric' });
    
    if (dateObj.toDateString() === today.toDateString()) {
      return { date: dateFormatted, time: timeFormatted, timeOrDate: timeFormatted };
    } else {
      return { date: dateFormatted, time: timeFormatted, timeOrDate: shortDateFormatted };
    }
  };

  const { date, time, timeOrDate } = email.time ? formatDateTime(email.time) : { date: '', time: '', timeOrDate: '' };

  const createMessageHTML = (html) => {
    return { __html: DOMPurify.sanitize(html) };
  };

  function getLogo(email){
    if (email.source === 'Google' ){
      return googleLogo; 
    }else if (email.source === 'Outlook'){
      return outlookLogo; 
    }else if (email.source === 'Slack'){
      return slackLogo; 
    }
  };

  const refreshTokens = async () => {
    let number_of_retries = 2;

    while (number_of_retries > 0) {
      try {
        const response = await fetch('http://127.0.0.1:5000/get_new_tokens', {
          method: 'GET',
          credentials: 'include',
        }); 
          
        if (!response.ok) {
          throw new Error('Response not ok');
        }
        return response.json();
      } catch (error) {
        console.error('There was a problem:', error);
        number_of_retries--; 
      }
    }
    navigate('/');
  };

  const handleRefresh = async () => {
    let number_of_retries = 2;

    while (number_of_retries > 0) {
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
              navigate('/');
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
    navigate('/');
  };

  const handleMarkRead = async (messageId, source) => {
    const messageData = { message_Id: messageId, source: source };
    let number_of_retries = 2;

    while (number_of_retries > 0) {
      try {
          const response = await fetch('http://127.0.0.1:5000/mark_as_read', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(messageData),
          });

          if (!response.ok) {
            throw new Error('Response not ok');
          }

          const data = await response.json();

          if (data.token_status === 'Logout') {
              navigate('/'); 
              return; 
          } else if (data.token_status === undefined) {
              navigate('/'); 
              return;
          } else if (data.token_status === 'Refresh') {
              await refreshTokens();
              number_of_retries--; 
          } else {
              handleRefresh(); 
              return; 
          }
      } catch (error) {
        console.error('There was a problem:', error);
        number_of_retries--;
      }
    }
    navigate('/');
  };

  const handleOpen = (threadId, webLink, source) => {
    let url = null;
    
    if (source === 'Google') {
      url = `https://mail.google.com/mail/u/0/#inbox/${threadId}`;
    }
    else if (source === 'Outlook') {
      url = webLink;
      console.log(url)
    }
    else if (source === 'Slack') {
      url = webLink;
      console.log(url)
    }

    if (url){
      window.open(url, '_blank')
    }
  };

  return (
    <div className="email-summary" onClick={toggleDetails}>
      <div className="email-header">  
        <div className="email-logo">
          <img src={getLogo(email)} alt={`${email.source} logo`} />
        </div>
        <div className="email-action"> 
          {email.source !== "Slack" && ( 
            <button onClick={(event) => { event.stopPropagation(); handleMarkRead(email.messageId, email.source);}}>
              Mark as Read 
            </button>
          )} 
          <button onClick={(event) => { event.stopPropagation(); handleOpen(email.threadId, email.webLink, email.source); }}>
            Open 
          </button>
          <div className="email-time">{timeOrDate}</div>
        </div>
      </div>
      <div className="email-content">
        <div>
          <div className="email-sender">{email.sender}</div>
          <div className="email-subject">{email.subject}</div>
        </div>
        {isExpanded && (
          <div className="email-details">
            <p>From: {email.sender_email}</p>
            <p>Date: {date} at {time}</p>
            <p>To: {email.receiver}</p>
            {email.html_body ? (
              <div dangerouslySetInnerHTML={createMessageHTML(email.html_body)}/>
            ) : (
              <p>{email.plain_body}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Email;
