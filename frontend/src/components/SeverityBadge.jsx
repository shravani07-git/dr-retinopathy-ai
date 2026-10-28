import React from 'react';

export default function SeverityBadge({ severity }) {
  return <span className={`severity severity-${severity?.toLowerCase().replaceAll(' ', '-')}`}>{severity}</span>;
}
