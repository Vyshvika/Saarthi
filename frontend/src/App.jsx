import { useEffect, useState, useCallback } from "react";
import Onboarding from "./components/Onboarding";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import { listSessions, createSession } from "./api";

export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem("saarthi_token"));
  const [userName, setUserName] = useState(localStorage.getItem("saarthi_name") || "");
  const [baseLevel, setBaseLevel] = useState(localStorage.getItem("saarthi_level") || "growth");
  const [sessions, setSessions] = useState([]);
  const [activeId, setActiveId] = useState(null);

  const refreshSessions = useCallback(async () => {
    const data = await listSessions();
    setSessions(data);
    if (data.length && !activeId) setActiveId(data[0].id);
  }, [activeId]);

  useEffect(() => {
    if (authed) refreshSessions();
  }, [authed, refreshSessions]);

  function handleAuthed(data) {
    setUserName(data.name);
    setBaseLevel(data.base_level);
    setAuthed(true);
  }

  async function handleNewChat() {
    const session = await createSession();
    setSessions((prev) => [session, ...prev]);
    setActiveId(session.id);
  }

  function handleLogout() {
    localStorage.clear();
    setAuthed(false);
    setSessions([]);
    setActiveId(null);
  }

  if (!authed) return <Onboarding onAuthed={handleAuthed} />;

  return (
    <div className="app-shell">
      <Sidebar
        sessions={sessions}
        activeId={activeId}
        onSelect={setActiveId}
        onNewChat={handleNewChat}
        onLogout={handleLogout}
        userName={userName}
      />
      {activeId ? (
        <ChatWindow sessionId={activeId} baseLevel={baseLevel} />
      ) : (
        <div className="chat-column">
          <div className="empty-state" style={{ height: "100%" }}>
            <h3>Start your first chat</h3>
            <p>Click "New chat" to begin.</p>
          </div>
        </div>
      )}
    </div>
  );
}
