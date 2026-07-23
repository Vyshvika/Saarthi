import { useState } from "react";
import { signup, login } from "../api";

const LEVEL_OPTIONS = [
  {
    id: "foundation",
    title: "Foundation track",
    desc: "I'm still building the basics - explain everything from the ground up, step by step.",
  },
  {
    id: "growth",
    title: "Growth track",
    desc: "I know the fundamentals - give me structured, detailed explanations with examples.",
  },
  {
    id: "mastery",
    title: "Mastery track",
    desc: "I'm confident with this subject - keep it concise and get straight to the point.",
  },
];

export default function Onboarding({ onAuthed }) {
  const [mode, setMode] = useState("signup");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [level, setLevel] = useState("growth");
  const [subject, setSubject] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data =
        mode === "signup"
          ? await signup({ name, email, password, base_level: level, subject_focus: subject || null })
          : await login({ email, password });
      localStorage.setItem("saarthi_token", data.access_token);
      localStorage.setItem("saarthi_name", data.name);
      localStorage.setItem("saarthi_level", data.base_level);
      onAuthed(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="onboarding">
      <div className="onboarding-card">
        <div className="brand-mark">
          <svg width="30" height="30" viewBox="0 0 40 40" fill="none">
            <circle cx="20" cy="20" r="18" stroke="#e3ac4d" strokeWidth="2" />
            <path d="M20 8 L20 20 L28 26" stroke="#38c9b4" strokeWidth="2.5" strokeLinecap="round" />
          </svg>
          <span>Saarthi</span>
        </div>

        {mode === "signup" ? (
          <>
            <h1>Set up your guide</h1>
            <p className="subhead">
              Tell us where you're starting from. Your guide calibrates itself to match -
              and keeps adjusting as you talk, so you never have to ask twice.
            </p>
          </>
        ) : (
          <>
            <h1>Welcome back</h1>
            <p className="subhead">Sign in to pick up where you left off.</p>
          </>
        )}

        {error && <div className="error-banner">{error}</div>}

        <form onSubmit={handleSubmit}>
          {mode === "signup" && (
            <div className="field">
              <label>Name</label>
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" required />
            </div>
          )}

          <div className="field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 6 characters"
              minLength={6}
              required
            />
          </div>

          {mode === "signup" && (
            <>
              <div className="field">
                <label>What are you focusing on? (optional)</label>
                <input
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g. Data Structures, Operating Systems"
                />
              </div>

              <div className="field">
                <label>Where would you place yourself right now?</label>
                <div className="level-picker">
                  {LEVEL_OPTIONS.map((opt) => (
                    <button
                      type="button"
                      key={opt.id}
                      className={`level-option ${level === opt.id ? "selected" : ""}`}
                      onClick={() => setLevel(opt.id)}
                    >
                      <span className={`dot ${opt.id}`} />
                      <span>
                        <strong>{opt.title}</strong>
                        <p>{opt.desc}</p>
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? "Please wait..." : mode === "signup" ? "Start learning" : "Sign in"}
          </button>
        </form>

        <div className="switch-mode">
          {mode === "signup" ? (
            <>Already have an account? <button onClick={() => setMode("login")}>Sign in</button></>
          ) : (
            <>New here? <button onClick={() => setMode("signup")}>Create an account</button></>
          )}
        </div>
      </div>
    </div>
  );
}
