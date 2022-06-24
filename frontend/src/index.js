import React, {Suspense} from 'react';
import ReactDOM from 'react-dom/client';
import './css/style.css';
import App from './App';
import './i18n'
import RotateLoader from 'react-spinners/RotateLoader';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Suspense fallback={
      <div className="spinner">
        <RotateLoader color="#f8b119" size={20} />
    </div>
    }>
      <App />
    </Suspense>
  </React.StrictMode>
);