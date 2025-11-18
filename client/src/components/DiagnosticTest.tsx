import React from 'react';

export default function DiagnosticTest() {
  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#000',
      color: '#0ff',
      fontSize: '32px',
      fontFamily: 'monospace'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1>🌌 Aurora TSX Test</h1>
        <p>If you see this, React + TSX is working!</p>
        <p style={{ fontSize: '16px', marginTop: '20px' }}>
          66 Complete Systems • 13 Tasks • 41 Tiers
        </p>
      </div>
    </div>
  );
}
