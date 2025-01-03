import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom'; 
import './Styles/index.css';
import App from './App';
import Dashboard from './Dashboard';
import CreateAccount from './CreateAccount';
import AccountRecovery from './AccountRecovery';
import RecoverAccount from './RecoverAccount';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  //<React.StrictMode>
     <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/createaccount" element={<CreateAccount />} />
        <Route path="/accountrecovery" element={<AccountRecovery />} />
        <Route path="/recoveraccount" element={<RecoverAccount />} />
      </Routes>
    </Router>
  //</React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
