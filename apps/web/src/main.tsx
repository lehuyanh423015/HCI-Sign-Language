import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AccountProvider } from './app/Account';
import { App } from './app/App';
import './styles/global.css';
import './styles/learning.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <AccountProvider><App /></AccountProvider>
    </BrowserRouter>
  </StrictMode>,
);
