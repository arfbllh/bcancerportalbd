// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home/Home';
import DatasetDetail from './components/DatasetDetail/DatasetDetail';
import Navbar from './components/Navbar/Navbar';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <div className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/datasets/:datasetId" element={<DatasetDetail />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;