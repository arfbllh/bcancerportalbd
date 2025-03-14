// src/components/Home/Home.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { datasetService } from '../../services/api';
import './Home.css';

const Home = () => {
  const [groupedDatasets, setGroupedDatasets] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        const data = await datasetService.getAllDatasets();
        setGroupedDatasets(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch datasets');
        setLoading(false);
      }
    };

    fetchDatasets();
  }, []);

  if (loading) return <div className="loading">Loading datasets...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="home-container">
      <h1>Available Datasets</h1>
      
      <div className="datasets-card">
        {Object.entries(groupedDatasets).map(([type, datasets]) => (
          <div key={type} className="dataset-section">
            <h2>{type}</h2>
            <ul className="dataset-list">
              {datasets.map(dataset => (
                <li key={dataset.id} className="dataset-item">
                  <Link to={`/datasets/${dataset.id}`} className="dataset-link">
                    <div className="dataset-name">{dataset.name}</div>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Home;