import React, { useEffect, useMemo, useState } from 'react';
import './DailyTripChecklists.css';

const STORAGE_KEY = 'highwayPilot.dailyTripChecklists.v1';

const PRE_TRIP_ITEMS = [
  { id: 'lights', label: 'Lights and signals operational' },
  { id: 'tires', label: 'Tires and tread condition checked' },
  { id: 'brakes', label: 'Brakes and air system check complete' },
  { id: 'fluid', label: 'Oil, coolant, and washer fluid levels checked' },
  { id: 'documents', label: 'Insurance, registration, and permits onboard' },
  { id: 'load_secure', label: 'Load securement and trailer coupling verified' },
];

const POST_TRIP_ITEMS = [
  { id: 'damage', label: 'Vehicle damage inspection complete' },
  { id: 'fuel', label: 'Fuel level recorded' },
  { id: 'mileage', label: 'Odometer and trip mileage logged' },
  { id: 'cleanout', label: 'Cab and trailer cleanout complete' },
  { id: 'defects', label: 'Defects documented for maintenance follow-up' },
  { id: 'handoff', label: 'Keys, docs, and dispatch handoff complete' },
];

const todayIso = () => new Date().toISOString().slice(0, 10);

const buildChecklist = (items) => items.map((item) => ({ ...item, checked: false }));

const buildEmptyRecord = () => ({
  driverName: '',
  truckUnit: '',
  startOdometer: '',
  endOdometer: '',
  preTrip: buildChecklist(PRE_TRIP_ITEMS),
  postTrip: buildChecklist(POST_TRIP_ITEMS),
  preTripNotes: '',
  postTripNotes: '',
  updatedAt: new Date().toISOString(),
});

const DailyTripChecklists = () => {
  const [selectedDate, setSelectedDate] = useState(todayIso());
  const [records, setRecords] = useState({});

  useEffect(() => {
    try {
      const cached = window.localStorage.getItem(STORAGE_KEY);
      if (cached) {
        const parsed = JSON.parse(cached);
        if (parsed && typeof parsed === 'object') {
          setRecords(parsed);
        }
      }
    } catch (error) {
      console.error('Failed to load daily trip checklists:', error);
    }
  }, []);

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
    } catch (error) {
      console.error('Failed to persist daily trip checklists:', error);
    }
  }, [records]);

  const activeRecord = useMemo(() => {
    return records[selectedDate] || buildEmptyRecord();
  }, [records, selectedDate]);

  const updateActiveRecord = (patch) => {
    setRecords((current) => ({
      ...current,
      [selectedDate]: {
        ...(current[selectedDate] || buildEmptyRecord()),
        ...patch,
        updatedAt: new Date().toISOString(),
      },
    }));
  };

  const toggleItem = (section, itemId) => {
    const list = activeRecord[section] || [];
    const updated = list.map((item) => (
      item.id === itemId ? { ...item, checked: !item.checked } : item
    ));
    updateActiveRecord({ [section]: updated });
  };

  const preTripDone = (activeRecord.preTrip || []).every((item) => item.checked);
  const postTripDone = (activeRecord.postTrip || []).every((item) => item.checked);

  const recentDates = Object.keys(records)
    .sort((a, b) => b.localeCompare(a))
    .slice(0, 7);

  return (
    <div className="daily-trips">
      <div className="daily-trips-header">
        <h1>Daily Pre-Trip and Post-Trip</h1>
        <p className="subtitle">
          Complete and track daily safety checks for every unit before and after routes.
        </p>
      </div>

      <div className="trip-meta-grid">
        <label>
          Date
          <input
            type="date"
            value={selectedDate}
            onChange={(event) => setSelectedDate(event.target.value)}
          />
        </label>
        <label>
          Driver
          <input
            type="text"
            placeholder="Driver name"
            value={activeRecord.driverName}
            onChange={(event) => updateActiveRecord({ driverName: event.target.value })}
          />
        </label>
        <label>
          Truck Unit
          <input
            type="text"
            placeholder="Unit / trailer"
            value={activeRecord.truckUnit}
            onChange={(event) => updateActiveRecord({ truckUnit: event.target.value })}
          />
        </label>
        <label>
          Start Odometer
          <input
            type="number"
            placeholder="mi"
            value={activeRecord.startOdometer}
            onChange={(event) => updateActiveRecord({ startOdometer: event.target.value })}
          />
        </label>
        <label>
          End Odometer
          <input
            type="number"
            placeholder="mi"
            value={activeRecord.endOdometer}
            onChange={(event) => updateActiveRecord({ endOdometer: event.target.value })}
          />
        </label>
      </div>

      <div className="trip-checklists-grid">
        <section className="trip-card">
          <div className="trip-card-header">
            <h2>Pre-Trip Checklist</h2>
            <span className={preTripDone ? 'status-complete' : 'status-pending'}>
              {preTripDone ? 'Complete' : 'Pending'}
            </span>
          </div>
          <ul>
            {activeRecord.preTrip.map((item) => (
              <li key={item.id}>
                <label>
                  <input
                    type="checkbox"
                    checked={item.checked}
                    onChange={() => toggleItem('preTrip', item.id)}
                  />
                  {item.label}
                </label>
              </li>
            ))}
          </ul>
          <label className="notes-field">
            Notes
            <textarea
              rows={3}
              placeholder="Optional notes from pre-trip inspection"
              value={activeRecord.preTripNotes}
              onChange={(event) => updateActiveRecord({ preTripNotes: event.target.value })}
            />
          </label>
        </section>

        <section className="trip-card">
          <div className="trip-card-header">
            <h2>Post-Trip Checklist</h2>
            <span className={postTripDone ? 'status-complete' : 'status-pending'}>
              {postTripDone ? 'Complete' : 'Pending'}
            </span>
          </div>
          <ul>
            {activeRecord.postTrip.map((item) => (
              <li key={item.id}>
                <label>
                  <input
                    type="checkbox"
                    checked={item.checked}
                    onChange={() => toggleItem('postTrip', item.id)}
                  />
                  {item.label}
                </label>
              </li>
            ))}
          </ul>
          <label className="notes-field">
            Notes
            <textarea
              rows={3}
              placeholder="Maintenance notes and end-of-day observations"
              value={activeRecord.postTripNotes}
              onChange={(event) => updateActiveRecord({ postTripNotes: event.target.value })}
            />
          </label>
        </section>
      </div>

      <section className="trip-history">
        <h3>Recent Daily Logs</h3>
        {recentDates.length === 0 ? (
          <p className="placeholder">No saved daily trip logs yet.</p>
        ) : (
          <div className="history-list">
            {recentDates.map((date) => {
              const record = records[date];
              const preDone = (record.preTrip || []).every((item) => item.checked);
              const postDone = (record.postTrip || []).every((item) => item.checked);
              return (
                <div key={date} className="history-item">
                  <button type="button" onClick={() => setSelectedDate(date)}>{date}</button>
                  <span>{record.driverName || 'Driver not set'}</span>
                  <span>{record.truckUnit || 'Unit not set'}</span>
                  <span className={preDone && postDone ? 'status-complete' : 'status-pending'}>
                    {preDone && postDone ? 'Complete' : 'Open'}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
};

export default DailyTripChecklists;
