import React from 'react';
export default function Metric({label, value, hint}) {
  return <div className="metric"><div className="metric-label">{label}</div><div className="metric-value">{value}</div>{hint && <div className="metric-hint">{hint}</div>}</div>
}
