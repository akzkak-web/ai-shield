export function BrandMark({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <defs>
        <linearGradient id="ai-mark" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#2E7CF6" />
          <stop offset="1" stopColor="#8B5CF6" />
        </linearGradient>
      </defs>
      <path
        d="M16 2.5 27 6.5v7.6c0 6.7-4.5 11.4-11 14.4C9.5 25.5 5 20.8 5 14.1V6.5L16 2.5z"
        fill="none"
        stroke="url(#ai-mark)"
        strokeWidth="2.4"
        strokeLinejoin="round"
      />
      <circle cx="16" cy="16" r="3.2" fill="#4E8DFF" />
      <path d="M16 5.8v4.4M16 21.8v4.4M5.8 16h4.4M21.8 16h4.4" stroke="#A78BFA" strokeWidth="1.6" />
      <circle cx="7.6" cy="8.8" r="1.4" fill="#C4B5FD" />
      <circle cx="24.4" cy="8.8" r="1.4" fill="#C4B5FD" />
      <circle cx="7.6" cy="23.2" r="1.4" fill="#C4B5FD" />
      <circle cx="24.4" cy="23.2" r="1.4" fill="#C4B5FD" />
    </svg>
  );
}
