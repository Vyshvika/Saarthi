const LEVELS = ["foundation", "growth", "mastery"];
const COLORS = { foundation: "#e07a5f", growth: "#e3ac4d", mastery: "#38c9b4" };
const ANGLES = { foundation: -50, growth: 0, mastery: 50 };
const LABELS = { foundation: "Foundation", growth: "Growth", mastery: "Mastery" };

export default function CalibrationDial({ level = "growth", size = 34 }) {
  const angle = ANGLES[level] ?? 0;
  const color = COLORS[level] ?? COLORS.growth;

  return (
    <div className="dial-wrap" title={`Calibrated to ${LABELS[level]}`}>
      <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
        <path
          d="M6 28 A16 16 0 0 1 34 28"
          stroke="rgba(244,242,236,0.15)"
          strokeWidth="3"
          strokeLinecap="round"
        />
        {LEVELS.map((lvl) => (
          <circle
            key={lvl}
            cx={20 + 15 * Math.sin((ANGLES[lvl] * Math.PI) / 180)}
            cy={28 - 15 * Math.cos((ANGLES[lvl] * Math.PI) / 180)}
            r={lvl === level ? 2.6 : 1.6}
            fill={lvl === level ? COLORS[lvl] : "rgba(244,242,236,0.25)"}
          />
        ))}
        <g style={{ transition: "transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)", transformOrigin: "20px 28px" }}
           transform={`rotate(${angle})`}>
          <line x1="20" y1="28" x2="20" y2="14" stroke={color} strokeWidth="2.5" strokeLinecap="round" />
        </g>
        <circle cx="20" cy="28" r="2.5" fill={color} />
      </svg>
      <span className="dial-label" style={{ color }}>{LABELS[level]}</span>
    </div>
  );
}
