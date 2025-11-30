import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faExclamationTriangle, faCalendarDay, faBell } from '@fortawesome/free-solid-svg-icons';

const Stats = ({ stats }) => {
  return (
    <div className="stats">
      <div className="stat-card">
        <div className="stat-icon danger">
          <FontAwesomeIcon icon={faExclamationTriangle} />
        </div>
        <div className="stat-number danger">{stats.total}</div>
        <div className="stat-label">Total Violations</div>
      </div>
      
      <div className="stat-card">
        <div className="stat-icon success">
          <FontAwesomeIcon icon={faCalendarDay} />
        </div>
        <div className="stat-number success">{stats.today}</div>
        <div className="stat-label">Today's Violations</div>
      </div>
      
      <div className="stat-card">
        <div className="stat-icon warning">
          <FontAwesomeIcon icon={faBell} />
        </div>
        <div className="stat-number warning">{stats.pending}</div>
        <div className="stat-label">Pending Notifications</div>
      </div>
    </div>
  );
};

export default Stats;