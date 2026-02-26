import React from 'react';
import { Toaster } from 'react-hot-toast';

const index = () => (
  <Toaster
    position="top-right"
    reverseOrder={false}
    gutter={8}
    containerClassName=""
    containerStyle={{}}
    toastOptions={{
      className: '',
      duration: 4000,
      style: {
        background: '#363636',
        color: '#fff',
      },
      success: {
        style: {
          background: '#10b981',
        },
        iconTheme: {
          primary: '#fff',
          secondary: '#10b981',
        },
      },
      error: {
        style: {
          background: '#ef4444',
        },
        iconTheme: {
          primary: '#fff',
          secondary: '#ef4444',
        },
      },
    }}
  />
);

export default index;
