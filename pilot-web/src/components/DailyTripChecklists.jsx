import React, { useEffect, useMemo, useState } from 'react';
import './DailyTripChecklists.css';
import { API_BASE_URL } from '../lib/api';

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

const normalizeChecklist = (savedItems, defaults) => {
  const checkedMap = new Map((savedItems || []).map((item) => [item.id, !!item.checked]));
  return defaults.map((item) => ({ ...item, checked: checkedMap.get(item.id) || false }));
};

const fromApiRecord = (record) => ({
  driverName: record?.driver_name || '',
  truckUnit: record?.truck_unit || '',
  startOdometer: record?.start_odometer ?? '',
  endOdometer: record?.end_odometer ?? '',
  preTrip: normalizeChecklist(record?.pre_trip, PRE_TRIP_ITEMS),
  postTrip: normalizeChecklist(record?.post_trip, POST_TRIP_ITEMS),
  preTripNotes: record?.pre_trip_notes || '',
  postTripNotes: record?.post_trip_notes || '',
  updatedAt: record?.updated_at || new Date().toISOString(),
});

const toApiPayload = (record) => ({
  driver_name: record.driverName,
  truck_unit: record.truckUnit,
  start_odometer: record.startOdometer === '' ? null : Number(record.startOdometer),
  end_odometer: record.endOdometer === '' ? null : Number(record.endOdometer),
  pre_trip: record.preTrip,
  post_trip: record.postTrip,
  pre_trip_notes: record.preTripNotes,
  post_trip_notes: record.postTripNotes,
});

const DailyTripChecklists = () => {
  const [selectedDate, setSelectedDate] = useState(todayIso());
  const [records, setRecords] = useState({});
  const [loadingRecord, setLoadingRecord] = useState(false);
  const [saveStatus, setSaveStatus] = useState('Idle');
  const [loadError, setLoadError] = useState('');

  const fetchRecentRecords = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ops/daily-trips?limit=14`);
      if (!response.ok) {
        throw new Error('Recent records fetch failed');
      }

      const data = await response.json();
      const list = Array.isArray(data.records) ? data.records : [];

      setRecords((current) => {
        const merged = { ...current };
        list.forEach((row) => {
          merged[row.checklist_date] = fromApiRecord(row);
        });
        return merged;
      });
    } catch (error) {
      console.error('Failed to fetch recent daily trip records:', error);
    }
  };

  const fetchRecord = async (checklistDate) => {
    setLoadingRecord(true);
    setLoadError('');
    try {
      const response = await fetch(`${API_BASE_URL}/ops/daily-trips?checklist_date=${encodeURIComponent(checklistDate)}`);
      if (!response.ok) {
        throw new Error('Daily trip record fetch failed');
      }

      const data = await response.json();
      const nextRecord = data.record ? fromApiRecord(data.record) : buildEmptyRecord();

      setRecords((current) => ({
        ...current,
        [checklistDate]: nextRecord,
      }));
    } catch (error) {
      console.error('Failed to fetch daily trip record:', error);
      setLoadError('Unable to load this date from server. You can still enter details and save again.');
      setRecords((current) => ({
        ...current,
        [checklistDate]: current[checklistDate] || buildEmptyRecord(),
      }));
    } finally {
      setLoadingRecord(false);
    }
  };

  useEffect(() => {
    fetchRecentRecords();
  }, []);

  useEffect(() => {
    fetchRecord(selectedDate);
  }, [selectedDate]);

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

  const saveActiveRecord = async () => {
    const payload = toApiPayload(activeRecord);
    setSaveStatus('Saving...');
    try {
      const response = await fetch(`${API_BASE_URL}/ops/daily-trips/${encodeURIComponent(selectedDate)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Save failed');
      }

      const data = await response.json();
      if (data.record) {
        setRecords((current) => ({
          ...current,
          [selectedDate]: fromApiRecord(data.record),
        }));
      }

      setSaveStatus('Saved');
      fetchRecentRecords();
    } catch (error) {
      console.error('Failed to save daily trip record:', error);
      setSaveStatus('Save failed');
    }
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
        <div className="trip-actions">
          <button className="primary-button" type="button" onClick={saveActiveRecord} disabled={loadingRecord || saveStatus === 'Saving...'}>
            {saveStatus === 'Saving...' ? 'Saving...' : 'Save Daily Log'}
          </button>
          <span className="trip-save-status">{loadingRecord ? 'Loading...' : saveStatus}</span>
        </div>
        {loadError && <p className="trip-error">{loadError}</p>}
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
