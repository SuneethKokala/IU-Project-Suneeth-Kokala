import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faShieldAlt, faUsers, faSignOutAlt, faExclamationTriangle, faTrash, faSyncAlt, faFileExcel } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import ThreeBackground from './ThreeBackground';
import ViolationHistory from './ViolationHistory';
import ImageUpload from './ImageUpload';
import Stats from './Stats';

const Dashboard = ({ onLogout, onNavigate }) => {
  const [violations, setViolations] = useState([]);
  const [stats, setStats] = useState({ total: 0, today: 0, pending: 0 });

  useEffect(() => {
    loadViolations();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const loadViolations = async () => {
    try {
      const response = await axios.get('http://localhost:3001/api/violations');
      setViolations(response.data.history || []);
      updateStats(response.data.history || []);
    } catch (error) {
      console.error('Error loading violations:', error);
    }
  };

  const updateStats = (history) => {
    const today = new Date().toDateString();
    const todayViolations = history.filter(v => 
      new Date(v.timestamp).toDateString() === today
    );
    const pendingNotifications = history.filter(v => !v.notified);
    
    setStats({
      total: history.length,
      today: todayViolations.length,
      pending: pendingNotifications.length
    });
  };

  const handleClearData = async () => {
    if (window.confirm('Are you sure you want to clear all violation data?')) {
      try {
        await axios.post('http://localhost:3001/api/clear_data');
        loadViolations();
      } catch (error) {
        alert('Failed to clear data');
      }
    }
  };

  const handleExportExcel = async () => {
    try {
      const response = await axios.get('http://localhost:3001/api/export_excel', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `PPE_Violations_Report_${new Date().toISOString().slice(0,10)}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('Failed to export Excel file');
    }
  };

  return (
    <div className="dashboard">
      <ThreeBackground />
      
      <div className="container">
        <div className="header">
          <h1>
            <FontAwesomeIcon icon={faShieldAlt} /> Safety Monitoring Dashboard
          </h1>
          <div className="header-actions">
            <button onClick={() => onNavigate('employees')} className="nav-btn">
              <FontAwesomeIcon icon={faUsers} /> Employees
            </button>
            <span className="supervisor-label">
              <FontAwesomeIcon icon={faUsers} /> Supervisor Panel
            </span>
            <button onClick={onLogout} className="logout-btn">
              <FontAwesomeIcon icon={faSignOutAlt} /> Logout
            </button>
          </div>
        </div>

        <Stats stats={stats} />
        
        <ImageUpload onViolationDetected={loadViolations} />
        
        <div className="alert-panel">
          <div className="panel-header">
            <h2>
              <FontAwesomeIcon icon={faExclamationTriangle} /> Violation History
            </h2>
            <div className="panel-actions">
              <button onClick={handleClearData} className="action-btn danger">
                <FontAwesomeIcon icon={faTrash} /> Clear Data
              </button>
              <button onClick={loadViolations} className="action-btn primary">
                <FontAwesomeIcon icon={faSyncAlt} /> Refresh
              </button>
              <button onClick={handleExportExcel} className="action-btn success">
                <FontAwesomeIcon icon={faFileExcel} /> Export Excel
              </button>
            </div>
          </div>
          
          <ViolationHistory 
            violations={violations} 
            onViolationUpdate={loadViolations} 
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;