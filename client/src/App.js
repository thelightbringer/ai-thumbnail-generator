import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [authUrl, setAuthUrl] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [selected, setSelected] = useState({});
  const [groupBy, setGroupBy] = useState('');
  const [groups, setGroups] = useState(null);

  useEffect(() => {
    axios.get('/auth-url').then(res => setAuthUrl(res.data.auth_url));
  }, []);

  const handleSearch = async () => {
    const res = await axios.post('/messages/search', { query });
    setMessages(res.data.messages);
    setSelected({});
    setGroups(null);
    setLoggedIn(true);
  };

  const handleAction = async (action) => {
    const ids = Object.keys(selected).filter(k => selected[k]);
    if (!ids.length) return;
    await axios.post(`/messages/${action}`, { ids });
    await handleSearch();
  };

  const handleGroup = async () => {
    const res = await axios.post('/messages/group', { query, group_by: groupBy });
    setGroups(res.data);
  };

  if (!loggedIn && authUrl) {
    return (
      <div className="container mt-5 text-center">
        <a className="btn btn-primary" href={authUrl}>Login with Google</a>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h3>Gmail Cleaner</h3>
      <div className="input-group mb-3">
        <input value={query} onChange={e => setQuery(e.target.value)} className="form-control" placeholder="Search query" />
        <button onClick={handleSearch} className="btn btn-secondary">Search</button>
      </div>
      {messages.length > 0 && (
        <div className="mb-2">
          <button onClick={() => handleAction('delete')} className="btn btn-danger me-2">Delete Selected</button>
          <button onClick={() => handleAction('archive')} className="btn btn-warning me-2">Archive Selected</button>
          <select value={groupBy} onChange={e => setGroupBy(e.target.value)} className="form-select w-auto d-inline me-2">
            <option value="">Group By</option>
            <option value="from">From</option>
            <option value="date">Date</option>
            <option value="subject">Subject</option>
          </select>
          <button onClick={handleGroup} className="btn btn-info">Group</button>
        </div>
      )}
      {groups ? (
        Object.entries(groups).map(([key, msgs]) => (
          <div key={key} className="mb-3">
            <h5>{key}</h5>
            <ul className="list-group">
              {msgs.map(m => (
                <li key={m.id} className="list-group-item">{m.subject} - {m.from} - {m.date}</li>
              ))
            </ul>
          </div>
        ))
      ) : (
        <ul className="list-group">
          {messages.map(m => (
            <li key={m.id} className="list-group-item">
              <input type="checkbox" className="form-check-input me-2" checked={!!selected[m.id]} onChange={e => setSelected({ ...selected, [m.id]: e.target.checked })} />
              {m.subject} - {m.from} - {m.date}
            </li>
          ))
        </ul>
      )}
    </div>
  );
}

export default App;

