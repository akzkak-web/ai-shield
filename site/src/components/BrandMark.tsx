import { useId } from "react";

export function BrandMark({ size = 32 }: { size?: number }) {
  const uid = useId().replace(/:/g, "");
  const shield = `shield-${uid}`;
  const swoosh = `swoosh-${uid}`;

  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
      <defs>
        <linearGradient id={shield} x1="8" y1="6" x2="56" y2="58" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#2F8CF7" />
          <stop offset=".55" stopColor="#3E7BF6" />
          <stop offset="1" stopColor="#6A5AF9" />
        </linearGradient>
        <linearGradient id={swoosh} x1="8" y1="40" x2="56" y2="24" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#2F8CF7" />
          <stop offset="1" stopColor="#8B7CF6" />
        </linearGradient>
      </defs>
      <path
        d="M32 4.5 55 12.5v18.8c0 12.6-9.3 21.9-23 27.2C18.3 53.2 9 43.9 9 31.3V12.5L32 4.5Z"
        fill="#fff"
        stroke={`url(#${shield})`}
        strokeWidth="3.6"
        strokeLinejoin="round"
      />
      <ellipse
        cx="32"
        cy="35"
        rx="24.5"
        ry="8.2"
        transform="rotate(-17 32 35)"
        fill="none"
        stroke={`url(#${swoosh})`}
        strokeWidth="2.4"
        strokeLinecap="round"
        opacity=".9"
      />
      <path
        d="M20.5 46 32 21.5 43.5 46"
        fill="none"
        stroke={`url(#${shield})`}
        strokeWidth="7.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M32 33.5 33.9 39.2 39.6 41.1 33.9 43 32 48.7 30.1 43 24.4 41.1 30.1 39.2Z"
        fill="#6A5AF9"
      />
      <circle cx="9.4" cy="33.2" r="1.6" fill="#2F8CF7" />
      <circle cx="54.6" cy="24.8" r="1.6" fill="#8B7CF6" />
    </svg>
  );
}
