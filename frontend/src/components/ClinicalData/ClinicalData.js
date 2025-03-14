// src/components/ClinicalData/ClinicalData.js
import React, { useState, useEffect } from 'react';
import { datasetService } from '../../services/api';
import { formatFieldLabel } from '../../utils/helpers';
import './ClinicalData.css';

const ClinicalData = ({ datasetId }) => {
  const [clinicalData, setClinicalData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filter state
  const [filters, setFilters] = useState({});
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  useEffect(() => {
    const fetchClinicalData = async () => {
      try {
        const data = await datasetService.getClinicalData(datasetId);
        setClinicalData(data);
        setFilteredData(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch clinical data');
        setLoading(false);
      }
    };

    fetchClinicalData();
  }, [datasetId]);
  
  useEffect(() => {
    // Apply filters whenever they change
    if (clinicalData.length > 0) {
      let result = [...clinicalData];
      
      // Apply each active filter
      Object.entries(filters).forEach(([field, value]) => {
        if (value) {
          result = result.filter(item => {
            // Case insensitive string includes for string fields
            if (typeof item[field] === 'string') {
              return item[field].toLowerCase().includes(value.toLowerCase());
            }
            // Exact match for numbers and other types
            else {
              return item[field] == value; // Using == for type coercion
            }
          });
        }
      });
      
      setFilteredData(result);
      setCurrentPage(1); // Reset to first page when filtering
    }
  }, [filters, clinicalData]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  const resetFilters = () => {
    setFilters({});
  };
  
  // Calculate pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredData.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  
  const paginate = (pageNumber) => setCurrentPage(pageNumber);
  
  const handleItemsPerPageChange = (e) => {
    setItemsPerPage(Number(e.target.value));
    setCurrentPage(1); // Reset to first page
  };

  if (loading) return <div className="loading">Loading clinical data...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!clinicalData || clinicalData.length === 0) return <div className="warning">No clinical data available</div>;

  // Define fixed headers matching ClinicalInfo component
  const fixedHeaders = [
    "Patient ID",
    "Age",
    "Gender",
    "Race",
    "Survival (months)",
    "Tumor Stage",
    "Status",
  ];

  // Map headers to corresponding data fields (adjust if your data has different field names)
  const fieldMapping = {
    "Patient ID": "patient_id",
    "Age": "age",
    "Gender": "gender",
    "Race": "race",
    "Tumor Stage": "stage",
    "Survival (months)": "survival_months",
    "Status": "status"
  };
  
  // Create filter fields for searchable columns
  const filterFields = Object.values(fieldMapping).filter(field => 
    field !== 'patient_id' && 
    field !== 'sample_id'
  );

  return (
    <div className="clinical-data-container">
      <h2>Clinical Data</h2>
      
      {/* Filter controls */}
      <div className="table-filters">
        {filterFields.map(field => (
          <div key={field} className="filter-group">
            <label className="filter-label" htmlFor={`filter-${field}`}>
              {formatFieldLabel(field)}
            </label>
            <input
              id={`filter-${field}`}
              type="text"
              className="filter-input"
              value={filters[field] || ''}
              onChange={(e) => handleFilterChange(field, e.target.value)}
              placeholder={`Filter by ${formatFieldLabel(field)}`}
            />
          </div>
        ))}
        
        <button className="reset-filters" onClick={resetFilters}>
          Reset Filters
        </button>
      </div>
      
      {/* Table */}
      <div className="table-responsive">
        <table className="clinical-table">
          <thead>
            <tr>
              {fixedHeaders.map(header => (
                <th key={header}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentItems.length > 0 ? (
              currentItems.map((patient, index) => (
                <tr key={index}>
                  {fixedHeaders.map(header => {
                    const field = fieldMapping[header];
                    return (
                      <td key={field}>
                        {header === "Status" ? (
                          <span
                            className={`status-badge ${
                              patient[field] === "Alive"
                                ? "status-alive"
                                : "status-deceased"
                            }`}
                          >
                            {patient[field]}
                          </span>
                        ) : (
                          patient[field]
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={fixedHeaders.length} className="no-data">
                  No matching data found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      {/* Pagination */}
      <div className="pagination">
        <div className="pagination-info">
          Showing {filteredData.length > 0 ? indexOfFirstItem + 1 : 0} to {Math.min(indexOfLastItem, filteredData.length)} of {filteredData.length} entries
        </div>
        
        <div className="items-per-page">
          <label>
            Show
            <select 
              value={itemsPerPage} 
              onChange={handleItemsPerPageChange}
              className="filter-input"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
            entries
          </label>
        </div>
        
        <div className="pagination-controls">
          <button
            className="pagination-button"
            onClick={() => paginate(1)}
            disabled={currentPage === 1}
          >
            First
          </button>
          <button
            className="pagination-button"
            onClick={() => paginate(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Prev
          </button>
          
          {/* Page numbers */}
          {[...Array(Math.min(totalPages, 5)).keys()].map(i => {
            let pageNum;
            if (totalPages <= 5) {
              pageNum = i + 1;
            } else if (currentPage <= 3) {
              pageNum = i + 1;
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i;
            } else {
              pageNum = currentPage - 2 + i;
            }
            
            return (
              <button
                key={pageNum}
                className={`pagination-button ${currentPage === pageNum ? 'active' : ''}`}
                onClick={() => paginate(pageNum)}
              >
                {pageNum}
              </button>
            );
          })}
          
          <button
            className="pagination-button"
            onClick={() => paginate(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
          <button
            className="pagination-button"
            onClick={() => paginate(totalPages)}
            disabled={currentPage === totalPages}
          >
            Last
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClinicalData;