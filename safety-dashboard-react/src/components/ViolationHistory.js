import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faHardHat, faClock, faCheck, faCheckCircle } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';

const ViolationHistory = ({ violations, onViolationUpdate }) => {
  const markAsNotified = async (violationTimestamp, event) => {
    try {
      const response = await axios.post('http://localhost:3001/api/mark_notified', {
        violation_id: violationTimestamp
      });

      if (response.data.success) {
        event.target.disabled = true;
        event.target.checked = true;
        event.target.nextElementSibling.textContent = 'Notified';
        
        if (onViolationUpdate) {
          onViolationUpdate();
        }
      } else {
        alert('Failed to mark as notified: ' + response.data.error);
        event.target.checked = false;
      }
    } catch (error) {
      alert('Error marking as notified: ' + error.message);
      event.target.checked = false;
    }
  };

  if (violations.length === 0) {
    return (
      <div className="no-violations">
        <FontAwesomeIcon 
          icon={faCheckCircle} 
          style={{ fontSize: '3em', color: '#28a745', marginBottom: '15px' }} 
        />
        <br />
        No violations recorded
      </div>
    );
  }

  return (
    <div className="history">
      {violations.map((violation, index) => {
        const isNotified = violation.notified || false;
        const notifiedAt = violation.notified_at ? new Date(violation.notified_at).toLocaleString() : '';
        
        return (
          <div key={index} className={`violation ${isNotified ? 'notified' : ''}`}>
            <div className="violation-content">
              <div className="violation-info">
                <div className="employee-name">
                  <FontAwesomeIcon icon={faUser} /> {violation.employee_name} ({violation.employee_id})
                </div>
                <div className="missing-ppe">
                  <FontAwesomeIcon icon={faHardHat} /> Missing: {violation.missing_ppe.join(', ')}
                </div>
                <div className="timestamp">
                  <FontAwesomeIcon icon={faClock} /> {new Date(violation.timestamp).toLocaleString()}
                </div>
                {isNotified && (
                  <div className="notified-info">
                    <FontAwesomeIcon icon={faCheck} /> Notified at: {notifiedAt}
                  </div>
                )}
              </div>
              
              <div className="checkbox-container">
                <input
                  type="checkbox"
                  checked={isNotified}
                  disabled={isNotified}
                  onChange={(e) => markAsNotified(violation.timestamp, e)}
                />
                <span className="checkbox-label">
                  {isNotified ? 'Notified' : 'Mark as Notified'}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ViolationHistory;