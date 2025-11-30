import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUsers, faUserPlus, faSave, faTimes, faSync, faTrash, faSignOutAlt, faTachometerAlt } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import ThreeBackground from './ThreeBackground';

const Employees = ({ onLogout, onNavigate }) => {
  const [employees, setEmployees] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    employee_id: '',
    name: '',
    department: '',
    position: ''
  });

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      const response = await axios.get('http://localhost:3001/api/employees');
      setEmployees(response.data.employees || []);
    } catch (error) {
      console.error('Error loading employees:', error);
    }
  };

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    
    if (!formData.employee_id || !formData.name || !formData.department || !formData.position) {
      alert('Please fill in all fields');
      return;
    }

    try {
      const response = await axios.post('http://localhost:3001/api/add_employee', formData);
      
      if (response.data.success) {
        setShowAddForm(false);
        setFormData({ employee_id: '', name: '', department: '', position: '' });
        loadEmployees();
        alert('Employee added successfully!');
      } else {
        alert('Failed to add employee: ' + response.data.error);
      }
    } catch (error) {
      alert('Error adding employee: ' + error.message);
    }
  };

  const handleDeleteEmployee = async (employeeId) => {
    if (!window.confirm(`Are you sure you want to delete employee ${employeeId}?`)) {
      return;
    }

    try {
      const response = await axios.post('http://localhost:3001/api/delete_employee', {
        employee_id: employeeId
      });
      
      if (response.data.success) {
        loadEmployees();
        alert('Employee deleted successfully!');
      } else {
        alert('Failed to delete employee: ' + response.data.error);
      }
    } catch (error) {
      alert('Error deleting employee: ' + error.message);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="employees">
      <ThreeBackground />
      
      <div className="container">
        <div className="header">
          <h1>
            <FontAwesomeIcon icon={faUsers} /> Employee Management
          </h1>
          <div className="header-actions">
            <button onClick={() => onNavigate('dashboard')} className="nav-btn">
              <FontAwesomeIcon icon={faTachometerAlt} /> Dashboard
            </button>
            <button onClick={onLogout} className="logout-btn">
              <FontAwesomeIcon icon={faSignOutAlt} /> Logout
            </button>
          </div>
        </div>

        <div className="alert-panel">
          <div className="panel-header">
            <h2>
              <FontAwesomeIcon icon={faUserPlus} /> Add New Employee
            </h2>
            <button 
              onClick={() => setShowAddForm(!showAddForm)} 
              className="action-btn success"
            >
              <FontAwesomeIcon icon={showAddForm ? faTimes : faUserPlus} />
              {showAddForm ? ' Cancel' : ' Add Employee'}
            </button>
          </div>
          
          {showAddForm && (
            <form onSubmit={handleAddEmployee} className="add-form">
              <div className="form-grid">
                <input
                  type="text"
                  name="employee_id"
                  placeholder="Employee ID"
                  value={formData.employee_id}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                />
                <input
                  type="text"
                  name="name"
                  placeholder="Full Name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                />
                <input
                  type="text"
                  name="department"
                  placeholder="Department"
                  value={formData.department}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                />
                <input
                  type="text"
                  name="position"
                  placeholder="Position"
                  value={formData.position}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="action-btn success">
                  <FontAwesomeIcon icon={faSave} /> Save Employee
                </button>
              </div>
            </form>
          )}
        </div>

        <div className="alert-panel">
          <div className="panel-header">
            <h2>
              <FontAwesomeIcon icon={faUsers} /> Employee List
            </h2>
            <button onClick={loadEmployees} className="action-btn primary">
              <FontAwesomeIcon icon={faSync} /> Refresh
            </button>
          </div>
          
          <div className="employee-list">
            {employees.length === 0 ? (
              <div className="no-employees">
                <FontAwesomeIcon 
                  icon={faUsers} 
                  style={{ fontSize: '3em', marginBottom: '15px', opacity: 0.3 }} 
                />
                <br />
                No employees added yet
              </div>
            ) : (
              employees.map((employee, index) => (
                <div key={index} className="employee-card">
                  <div className="employee-info">
                    <div className="employee-name">
                      <FontAwesomeIcon icon={faUsers} /> {employee.name} ({employee.employee_id})
                    </div>
                    <div className="employee-details">
                      <FontAwesomeIcon icon={faUsers} /> {employee.department} • {employee.position}
                    </div>
                  </div>
                  <button 
                    onClick={() => handleDeleteEmployee(employee.employee_id)}
                    className="action-btn danger"
                    style={{ padding: '8px 16px' }}
                  >
                    <FontAwesomeIcon icon={faTrash} /> Delete
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Employees;