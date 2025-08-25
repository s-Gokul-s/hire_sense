import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import LandingPage from './pages/LandingPage';
import ShortlisterPage from './pages/ShortlisterPage'
function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/shortlister" element={<ShortlisterPage />} />
    </Routes>
  );
}

export default App
