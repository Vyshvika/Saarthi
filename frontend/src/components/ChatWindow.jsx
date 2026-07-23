import { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble";
import CalibrationDial from "./CalibrationDial";
import { getMessages, getLevel, sendMessageStream } from "../api";

export default function ChatWindow({ sessionId, baseLevel, onMenuClick }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [level, setLevel] = useState(baseLevel);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;
    (async () => {
      const [msgs, lvl] = await Promise.all([getMessages(sessionId), getLevel(sessionId)]);
      setMessages(msgs);
      setLevel(lvl.effective_level);
    })();
  }, [sessionId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const text = input.trim();
    if (!text || sending || !sessionId) return;

    setInput("");
    setSending(true);
    setMessages((prev) => [...prev, { id: `tmp-user-${Date.now()}`, role: "user", content: text }]);

    const guideId = `tmp-guide-${Date.now()}`;
    setMessages((prev) => [...prev, { id: guideId, role: "guide", content: "", level_at_response: level }]);

    try {
      await sendMessageStream(sessionId, text, (chunk) => {
        setMessages((prev) =>
          prev.map((m) => (m.id === guideId ? { ...m, content: m.content + chunk } : m))
        );
      });
      const lvl = await getLevel(sessionId);
      setLevel(lvl.effective_level);
    } catch (e) {
      setMessages((prev) =>
        prev.map((m) => (m.id === guideId ? { ...m, content: "Something went wrong sending that. Try again." } : m))
      );
    } finally {
      setSending(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-column">
      <div className="chat-header">
        <button className="menu-btn" onClick={onMenuClick}>☰</button>
        <h2>Saarthi</h2>
        <CalibrationDial level={level} />
      </div>

      <div className="messages" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="empty-state">
            <h3>Ask anything to get started</h3>
            <p>Your guide is calibrated to your track and will keep adjusting as you talk.</p>
          </div>
        ) : (
          messages.map((m) => (
            <MessageBubble key={m.id} role={m.role} content={m.content} level={m.level_at_response} />
          ))
        )}
      </div>

      <div className="composer">
        <div className="composer-inner">
          <textarea
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask your question..."
          />
          <button className="send-btn" onClick={handleSend} disabled={sending || !input.trim()}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
