import React, { useState, useEffect, useRef } from 'react';
import { datasetService } from '../../services/api';
import * as d3 from 'd3';
import Plotly from 'plotly.js-dist';
import './Summary.css';

const Summary = ({ datasetId }) => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // References for Plotly charts
  const pieChartRefs = useRef({});
  const barChartRefs = useRef({});
  const scatterPlotRef = useRef(null);
  const kmPlotRefs = useRef({});

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        const data = await datasetService.getSummaryStats(datasetId);
        setChartData(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch summary data');
        setLoading(false);
      }
    };

    fetchChartData();
  }, [datasetId]);

  useEffect(() => {
    if (chartData) {
      // Create charts when data is available
      createPieCharts();
      createBarCharts();
      createDotPlots();
      createTables(); // Still using D3 for tables
    }
  }, [chartData]);

  // Download chart data as CSV
  const downloadChartData = (id, data, type = 'pie') => {
    let csvContent = "data:text/csv;charset=utf-8,";
    
    if (type === 'pie') {
      // Header
      csvContent += "Category,Value\n";
      
      // Data rows
      data.forEach(item => {
        csvContent += `${item.category},${item.value}\n`;
      });
    } else if (type === 'bar') {
      // Header
      csvContent += "Range,Count\n";
      
      // Data rows
      data.forEach(item => {
        csvContent += `${item.range},${item.count}\n`;
      });
    } else if (type === 'scatter') {
      // Header
      csvContent += "Mutation Count,Fraction Genome Altered\n";
      
      // Data rows
      data.forEach(item => {
        csvContent += `${item.mutationCount},${item.fractionGenomeAltered}\n`;
      });
    } else if (type === 'km') {
      // Header
      csvContent += "Time,Survival,Censored\n";
      
      // Data rows
      data.forEach(item => {
        csvContent += `${item.time},${item.survival},${item.censored}\n`;
      });
    } else if (type === 'table') {
      // Header
      csvContent += data.columns.join(',') + '\n';
      
      // Data rows
      data.rows.forEach(row => {
        csvContent += data.columns.map(col => row[col]).join(',') + '\n';
      });
    }
    
    // Create download link
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${id}_data.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Create download button for charts
  const createDownloadButton = (container, id, data, type) => {
    const button = document.createElement("button");
    button.className = "download-btn";
    button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>';
    button.title = "Download data";
    button.onclick = () => downloadChartData(id, data, type);
    container.appendChild(button);
  };

  // Create pie charts using Plotly
  const createPieCharts = () => {
    const pieChartIds = [
      'samplesPerPatient',
      'overallSurvivalStatus',
      'sampleType',
      'sex',
      'ethnicityCategory',
      'raceCategory',
      'adjuvantTherapy',
      'ajccMetastasis',
      'ajccPublication',
      'ajccTumor'
    ];

    pieChartIds.forEach(id => {
      if (chartData[id] && pieChartRefs.current[id]) {
        const data = chartData[id];
        const container = pieChartRefs.current[id];
        
        const plotlyData = [{
          type: 'pie',
          values: data.map(d => d.value),
          labels: data.map(d => d.category),
          textinfo: 'percent',
          hoverinfo: 'label+percent+value',
          hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
          marker: {
            colors: d3.schemeCategory10
          },
          pull: 0.03,  // Add some separation between slices for interactivity
          textposition: 'inside'
        }];
        
        const layout = {
          margin: {t: 30, b: 30, l: 30, r: 30},
          height: 300,
          showlegend: true,
          legend: {
            orientation: 'h',
            xanchor: 'center',
            yanchor: 'bottom',
            x: 0.5,
            y: -0.15
          },
          title: {
            text: '',
            font: {
              size: 16
            }
          },
          annotations: [{
            text: `Total: ${data.reduce((sum, item) => sum + item.value, 0)}`,
            showarrow: false,
            x: 0.5,
            y: 0.5,
            font: {
              size: 14
            }
          }]
        };
        
        const config = {
          responsive: true,
          displayModeBar: true,
          modeBarButtonsToAdd: ['toImage'],
          modeBarButtonsToRemove: ['lasso2d', 'select2d'],
          displaylogo: false
        };
        
        Plotly.newPlot(container, plotlyData, layout, config);
        
        // Add download button
        createDownloadButton(container.parentNode, id, data, 'pie');
      }
    });
  };

  // Create bar charts using Plotly
  const createBarCharts = () => {
    const barChartIds = [
      'mutationCount',
      'fractionGenomicAltered',
      'birthFromDiagnosis',
      'daysToFollowup',
      'daysToCollection',
      'deathFromDiagnosis'
    ];

    barChartIds.forEach(id => {
      if (chartData[id] && barChartRefs.current[id]) {
        const data = chartData[id];
        const container = barChartRefs.current[id];
        
        const plotlyData = [{
          type: 'bar',
          x: data.map(d => d.range),
          y: data.map(d => d.count),
          marker: {
            color: '#4682B4',
            line: {
              width: 1,
              color: '#333'
            }
          },
          hovertemplate: '<b>Range: %{x}</b><br>Count: %{y}<extra></extra>',
          text: data.map(d => d.count),
          textposition: 'auto'
        }];
        
        const layout = {
          margin: {t: 30, b: 50, l: 50, r: 30},
          height: 300,
          xaxis: {
            title: {
              text: 'Range',
              font: {
                size: 12
              }
            },
            tickangle: -45
          },
          yaxis: {
            title: {
              text: 'Number of Samples',
              font: {
                size: 12
              }
            },
            gridcolor: '#eee'
          },
          bargap: 0.1,
          hovermode: 'closest'
        };
        
        const config = {
          responsive: true,
          displayModeBar: true,
          modeBarButtonsToAdd: ['toImage'],
          modeBarButtonsToRemove: ['lasso2d'],
          displaylogo: false
        };
        
        Plotly.newPlot(container, plotlyData, layout, config);
        
        // Add download button
        createDownloadButton(container.parentNode, id, data, 'bar');
      }
    });
  };

  // Create dot plots and scatter plots using Plotly
  const createDotPlots = () => {
    // Mutation Count vs Fraction Genome Altered (Scatter plot)
    if (chartData.mutationVsFraction && scatterPlotRef.current) {
      const data = chartData.mutationVsFraction;
      const container = scatterPlotRef.current;
      
      const plotlyData = [{
        type: 'scatter',
        mode: 'markers',
        x: data.map(d => d.fractionGenomeAltered),
        y: data.map(d => d.mutationCount),
        marker: {
          color: '#4682B4',
          size: 8,
          opacity: 0.7,
          line: {
            width: 1,
            color: '#333'
          }
        },
        hovertemplate: '<b>Fraction Genome Altered: %{x:.3f}</b><br>Mutation Count: %{y}<extra></extra>'
      }];
      
      // Add a trendline
      if (data.length > 1) {
        const xValues = data.map(d => d.fractionGenomeAltered);
        const yValues = data.map(d => d.mutationCount);
        
        // Calculate linear regression
        const n = xValues.length;
        const sumX = xValues.reduce((a, b) => a + b, 0);
        const sumY = yValues.reduce((a, b) => a + b, 0);
        const sumXY = xValues.reduce((a, b, i) => a + b * yValues[i], 0);
        const sumXX = xValues.reduce((a, b) => a + b * b, 0);
        
        const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;
        
        const xRange = [0, Math.max(...xValues) * 1.1];
        const yRange = xRange.map(x => slope * x + intercept);
        
        plotlyData.push({
          type: 'scatter',
          mode: 'lines',
          x: xRange,
          y: yRange,
          line: {
            color: '#FF7F50',
            width: 2,
            dash: 'dot'
          },
          hoverinfo: 'skip',
          showlegend: true,
          name: 'Trend Line'
        });
      }
      
      const layout = {
        margin: {t: 30, b: 50, l: 50, r: 30},
        height: 300,
        xaxis: {
          title: {
            text: 'Fraction Genome Altered',
            font: {
              size: 12
            }
          },
          zeroline: true,
          zerolinecolor: '#eee',
          gridcolor: '#eee'
        },
        yaxis: {
          title: {
            text: 'Mutation Count',
            font: {
              size: 12
            }
          },
          zeroline: true,
          zerolinecolor: '#eee',
          gridcolor: '#eee'
        },
        hovermode: 'closest'
      };
      
      const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToAdd: ['toImage'],
        displaylogo: false
      };
      
      Plotly.newPlot(container, plotlyData, layout, config);
      
      // Add download button
      createDownloadButton(container.parentNode, 'mutationVsFraction', data, 'scatter');
    }
    
    // KM Plots
    const kmPlotIds = ['kmOverall', 'kmDiseaseFree'];
    
    kmPlotIds.forEach(id => {
      if (chartData[id] && kmPlotRefs.current[id]) {
        const data = chartData[id];
        const container = kmPlotRefs.current[id];
        
        // Sort data by time to ensure proper line rendering
        const sortedData = [...data].sort((a, b) => a.time - b.time);
        
        // Line plot for survival curve
        const plotlyData = [{
          type: 'scatter',
          mode: 'lines',
          x: sortedData.map(d => d.time),
          y: sortedData.map(d => d.survival * 100),
          line: {
            color: '#4682B4',
            width: 2
          },
          name: 'Survival',
          hovertemplate: '<b>Time: %{x} months</b><br>Survival: %{y:.1f}%<extra></extra>'
        }];
        
        // Add confidence interval (if available) as shaded area
        // This is an example - would need actual CI data
        /*
        plotlyData.push({
          type: 'scatter',
          mode: 'lines',
          x: [...sortedData.map(d => d.time), ...sortedData.map(d => d.time).reverse()],
          y: [...sortedData.map(d => (d.survival + 0.1) * 100), ...sortedData.map(d => (d.survival - 0.1) * 100).reverse()],
          fill: 'toself',
          fillcolor: 'rgba(70, 130, 180, 0.2)',
          line: {width: 0},
          hoverinfo: 'skip',
          showlegend: false
        });
        */
        
        // Add censored points if available
        const censoredPoints = sortedData.filter(d => d.censored);
        if (censoredPoints.length > 0) {
          plotlyData.push({
            type: 'scatter',
            mode: 'markers',
            x: censoredPoints.map(d => d.time),
            y: censoredPoints.map(d => d.survival * 100),
            marker: {
              color: '#fff',
              size: 8,
              symbol: 'circle',
              line: {
                color: '#4682B4',
                width: 2
              }
            },
            name: 'Censored',
            hovertemplate: '<b>Time: %{x} months</b><br>Status: Censored<br>Survival: %{y:.1f}%<extra></extra>'
          });
        }
        
        const layout = {
          margin: {t: 30, b: 50, l: 50, r: 30},
          height: 300,
          xaxis: {
            title: {
              text: 'Time (months)',
              font: {
                size: 12
              }
            },
            zeroline: true,
            zerolinecolor: '#eee',
            gridcolor: '#eee'
          },
          yaxis: {
            title: {
              text: '% Event-free',
              font: {
                size: 12
              }
            },
            range: [0, 100],
            zeroline: true,
            zerolinecolor: '#eee',
            gridcolor: '#eee'
          },
          hovermode: 'closest',
          legend: {
            x: 0.01,
            y: 0.01,
            orientation: 'h',
            bgcolor: 'rgba(255,255,255,0.7)'
          }
        };
        
        const config = {
          responsive: true,
          displayModeBar: true,
          modeBarButtonsToAdd: ['toImage'],
          displaylogo: false
        };
        
        Plotly.newPlot(container, plotlyData, layout, config);
        
        // Add download button
        createDownloadButton(container.parentNode, id, data, 'km');
      }
    });
  };

  // Create tables using D3 (with download button)
  const createTables = () => {
    const tableIds = [
      'genomicProfile',
      'cancerTypeDetailed',
      'mutatedGenes',
      'cnaGenes',
      'brachytherapy',
      'cent17CopyNumber'
    ];

    tableIds.forEach(id => {
      if (chartData[id]) {
        createTable(id, chartData[id]);
      }
    });
  };

  const createTable = (id, data) => {
    const containerElement = document.getElementById(id);
    if (!containerElement || !data || !data.columns || !data.rows) return;
    
    const container = d3.select(`#${id}`);
    container.selectAll("*").remove();

    // Create table container
    const tableContainer = container.append("div")
      .attr("class", "table-responsive");

    // Create download button
    createDownloadButton(containerElement, id, data, 'table');

    // Create table
    const table = tableContainer.append("table")
      .attr("class", "data-table");

    // Create header
    const thead = table.append("thead");
    thead.append("tr")
      .selectAll("th")
      .data(data.columns)
      .enter()
      .append("th")
      .text(d => d)
      .on("click", function(event, d) {
        // Sort table by column
        const isNumeric = (str) => {
          return !isNaN(str) && !isNaN(parseFloat(str));
        };
        
        const sortRows = () => {
          const rows = tbody.selectAll("tr").data().sort((a, b) => {
            // Check if we're dealing with numeric values
            if (isNumeric(a[d]) && isNumeric(b[d])) {
              return parseFloat(b[d]) - parseFloat(a[d]);
            }
            // Otherwise sort alphabetically
            return a[d].localeCompare(b[d]);
          });
          
          // If already sorted in descending order, reverse it
          if (this.dataset.sorted === "desc") {
            rows.reverse();
            this.dataset.sorted = "asc";
          } else {
            this.dataset.sorted = "desc";
          }
          
          // Update the DOM
          tbody.selectAll("tr").data(rows)
            .selectAll("td")
            .data(row => data.columns.map(column => row[column]))
            .text(d => d);
        };
        
        sortRows();
      })
      .style("cursor", "pointer")
      .append("span")
      .attr("class", "sort-icon")
      .html(" &#x25BC;");

    // Create body with interactive rows
    const tbody = table.append("tbody");
    const rows = tbody.selectAll("tr")
      .data(data.rows)
      .enter()
      .append("tr");
      
    // Add row hover effect
    rows.on("mouseover", function() {
      d3.select(this).classed("highlight", true);
    }).on("mouseout", function() {
      d3.select(this).classed("highlight", false);
    });
    
    // Add cells with tooltips for long content
    rows.selectAll("td")
      .data(row => data.columns.map(column => row[column]))
      .enter()
      .append("td")
      .text(d => d)
      .attr("title", d => d); // Add tooltip
  };
  
  // Function to create refs for Plotly charts
  const createRef = (id, refObject) => {
    return (element) => {
      if (element) {
        refObject[id] = element;
      }
    };
  };

  if (loading) return <div className="loading">Loading summary...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!chartData) return <div className="warning">No summary data available</div>;

  return (
    <div className="summary-container">
      <h2>Dataset Summary</h2>
      
      <h3>Pie Charts</h3>
      <div className="chart-grid">
        <div className="chart-card">
          <h4>Number of Samples Per Patient</h4>
          <div ref={createRef('samplesPerPatient', pieChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Overall Survival Status</h4>
          <div ref={createRef('overallSurvivalStatus', pieChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Sample Type</h4>
          <div ref={createRef('sampleType', pieChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Sex</h4>
          <div ref={createRef('sex', pieChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Ethnicity Category</h4>
          <div ref={createRef('ethnicityCategory', pieChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Race Category</h4>
          <div ref={createRef('raceCategory', pieChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Adjuvant Postoperative Pharmaceutical Therapy</h4>
          <div ref={createRef('adjuvantTherapy', pieChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>American Joint Committee on Cancer Metastasis</h4>
          <div ref={createRef('ajccMetastasis', pieChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>American Joint Committee on Cancer Publication</h4>
          <div ref={createRef('ajccPublication', pieChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>American Joint Committee on Cancer Tumor</h4>
          <div ref={createRef('ajccTumor', pieChartRefs.current)} className="chart-container"></div>
        </div>
      </div>

      <h3>Tables</h3>
      <div className="table-grid">
        <div className="table-card">
          <h4>Genomic Profile Sample Counts</h4>
          <div id="genomicProfile" className="table-container"></div>
        </div>
        
        <div className="table-card">
          <h4>Cancer Type Detailed</h4>
          <div id="cancerTypeDetailed" className="table-container"></div>
        </div>
        
        <div className="table-card">
          <h4>Mutated Genes</h4>
          <div id="mutatedGenes" className="table-container"></div>
        </div>
        
        <div className="table-card">
          <h4>CNA Genes</h4>
          <div id="cnaGenes" className="table-container"></div>
        </div>
        
        <div className="table-card">
          <h4>Brachytherapy First Reference Point Administered Total Dose</h4>
          <div id="brachytherapy" className="table-container"></div>
        </div>
        
        <div className="table-card">
          <h4>Cent17 Copy Number</h4>
          <div id="cent17CopyNumber" className="table-container"></div>
        </div>
      </div>

      <h3>Bar Charts</h3>
      <div className="chart-grid">
        <div className="chart-card">
          <h4>Mutation Count</h4>
          <div ref={createRef('mutationCount', barChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Fraction Genomic Altered</h4>
          <div ref={createRef('fractionGenomicAltered', barChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Birth from Initial Pathologic Diagnosis Date</h4>
          <div ref={createRef('birthFromDiagnosis', barChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Days to Last Follow-up</h4>
          <div ref={createRef('daysToFollowup', barChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Days to Sample Collection</h4>
          <div ref={createRef('daysToCollection', barChartRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>Death from Initial Pathologic Diagnosis Date</h4>
          <div ref={createRef('deathFromDiagnosis', barChartRefs.current)} className="chart-container"></div>
        </div>
      </div>

      <h3>Dot Plots</h3>
      <div className="chart-grid">
        <div className="chart-card">
          <h4>Mutation Count vs Fraction Genome Altered</h4>
          <div ref={el => scatterPlotRef.current = el} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>KM Plot: Overall (months)</h4>
          <div ref={createRef('kmOverall', kmPlotRefs.current)} className="chart-container"></div>
        </div>
        
        <div className="chart-card">
          <h4>KM Plot: Disease Free (months)</h4>
          <div ref={createRef('kmDiseaseFree', kmPlotRefs.current)} className="chart-container"></div>
        </div>
      </div>
    </div>
  );
};

export default Summary;