export default function MessageBubble({ role, content, level }) {
  return (
    <div className={`msg-row ${role}`}>
      <div>
        {role === "guide" && level && <span className="level-tag">{level}</span>}
        <div className="msg-bubble">{content}</div>
      </div>
    </div>
  );
}
