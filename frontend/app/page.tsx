'use client';
import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { Activity, Boxes, Network, ShieldCheck, Sparkles, Play, Server } from 'lucide-react';

const stages=[['01','Discover','Map target compute, network and storage'],['02','Validate','Run deterministic VCF preflight checks'],['03','Design','Generate a repeatable deployment specification'],['04','Deploy','Orchestrate VCF Installer through supported APIs']];
export default function Home(){
 const root=useRef<HTMLDivElement>(null); const [ready,setReady]=useState(false);
 useEffect(()=>{const ctx=gsap.context(()=>{gsap.from('.reveal',{y:24,opacity:0,duration:.9,stagger:.08,ease:'power3.out'});gsap.to('.orb',{scale:1.12,duration:4,yoyo:true,repeat:-1,ease:'sine.inOut'})},root);return()=>ctx.revert()},[]);
 async function check(){try{const r=await fetch('http://localhost:8000/health');setReady(r.ok)}catch{setReady(false)}}
 return <main ref={root}>
  <div className="orb a"/><div className="orb b"/>
  <nav className="reveal"><div className="brand"><Boxes/> VCF <b>STUDIO</b><span>0.1</span></div><div className="status"><i className={ready?'on':''}/>{ready?'CONTROL PLANE ONLINE':'LOCAL MODE'}</div></nav>
  <section className="hero">
   <div className="eyebrow reveal"><Sparkles size={15}/> INTELLIGENT PRIVATE CLOUD ENGINEERING</div>
   <h1 className="reveal">From nested ESXi<br/>to <em>VCF 9.</em> One flow.</h1>
   <p className="reveal">Design, validate and orchestrate repeatable VMware Cloud Foundation environments with an API-first control plane and a live deployment timeline.</p>
   <div className="actions reveal"><button onClick={check}><Play size={16}/> Initialize Lab</button><button className="ghost">Open Blueprint</button></div>
  </section>
  <section className="grid reveal">
   <div className="panel command"><header><Activity/> DEPLOYMENT COMMAND CENTER <span>PHASE 0</span></header><div className="topology"><Node icon={<Server/>} t="Physical ESXi"/><Line/><Node icon={<Network/>} t="Nested Fabric"/><Line/><Node icon={<Boxes/>} t="VCF Installer"/><Line/><Node icon={<ShieldCheck/>} t="Management Domain"/></div></div>
   <div className="panel score"><small>READINESS</small><strong>00</strong><span>/100</span><p>Connect the control plane and define your first lab blueprint.</p></div>
  </section>
  <section className="stages">{stages.map(s=><article className="reveal" key={s[0]}><span>{s[0]}</span><h3>{s[1]}</h3><p>{s[2]}</p></article>)}</section>
 </main>
}
function Node({icon,t}:{icon:React.ReactNode,t:string}){return <div className="node"><div>{icon}</div><span>{t}</span></div>}; function Line(){return <div className="line"><i/></div>}
