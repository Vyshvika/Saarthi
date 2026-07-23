export default function Sidebar({ sessions, activeId, onSelect, onNewChat, onLogout, userName }) {
  return (
    <aside className="sidebar">
      <div className="brand-mark">
        <svg width="26" height="26" viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="18" stroke="#e3ac4d" strokeWidth="2" />
          <path d="M20 8 L20 20 L28 26" stroke="#38c9b4" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
        <span style={{ fontSize: 17 }}>Saarthi</span>
      </div>

      <button className="new-chat-btn" onClick={onNewChat}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
          <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
        New chat
      </button>

      <div className="session-list">
        {sessions.map((s) => (
          <button
            key={s.id}
            className={`session-item ${s.id === activeId ? "active" : ""}`}
            onClick={() => onSelect(s.id)}
          >
            {s.title}
          </button>
        ))}
      </div>

      <div className="sidebar-footer">
        <span>{userName}</span>
        <button onClick={onLogout}>Sign out</button>
      </div>
    </aside>
  );
}
