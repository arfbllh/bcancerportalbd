// src/components/Heatmap/Heatmap.js
import React, { useState, useEffect } from "react";
import "./Heatmap.css";
import Plotly from "plotly.js-dist";
import { ApiService } from "../../services/heatmapapi";

const Heatmap = ({ datasetName = "brca_tcga_pub2015" }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [plotData, setPlotData] = useState(null);

  useEffect(() => {
    // Fetch heatmap data when component mounts
    fetchHeatmapData();
  }, []);

  const fetchHeatmapData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await ApiService.getHeatmapData("/api/datasets/heatmap");

      if (!response.ok) {
        throw new Error(
          `Server responded with ${response.status}: ${response.statusText}`
        );
      }

      const data = await response.json();
      setPlotData(JSON.parse(data));
    } catch (err) {
      console.error("Error fetching heatmap data:", err);
      setError(`Failed to load heatmap: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Render the plotly visualization when data is available
    if (plotData && !loading) {
      const plotElement = document.getElementById("heatmap-plot");

      // Make sure the element exists before attempting to render
      if (plotElement) {
        Plotly.newPlot(plotElement, plotData.data, plotData.layout, {
          responsive: true,
          toImageButtonOptions: {
            format: "png",
            filename: `heatmap_${datasetName}`,
            height: 800,
            width: 1200,
            scale: 1,
          },
        });

        // Clean up function to purge Plotly when component unmounts
        return () => {
          Plotly.purge(plotElement);
        };
      }
    }
  }, [plotData, loading, datasetName]);

  return (
    <div className="heatmap-container">
      <h2>Gene Expression Heatmap</h2>

      {loading && (
        <div className="loading-container">
          <div className="loader"></div>
          <p>Loading heatmap data...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <h3>Error Loading Heatmap</h3>
          <p>{error}</p>
          <button className="retry-btn" onClick={fetchHeatmapData}>
            Retry
          </button>
        </div>
      )}

      <div
        id="heatmap-plot"
        className="heatmap-plot"
        style={{
          display: loading || error ? "none" : "block",
          width: "100%",
          height: "800px",
        }}
      ></div>

      {!loading && !error && (
        <div className="heatmap-controls">
          <button
            className="download-btn"
            onClick={() => {
              const plotElement = document.getElementById("heatmap-plot");
              Plotly.downloadImage(plotElement, {
                format: "png",
                filename: `heatmap_${datasetName}`,
                height: 800,
                width: 1200,
                scale: 2,
              });
            }}
          >
            Download PNG
          </button>
        </div>
      )}
    </div>
  );
};

export default Heatmap;
