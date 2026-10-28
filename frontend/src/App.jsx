import React, { useEffect, useMemo, useState } from 'react';
import { UploadCloud, Eye, Activity, ShieldCheck, BrainCircuit, FileDown, Sun, Moon, CheckCircle2, AlertTriangle, RotateCcw, ScanLine, Stethoscope } from 'lucide-react';
import SeverityBadge from './components/SeverityBadge';
import Metric from './components/Metric';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const levels = ['No DR', 'Mild DR', 'Moderate DR', 'Severe DR', 'Proliferative DR'];

function App(){
  const [file,setFile]=useState(null);
  const [preview,setPreview]=useState('');
  const [result,setResult]=useState(null);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState('');
  const [theme,setTheme]=useState('dark');
  const [risk,setRisk]=useState({years:5,hba1c:7.0,hypertension:false,visionChange:false});

  useEffect(()=>{ document.documentElement.dataset.theme=theme; },[theme]);
  useEffect(()=>{ if(!file){setPreview(''); return;} const u=URL.createObjectURL(file); setPreview(u); return()=>URL.revokeObjectURL(u); },[file]);

  const riskScore=useMemo(()=>{
    let s=0; s += Math.min(30, Number(risk.years)*2); s += Math.max(0,(Number(risk.hba1c)-6)*10); if(risk.hypertension)s+=20; if(risk.visionChange)s+=25; return Math.min(100,Math.round(s));
  },[risk]);

  const analyze=async()=>{
    if(!file){setError('Please upload a retinal/fundus image first.'); return;}
    setError(''); setLoading(true); setResult(null);
    const body=new FormData(); body.append('file',file); body.append('years_with_diabetes',risk.years); body.append('hba1c',risk.hba1c); body.append('hypertension',risk.hypertension); body.append('vision_change',risk.visionChange);
    try{
      const r=await fetch(`${API}/analyze`,{method:'POST',body});
      const data=await r.json(); if(!r.ok) throw new Error(data.detail || 'Analysis failed');
      setResult(data);
    }catch(e){setError(e.message + ' — make sure the FastAPI backend is running on port 8000.');}
    finally{setLoading(false);}
  };

  const reset=()=>{setFile(null);setResult(null);setError('');};
  const download=()=>{
    if(!result)return;
    const text=`RetinaGuard AI - Screening Summary\n\nSeverity: ${result.severity}\nConfidence: ${Math.round(result.confidence*100)}%\nImage quality: ${result.quality.label} (${result.quality.score}/100)\nRisk questionnaire score: ${riskScore}/100\n\nRecommendation:\n${result.recommendation}\n\nImportant: This is a screening/education project and not a medical diagnosis.`;
    const blob=new Blob([text],{type:'text/plain'}); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='retinaguard-screening-summary.txt'; a.click(); URL.revokeObjectURL(a.href);
  };

  return <div className="app-shell">
    <header className="topbar">
      <div className="brand"><div className="brand-mark"><Eye size={22}/></div><div><b>RetinaGuard AI</b><span>Diabetic Retinopathy Screening</span></div></div>
      <button className="icon-btn" onClick={()=>setTheme(theme==='dark'?'light':'dark')} aria-label="toggle theme">{theme==='dark'?<Sun/>:<Moon/>}</button>
    </header>

    <main>
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow"><ShieldCheck size={16}/> AI-assisted retinal screening</div>
          <h1>Detect diabetic retinopathy severity from a fundus image.</h1>
          <p>Upload a retinal image, run image-quality checks, classify DR into five clinical severity levels, review explainability signals, and export a screening summary.</p>
          <div className="hero-pills"><span><BrainCircuit/>5-class AI pipeline</span><span><ScanLine/>Image quality gate</span><span><Activity/>Risk context</span></div>
        </div>
        <div className="hero-card">
          <div className="retina-orb"><div className="retina-ring"></div><div className="retina-disc"></div></div>
          <div><strong>Privacy first</strong><p>The starter backend processes uploads for analysis and does not persist them by default.</p></div>
        </div>
      </section>

      <section className="workspace-grid">
        <div className="panel upload-panel">
          <div className="panel-heading"><div><span className="step">01</span><h2>Upload fundus image</h2></div><button className="text-btn" onClick={reset}><RotateCcw size={16}/> Reset</button></div>
          <label className={`dropzone ${preview?'has-image':''}`}>
            {preview ? <img src={preview} alt="retinal preview"/> : <><UploadCloud size={42}/><strong>Drag & drop or choose an image</strong><span>JPG, JPEG or PNG • retinal/fundus image recommended</span></>}
            <input type="file" accept="image/png,image/jpeg" onChange={e=>setFile(e.target.files?.[0]||null)}/>
          </label>
          {file && <div className="file-row"><CheckCircle2 size={18}/><div><b>{file.name}</b><span>{(file.size/1024/1024).toFixed(2)} MB</span></div></div>}

          <div className="risk-box">
            <div className="section-title"><Activity size={18}/><div><b>Optional risk context</b><span>Used only as supporting context, not to alter the image diagnosis.</span></div></div>
            <div className="form-grid">
              <label>Years with diabetes<input type="number" min="0" max="60" value={risk.years} onChange={e=>setRisk({...risk,years:e.target.value})}/></label>
              <label>HbA1c (%)<input type="number" step="0.1" min="4" max="20" value={risk.hba1c} onChange={e=>setRisk({...risk,hba1c:e.target.value})}/></label>
              <label className="check"><input type="checkbox" checked={risk.hypertension} onChange={e=>setRisk({...risk,hypertension:e.target.checked})}/><span>Hypertension</span></label>
              <label className="check"><input type="checkbox" checked={risk.visionChange} onChange={e=>setRisk({...risk,visionChange:e.target.checked})}/><span>Recent vision change</span></label>
            </div>
            <div className="risk-meter"><div className="risk-track"><div style={{width:`${riskScore}%`}}/></div><span>Context score: {riskScore}/100</span></div>
          </div>
          <button className="primary-btn" onClick={analyze} disabled={!file||loading}>{loading?<><span className="spinner"/>Analyzing image…</>:<><BrainCircuit size={19}/>Analyze retina</>}</button>
          {error && <div className="error"><AlertTriangle size={18}/>{error}</div>}
        </div>

        <div className="panel results-panel">
          <div className="panel-heading"><div><span className="step">02</span><h2>AI screening result</h2></div>{result && <button className="text-btn" onClick={download}><FileDown size={16}/> Export</button>}</div>
          {!result ? <div className="empty-state"><div className="empty-icon"><Eye size={34}/></div><h3>Your result will appear here</h3><p>The system will display DR severity, confidence, image quality, lesion indicators, and a recommendation.</p></div> : <>
            <div className="result-hero">
              <div><span className="muted">Predicted severity</span><h3>{result.severity}</h3><SeverityBadge severity={result.severity}/></div>
              <div className="confidence"><span>{Math.round(result.confidence*100)}%</span><small>model confidence</small></div>
            </div>
            {result.is_demo && <div className="demo-banner"><AlertTriangle size={18}/><div><b>Demo model active</b><span>No trained DR weights were found. This output is a UI/backend simulation and is not clinically meaningful.</span></div></div>}
            <div className="metric-grid"><Metric label="Image quality" value={`${result.quality.score}/100`} hint={result.quality.label}/><Metric label="Brightness" value={result.quality.brightness}/><Metric label="Contrast" value={result.quality.contrast}/><Metric label="Context score" value={`${riskScore}/100`} hint="questionnaire only"/></div>
            <div className="severity-scale">{levels.map((x,i)=><div key={x} className={x===result.severity?'active':''}><span>{i}</span><small>{x.replace(' DR','')}</small></div>)}</div>
            <div className="lesion-card"><div className="section-title"><ScanLine size={18}/><div><b>Visual indicator summary</b><span>Model-side signals / demo proxies</span></div></div><div className="lesion-grid">{Object.entries(result.indicators).map(([k,v])=><div key={k}><span>{k.replaceAll('_',' ')}</span><b>{v}</b></div>)}</div></div>
            <div className="recommendation"><Stethoscope size={20}/><div><b>Recommendation</b><p>{result.recommendation}</p></div></div>
          </>}
        </div>
      </section>

      <section className="info-grid">
        <div className="panel"><span className="step">03</span><h2>What the AI looks for</h2><p className="sub">Typical DR signs include:</p><div className="signs"><span>🔴 Microaneurysms</span><span>🩸 Hemorrhages</span><span>🟡 Hard exudates</span><span>⚪ Cotton-wool spots</span><span>🧬 Abnormal vessels</span><span>🎯 Macular swelling clues</span></div></div>
        <div className="panel"><span className="step">04</span><h2>Unique functionality included</h2><div className="feature-list"><p><b>Image quality gate:</b> catches very dark, washed-out, low-contrast, or blurry uploads.</p><p><b>Explainability-ready architecture:</b> the backend is structured so a real Grad-CAM module can be added with trained CNN weights.</p><p><b>Risk-context layer:</b> keeps patient risk factors separate from image-model output to avoid misleading fusion.</p><p><b>Exportable summary:</b> creates a simple screening report for demos and project evaluation.</p></div></div>
      </section>

      <section className="disclaimer"><ShieldCheck size={18}/><p><b>Medical safety:</b> RetinaGuard AI is an educational/research project. It must not be used as a substitute for an ophthalmologist, retinal examination, or urgent medical care.</p></section>
    </main>
    <footer>RetinaGuard AI • React + FastAPI • Designed for academic demonstration</footer>
  </div>
}

export default App;
