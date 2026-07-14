/* MedEasy Frontend — All UI Logic — v2.0 (Fixed) */
const API = async (url, opts = {}) => {
  const userTokenRaw = localStorage.getItem('medeasy_token') || localStorage.getItem('token') || null;
  let token = null;
  try { token = userTokenRaw ? JSON.parse(userTokenRaw) : null; } catch(e){ token = userTokenRaw; }
  console.debug('[API] token:', token);

  const providedHeaders = Object.assign({}, opts.headers || {});
  // If body is FormData, do not set Content-Type (browser will set multipart boundary)
  if (!(opts.body instanceof FormData) && !providedHeaders['Content-Type']) {
    providedHeaders['Content-Type'] = 'application/json';
  }
  if (token) providedHeaders['Authorization'] = providedHeaders['Authorization'] || `Bearer ${token}`;

  const fetchOpts = Object.assign({}, opts, {
    headers: providedHeaders,
    // Always include credentials (cookies) so Flask session cookies are sent
    credentials: opts.credentials || 'include'
  });

  const r = await fetch(url, fetchOpts);
  return r.json();
};

// ── STATE ─────────────────────────────────────────────────────
let currentUser = null, reportCtx = null, chatOpen = false;
let allHistory = [];
const STEPS = [
  "Tokenizing report text...","Running Named Entity Recognition...",
  "Extracting lab values...","Classifying report type (Naive Bayes)...",
  "Comparing against normal ranges...","Generating plain language summary...",
  "Building your health dashboard..."
];

// ── LOCAL STORAGE HELPERS ─────────────────────────────────────
const LS = {
  get(key) {
    try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : null; } catch(e) { return null; }
  },
  set(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); return true; } catch(e) { return false; }
  },
  remove(key) { try { localStorage.removeItem(key); } catch(e) {} },
  getGuestHistory() { return this.get('medeasy_guest_history') || []; },
  saveGuestReport(result) {
    const hist = this.getGuestHistory();
    const entry = {
      id: 'g_' + Date.now(),
      uploaded_at: new Date().toISOString(),
      report_type: result.report_type || 'Unknown',
      patient_name: result.patient?.name || 'Unknown',
      overall_status: result.status_key || 'Fair',
      total_tests: result.total_tests || 0,
      normal_count: result.normal_count || 0,
      abnormal_count: result.abnormal_count || 0,
      language: result.language || 'English',
      result: result
    };
    hist.unshift(entry);
    this.set('medeasy_guest_history', hist.slice(0, 30));
    return entry.id;
  },
  deleteGuestReport(id) {
    const hist = this.getGuestHistory().filter(r => r.id !== id);
    this.set('medeasy_guest_history', hist);
  },
  saveLanguage(lang) { this.set('medeasy_lang', lang); },
  getLanguage() { return this.get('medeasy_lang') || 'English'; }
};

// ── INIT ──────────────────────────────────────────────────────
window.addEventListener('load', async () => {
  const ta = document.getElementById('reportTxt');
  const abtn = document.getElementById('analyzeBtn');
  if(ta) ta.addEventListener('input', () => { abtn.disabled = ta.value.trim().length < 10; });

  const fi = document.getElementById('fi');
  if(fi) fi.addEventListener('change', e => processFile(e.target.files[0]));

  const dz = document.getElementById('dz');
  if(dz){
    dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('drag'); });
    dz.addEventListener('dragleave', () => dz.classList.remove('drag'));
    dz.addEventListener('drop', e => { e.preventDefault(); dz.classList.remove('drag'); processFile(e.dataTransfer.files[0]); });
  }

  const langSel = document.getElementById('langSel');
  if(langSel) {
    const saved = LS.getLanguage();
    if(saved) langSel.value = saved;
    langSel.addEventListener('change', () => {
      LS.saveLanguage(langSel.value);
      if(document.getElementById('dashSec')?.style.display !== 'none' && reportCtx){
        document.getElementById('dashSec').style.display = 'none';
        doAnalyze();
      }
    });
  }

  hideLangSel();

  try {
    const me = await API('/api/auth/me');
    if(me.id){ currentUser = me; onLoginOk(false); }
    else { showPage('login'); }
  } catch(e){ showPage('login'); }
});

function hideLangSel() {
  const ls = document.getElementById('langSelWrap');
  if(ls) ls.style.display = 'none';
}
function showLangSel() {
  const ls = document.getElementById('langSelWrap');
  if(ls) ls.style.display = 'flex';
}

// ── PAGE NAVIGATION ───────────────────────────────────────────
function showPage(name){
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const pg = document.getElementById(name + 'Page');
  if(pg){ pg.classList.add('active'); window.scrollTo({top:0,behavior:'smooth'}); }
  if(name === 'profile') loadProfile();
  if(name === 'history') loadHistory();
}
function goHome(){ showPage(currentUser ? 'home' : 'login'); }
function goSignup(){ showPage('signup'); }

// ── AUTH ──────────────────────────────────────────────────────
async function doLogin(){
  const email = document.getElementById('liEmail').value.trim();
  const pwd   = document.getElementById('liPwd').value;
  const btn   = document.getElementById('liBtn');
  document.getElementById('liErr').style.display = 'none';
  if(!email||!pwd){ showAuthErr('liErr','Please fill in all fields.'); return; }
  btn.disabled=true; btn.textContent='Signing in...';
  const r = await API('/api/auth/login',{method:'POST',body:JSON.stringify({email,password:pwd})});
  btn.disabled=false; btn.textContent='Sign In';
  if(r.error){ showAuthErr('liErr',r.error); document.getElementById('liEmail').classList.add('err'); setTimeout(()=>document.getElementById('liEmail').classList.remove('err'),600); return; }
  currentUser = r; onLoginOk(true);
}

async function doSignup(){
  const name=document.getElementById('suName').value.trim(), email=document.getElementById('suEmail').value.trim();
  const pwd=document.getElementById('suPwd').value, pwd2=document.getElementById('suPwd2').value;
  const btn=document.getElementById('suBtn');
  document.getElementById('suErr').style.display='none'; document.getElementById('suOk').style.display='none';
  if(!name||!email||!pwd){ showAuthErr('suErr','Please fill in all fields.'); return; }
  if(pwd.length<6){ showAuthErr('suErr','Password must be at least 6 characters.'); return; }
  if(pwd!==pwd2){ showAuthErr('suErr','Passwords do not match.'); document.getElementById('suPwd2').classList.add('err'); setTimeout(()=>document.getElementById('suPwd2').classList.remove('err'),600); return; }
  btn.disabled=true; btn.textContent='Creating...';
  const r = await API('/api/auth/signup',{method:'POST',body:JSON.stringify({name,email,password:pwd})});
  btn.disabled=false; btn.textContent='Create Account';
  if(r.error){ showAuthErr('suErr',r.error); return; }
  currentUser=r;
  const ok=document.getElementById('suOk'); ok.textContent='Account created! Redirecting...'; ok.style.display='block';
  setTimeout(()=>onLoginOk(true),1100);
}

async function doGuest(){
  currentUser={id:'guest',name:'Guest User',email:'guest@medeasy',isGuest:true};
  onLoginOk(true);
}

function onLoginOk(anim){
  updateNav();
  showLangSel();
  const gh=document.getElementById('guestHint');
  if(gh) gh.style.display=currentUser?.isGuest?'block':'none';
  showPage('home');
  if(anim) showToast('Welcome, '+currentUser.name.split(' ')[0]+'!','ok');
}

async function doLogout(){
  if(!currentUser?.isGuest) await API('/api/auth/logout',{method:'POST'});
  currentUser=null; reportCtx=null;
  document.getElementById('navUser').style.display='none';
  document.getElementById('navAuthBtns').style.display='flex';
  document.getElementById('navBadge').style.display='inline-flex';
  hideLangSel();
  showPage('login'); showToast('Signed out','info');
}

function updateNav(){
  if(!currentUser) return;
  document.getElementById('navAuthBtns').style.display='none';
  document.getElementById('navBadge').style.display='none';
  document.getElementById('navUser').style.display='flex';
  const ini=currentUser.name.split(' ').map(n=>n[0]).join('').toUpperCase().slice(0,2);
  document.getElementById('navAv').textContent=ini;
  document.getElementById('navUname').textContent=currentUser.name.split(' ')[0];
}

function showAuthErr(id,msg){ const e=document.getElementById(id); e.textContent=msg; e.style.display='block'; }
function togglePwd(inputId,btn){ const i=document.getElementById(inputId); i.type=i.type==='password'?'text':'password'; btn.textContent=i.type==='password'?'👁':'🙈'; }
function chkPwd(pwd){
  const bar=document.getElementById('pwdBar'),lbl=document.getElementById('pwdLbl'); if(!bar)return;
  let s=0; if(pwd.length>=6)s++; if(pwd.length>=10)s++; if(/[A-Z]/.test(pwd))s++; if(/[0-9]/.test(pwd))s++; if(/[^A-Za-z0-9]/.test(pwd))s++;
  const c=[{w:'0%',c:'transparent',t:''},{w:'25%',c:'var(--red)',t:'Weak'},{w:'50%',c:'var(--ylw)',t:'Fair'},{w:'75%',c:'var(--org)',t:'Good'},{w:'90%',c:'var(--grn)',t:'Strong'},{w:'100%',c:'#34d399',t:'Very Strong'}][Math.min(s,5)];
  bar.style.width=c.w; bar.style.background=c.c; lbl.textContent=c.t; lbl.style.color=c.c;
}

// ── PROFILE ───────────────────────────────────────────────────
async function loadProfile(){
  if(!currentUser) return;
  const ini=currentUser.name.split(' ').map(n=>n[0]).join('').toUpperCase().slice(0,2);
  document.getElementById('pAv').textContent=ini;
  document.getElementById('pName').textContent=currentUser.name;
  document.getElementById('pEmail').textContent=currentUser.email;
  document.getElementById('pEditName').value=currentUser.name;
  document.getElementById('pEditEmail').value=currentUser.email;
  document.getElementById('pLang').textContent=document.getElementById('langSel').value.slice(0,2).toUpperCase();
  if(currentUser.isGuest){
    const gHist = LS.getGuestHistory();
    document.getElementById('pReports').textContent=gHist.length;
    document.getElementById('pAbnormal').textContent=gHist.reduce((a,r)=>a+(r.abnormal_count||0),0);
    document.getElementById('pJoined').textContent='Guest';
    return;
  }
  const me = await API('/api/auth/me');
  document.getElementById('pReports').textContent=me.total||0;
  document.getElementById('pAbnormal').textContent=me.total_abnormal||0;
  document.getElementById('pJoined').textContent=me.created_at?new Date(me.created_at).getFullYear():'—';
}
async function saveProfile(){
  const name=document.getElementById('pEditName').value.trim(), email=document.getElementById('pEditEmail').value.trim();
  if(!name||!email){showToast('Please fill in all fields','err');return;}
  if(!currentUser.isGuest) await API('/api/auth/profile',{method:'PUT',body:JSON.stringify({name,email})});
  currentUser.name=name; currentUser.email=email; updateNav(); loadProfile();
  showToast('Profile updated!','ok');
}
async function changePwd(){
  const p1=document.getElementById('pPwd1').value, p2=document.getElementById('pPwd2').value;
  if(!p1||!p2){showToast('Fill in both fields','err');return;}
  if(p1.length<6){showToast('Min 6 characters','err');return;}
  if(p1!==p2){showToast('Passwords do not match','err');return;}
  if(!currentUser.isGuest) await API('/api/auth/password',{method:'PUT',body:JSON.stringify({password:p1})});
  document.getElementById('pPwd1').value=''; document.getElementById('pPwd2').value='';
  showToast('Password updated 🔒','ok');
}
async function deleteAccount(){
  if(!confirm('Delete your account and all saved reports? This cannot be undone.')) return;
  if(!currentUser.isGuest) await API('/api/auth/account',{method:'DELETE'});
  else LS.remove('medeasy_guest_history');
  doLogout();
}

// ── FILE PROCESSING ───────────────────────────────────────────
const SAMPLES = {
  diabetes:"Patient: Ramesh Kumar  Age: 48  M\nHbA1c           : 8.4 %\nFasting Glucose : 178 mg/dL\nPPBS            : 265 mg/dL\nCreatinine      : 1.3 mg/dL\nTotal Cholesterol: 228 mg/dL\nTriglycerides   : 230 mg/dL\nHDL             : 38 mg/dL\nLDL             : 145 mg/dL\nHemoglobin      : 11.2 g/dL\nVitamin D       : 16 ng/mL",
  cbc:"Patient: Anjali Singh  Age: 28  F\nHemoglobin      : 9.6 g/dL\nWBC             : 13.8 x10/uL\nPlatelets       : 195 x10/uL\nHematocrit      : 31 %\nMCV             : 72 fL\nFerritin        : 6 ng/mL\nVitamin B12     : 158 pg/mL",
  lipid:"Patient: Suresh Patil  Age: 55  M\nTotal Cholesterol: 262 mg/dL\nHDL             : 35 mg/dL\nLDL             : 180 mg/dL\nTriglycerides   : 295 mg/dL\nFasting Glucose : 112 mg/dL\nALT             : 44 U/L",
  full:"Patient: Priya Mehta  Age: 42  F\nHemoglobin      : 10.8 g/dL\nWBC             : 11.5 x10/uL\nHbA1c           : 6.9 %\nFasting Glucose : 118 mg/dL\nTotal Cholesterol: 215 mg/dL\nHDL             : 42 mg/dL\nLDL             : 138 mg/dL\nTriglycerides   : 185 mg/dL\nCreatinine      : 0.9 mg/dL\nALT             : 45 U/L\nTSH             : 5.8 mIU/L\nVitamin D       : 14 ng/mL\nFerritin        : 8 ng/mL"
};

function loadSample(k){ document.getElementById('reportTxt').value=SAMPLES[k]; document.getElementById('analyzeBtn').disabled=false; document.getElementById('reportTxt').focus(); }

async function processFile(file){
  if(!file) return;
  const ext=file.name.split('.').pop().toLowerCase();
  document.getElementById('fileTag').textContent='📄 '+file.name;
  document.getElementById('fileTag').style.display='inline-flex';
  showMsg('info','⏳ Extracting text from '+file.name+'...');
  document.getElementById('analyzeBtn').disabled=true;
  document.getElementById('reportTxt').value='';
  document.getElementById('reportTxt').placeholder='Extracting...';
  try {
    let text='';
    if(ext==='pdf'){
      const buf=await file.arrayBuffer();
      if(typeof pdfjsLib!=='undefined'){
        const pdf=await pdfjsLib.getDocument({data:buf}).promise;
        const pages=[];
        for(let i=1;i<=pdf.numPages;i++){const pg=await pdf.getPage(i);const c=await pg.getTextContent();pages.push(c.items.map(x=>x.str).join(' '));}
        text=pages.join('\n');
      } else {
        const fd=new FormData(); fd.append('file',file); fd.append('language',document.getElementById('langSel').value);
        const r=await fetch('/api/analyze',{method:'POST',body:fd});
        const d=await r.json();
        if(d.error){throw new Error(d.error);}
        renderDash(d); resetForm(); return;
      }
    } else if(ext==='docx'||ext==='doc'){
      const buf=await file.arrayBuffer();
      if(typeof mammoth!=='undefined'){const res=await mammoth.extractRawText({arrayBuffer:buf});text=res.value;}
      else { throw new Error('DOCX support not available in browser.'); }
    } else if(ext==='rtf'){
      text=(await file.text()).replace(/\\[a-z]+[-]?\d*[ ]?/gi,' ').replace(/[{}\\]/g,' ').replace(/\s+/g,' ').trim();
    } else if(ext==='csv'){
      text=(await file.text()).split('\n').map(l=>{const c=l.split(',').map(x=>x.trim()).filter(Boolean);return c.length>=2?c[0]+' : '+c[1]+(c[2]?' '+c[2]:''):l;}).join('\n');
    } else {
      text=await file.text();
    }
    text=text.trim();
    if(text.length<5) throw new Error('Could not extract text. Please paste it manually.');
    document.getElementById('reportTxt').value=text; document.getElementById('reportTxt').placeholder='';
    document.getElementById('analyzeBtn').disabled=false;
    showMsg('ok','✓ Text extracted ('+text.length+' chars). Click Analyze!');
    setTimeout(()=>{document.getElementById('extractMsg').style.display='none';},4000);
  } catch(e){
    showMsg('err','❌ '+e.message);
    document.getElementById('reportTxt').placeholder='Could not extract. Please paste the text manually.';
    document.getElementById('analyzeBtn').disabled=true;
  }
}

function showMsg(type,msg){
  const el=document.getElementById('extractMsg');
  const s={info:{bg:'rgba(56,189,248,.08)',bdr:'rgba(56,189,248,.2)',col:'var(--acc)'},ok:{bg:'rgba(52,211,153,.08)',bdr:'rgba(52,211,153,.2)',col:'var(--grn)'},err:{bg:'rgba(248,113,113,.08)',bdr:'rgba(248,113,113,.3)',col:'var(--red)'}};
  const st=s[type]||s.info;
  el.style.display='block'; el.style.background=st.bg; el.style.borderColor=st.bdr; el.style.color=st.col; el.textContent=msg;
}

// ── ANALYZE ───────────────────────────────────────────────────
async function doAnalyze(){
  const ta=document.getElementById('reportTxt'); const text=ta.value.trim(); if(!text) return;
  const lang=document.getElementById('langSel').value;
  document.getElementById('heroSec').style.display='none';
  document.getElementById('dashSec').style.display='none';
  document.getElementById('loadSec').style.display='block';
  let si=0; const stepEl=document.getElementById('loadStep');
  const timer=setInterval(()=>{if(si<STEPS.length-1){stepEl.style.opacity=0;setTimeout(()=>{stepEl.textContent=STEPS[++si];stepEl.style.opacity=1;},180);}},400);
  try {
    const r=await API('/api/analyze',{method:'POST',body:JSON.stringify({text,language:lang})});
    clearInterval(timer);
    if(r.error){ throw new Error(r.error); }
    r.rawText=text.slice(0,2000); reportCtx=r;
    renderDash(r);
    if(currentUser && !currentUser.isGuest){
      document.getElementById('saveRptBtn').style.display='inline-flex';
      autoSaveReport(r, text);
    } else if(currentUser && currentUser.isGuest){
      LS.saveGuestReport(r);
      showToast('Report saved to local history 💾','info');
    }
  } catch(e){
    clearInterval(timer);
    document.getElementById('loadSec').style.display='none';
    document.getElementById('heroSec').style.display='block';
    showMsg('err','Analysis error: '+e.message);
    document.getElementById('analyzeBtn').disabled=false;
  }
}

async function autoSaveReport(result, text){
  try {
    const r = await API('/api/report/save',{method:'POST',body:JSON.stringify({result,raw_text:text.slice(0,2000)})});
    if(r.id){ document.getElementById('saveRptBtn').style.display='none'; showToast('Report saved to history! 💾','ok'); }
  } catch(e) { /* manual save still available */ }
}

// ── RENDER DASHBOARD ──────────────────────────────────────────
function renderDash(r){
  document.getElementById('loadSec').style.display='none';
  document.getElementById('dashSec').style.display='block';
  window.scrollTo({top:0,behavior:'smooth'});
  const SC={Good:'var(--grn)',Fair:'var(--ylw)',Attention:'var(--org)',Critical:'var(--red)'};
  const sc=SC[r.status_key]||'var(--ylw)';
  const em={Good:'🟢',Fair:'🟡',Attention:'🟠',Critical:'🔴'}[r.status_key]||'⚪';
  const p=r.patient||{};
  document.getElementById('metaRow').innerHTML=
    '<span class="meta-tag" style="color:'+sc+'">'+em+' '+(r.status_label||r.status_key)+'</span>'+
    '<span class="meta-tag">'+r.report_type.split(' - ')[0]+'</span>'+
    '<span class="meta-tag">'+r.language+'</span>'+
    (p.name&&p.name!=='Unknown'?'<span class="meta-tag">👤 '+p.name+'</span>':'')+
    (p.age&&p.age!=='Unknown'?'<span class="meta-tag">Age '+p.age+'</span>':'')+
    '<span class="meta-tag">'+Math.round((r.report_confidence||0)*100)+'% match</span>';
  document.getElementById('sumRow').innerHTML=
    '<div class="sum-card"><div class="s-lbl">Overall</div><div class="s-val" style="color:'+sc+';font-size:.88rem">'+em+' '+(r.status_label||r.status_key)+'</div><div class="s-sub">'+r.report_type.split(' - ')[0]+'</div></div>'+
    '<div class="sum-card"><div class="s-lbl">Tests</div><div class="s-val" style="color:var(--acc)">'+r.total_tests+'</div><div class="s-sub">parameters</div></div>'+
    '<div class="sum-card"><div class="s-lbl">Normal</div><div class="s-val" style="color:var(--grn)">'+r.normal_count+'</div><div class="s-sub">within range ✓</div></div>'+
    '<div class="sum-card"><div class="s-lbl">Attention</div><div class="s-val" style="color:'+(r.abnormal_count>0?'var(--red)':'var(--grn)')+'">'+(r.abnormal_count)+'</div><div class="s-sub">'+(r.abnormal_count>0?'out of range ⚠':'all good ✓')+'</div></div>';
  document.getElementById('urgentBanner').innerHTML=r.urgent_flags&&r.urgent_flags.length?'<div class="urgent-banner">⚠️ <strong>URGENT:</strong> '+r.urgent_flags.join('<br>')+'</div>':'';
  document.getElementById('explainTxt').innerHTML='<p style="font-size:.93rem;line-height:1.9">'+r.explanation+'</p>';

  renderDiseaseDetection(r);
  renderBloodTestCards(r);
  renderSuggestions(r);
  renderDoctorSection(r);
  renderFullSummary(r);

  const cc=document.getElementById('condCard');
  const conds=p.conditions||[];
  if(conds.length){cc.style.display='block';document.getElementById('condContent').innerHTML=conds.map(c=>'<span class="cpill">'+c+'</span>').join('');}else cc.style.display='none';
}

// ── DISEASE DETECTION ─────────────────────────────────────────
function renderDiseaseDetection(r){
  const lang=r.language||'English';
  const detected=detectConditions(r.lab_values||[],lang);
  const el=document.getElementById('diseaseDetect');
  if(!el) return;
  if(!detected.length){el.style.display='none';return;}
  el.style.display='block';
  const TITLE={English:'🔬 Detected Health Conditions',Hindi:'🔬 पहचानी गई स्वास्थ्य स्थितियां',Marathi:'🔬 आरोग्य स्थिती',Bengali:'🔬 শনাক্ত স্বাস্থ্য সমস্যা',Tamil:'🔬 கண்டறியப்பட்ட நோய்கள்',Telugu:'🔬 గుర్తించిన ఆరోగ్య సమస్యలు'};
  const titleEl=document.getElementById('diseaseDetectTitle');
  if(titleEl) titleEl.textContent=TITLE[lang]||TITLE.English;
  const contentEl=document.getElementById('diseaseDetectContent');
  if(contentEl) contentEl.innerHTML=detected.map(d=>'<div class="disease-card"><div class="disease-icon">'+d.icon+'</div><div class="disease-body"><div class="disease-name">'+d.name+'</div><div class="disease-evidence">'+d.evidence+'</div>'+(d.severity?'<div class="disease-sev disease-sev-'+d.severity+'">'+d.sevLabel+'</div>':'')+'</div></div>').join('');
}

function detectConditions(vals,lang){
  const conditions=[];
  const L={
    English:{diabetes:'Diabetes / Pre-Diabetes',anemia:'Anemia',high_chol:'High Cholesterol (Hyperlipidemia)',thyroid:'Thyroid Dysfunction',kidney:'Kidney Function Alert',liver:'Liver Function Alert',vitamin_d:'Vitamin D Deficiency',vitamin_b12:'Vitamin B12 Deficiency',infection:'Possible Infection / Inflammation',mild:'Mild',moderate:'Moderate',severe:'Severe'},
    Hindi:{diabetes:'मधुमेह / प्री-डायबिटीज',anemia:'एनीमिया',high_chol:'उच्च कोलेस्ट्रॉल',thyroid:'थायरॉइड विकार',kidney:'किडनी फंक्शन अलर्ट',liver:'लिवर फंक्शन अलर्ट',vitamin_d:'विटामिन D की कमी',vitamin_b12:'विटामिन B12 की कमी',infection:'संभावित संक्रमण',mild:'हल्का',moderate:'मध्यम',severe:'गंभीर'},
    Marathi:{diabetes:'मधुमेह / प्री-डायबिटीज',anemia:'अ‍ॅनिमिया',high_chol:'उच्च कोलेस्टेरॉल',thyroid:'थायरॉईड विकार',kidney:'किडनी अलर्ट',liver:'यकृत अलर्ट',vitamin_d:'व्हिटॅमिन D कमतरता',vitamin_b12:'व्हिटॅमिन B12 कमतरता',infection:'संसर्ग शक्यता',mild:'सौम्य',moderate:'मध्यम',severe:'गंभीर'},
    Bengali:{diabetes:'ডায়াবেটিস',anemia:'রক্তশূন্যতা',high_chol:'উচ্চ কোলেস্টেরল',thyroid:'থাইরয়েড সমস্যা',kidney:'কিডনি সতর্কতা',liver:'লিভার সতর্কতা',vitamin_d:'ভিটামিন D ঘাটতি',vitamin_b12:'ভিটামিন B12 ঘাটতি',infection:'সংক্রমণের সম্ভাবনা',mild:'হালকা',moderate:'মধ্যম',severe:'গুরুতর'},
    Tamil:{diabetes:'நீரிழிவு',anemia:'இரத்த சோகை',high_chol:'உயர் கொழுப்பு',thyroid:'தைராய்டு கோளாறு',kidney:'சிறுநீரக எச்சரிக்கை',liver:'கல்லீரல் எச்சரிக்கை',vitamin_d:'வைட்டமின் D குறைபாடு',vitamin_b12:'வைட்டமின் B12 குறைபாடு',infection:'நோய்த்தொற்று அபாயம்',mild:'மென்மையான',moderate:'மிதமான',severe:'தீவிரமான'},
    Telugu:{diabetes:'మధుమేహం',anemia:'రక్తహీనత',high_chol:'అధిక కొలెస్ట్రాల్',thyroid:'థైరాయిడ్ సమస్య',kidney:'కిడ్నీ హెచ్చరిక',liver:'లివర్ హెచ్చరిక',vitamin_d:'విటమిన్ D లోపం',vitamin_b12:'విటమిన్ B12 లోపం',infection:'సంక్రమణ అవకాశం',mild:'మెల్లగా',moderate:'మధ్యస్థం',severe:'తీవ్రంగా'}
  };
  const lbl=L[lang]||L.English;

  const hba1c=vals.find(v=>v.name==='HbA1c');
  const glucose=vals.find(v=>v.name.toLowerCase().includes('glucose')||v.name.toLowerCase().includes('sugar'));
  if(hba1c&&hba1c.status!=='Normal'){const n=parseFloat(hba1c.numeric_value);const sev=n>8?'severe':n>6.5?'moderate':'mild';conditions.push({icon:'🩸',name:lbl.diabetes,evidence:hba1c.name+': '+hba1c.value+' ('+hba1c.normal_range+')',severity:sev,sevLabel:lbl[sev]});}
  else if(glucose&&glucose.status!=='Normal'){conditions.push({icon:'🩸',name:lbl.diabetes,evidence:glucose.name+': '+glucose.value,severity:'mild',sevLabel:lbl.mild});}

  const hb=vals.find(v=>v.name==='Hemoglobin');
  if(hb&&['Low','Critical Low'].includes(hb.status)){const n=parseFloat(hb.numeric_value);const sev=n<7?'severe':n<10?'moderate':'mild';conditions.push({icon:'💉',name:lbl.anemia,evidence:'Hemoglobin: '+hb.value+' ('+hb.normal_range+')',severity:sev,sevLabel:lbl[sev]});}

  const chol=vals.find(v=>v.name.toLowerCase().includes('cholesterol'));
  const ldl=vals.find(v=>v.name==='LDL Cholesterol');
  const trig=vals.find(v=>v.name==='Triglycerides');
  if([chol,ldl,trig].some(v=>v&&v.status!=='Normal'&&v.status!=='Low')){conditions.push({icon:'🫀',name:lbl.high_chol,evidence:[chol,ldl,trig].filter(v=>v&&v.status!=='Normal').map(v=>v.name+': '+v.value).join(', '),severity:'moderate',sevLabel:lbl.moderate});}

  const tsh=vals.find(v=>v.name==='TSH');
  if(tsh&&tsh.status!=='Normal'){conditions.push({icon:'🦋',name:lbl.thyroid,evidence:'TSH: '+tsh.value,severity:'moderate',sevLabel:lbl.moderate});}

  const creat=vals.find(v=>v.name==='Creatinine');
  if(creat&&creat.status!=='Normal'){conditions.push({icon:'🫘',name:lbl.kidney,evidence:'Creatinine: '+creat.value,severity:'moderate',sevLabel:lbl.moderate});}

  const alt=vals.find(v=>v.name==='ALT');
  const ast=vals.find(v=>v.name==='AST');
  if([alt,ast].some(v=>v&&v.status!=='Normal')){conditions.push({icon:'🟤',name:lbl.liver,evidence:[alt,ast].filter(v=>v&&v.status!=='Normal').map(v=>v.name+': '+v.value).join(', '),severity:'mild',sevLabel:lbl.mild});}

  const vitD=vals.find(v=>v.name.toLowerCase().includes('vitamin d'));
  if(vitD&&['Low','Critical Low'].includes(vitD.status)){conditions.push({icon:'☀️',name:lbl.vitamin_d,evidence:vitD.name+': '+vitD.value,severity:'mild',sevLabel:lbl.mild});}

  const vitB12=vals.find(v=>v.name.toLowerCase().includes('b12'));
  if(vitB12&&['Low','Critical Low'].includes(vitB12.status)){conditions.push({icon:'🧠',name:lbl.vitamin_b12,evidence:vitB12.name+': '+vitB12.value,severity:'mild',sevLabel:lbl.mild});}

  const wbc=vals.find(v=>v.name==='WBC');
  if(wbc&&['High','Critical High'].includes(wbc.status)){conditions.push({icon:'🦠',name:lbl.infection,evidence:'WBC: '+wbc.value,severity:'moderate',sevLabel:lbl.moderate});}

  return conditions;
}

// ── BLOOD TEST CARDS ──────────────────────────────────────────
function renderBloodTestCards(r){
  const vals=r.lab_values||[];
  const wrap=document.getElementById('testCardsWrap');
  if(!wrap) return;
  if(!vals.length){wrap.style.display='none';return;}
  wrap.style.display='block';

  const categories={
    cbc:{label:'🔴 Complete Blood Count',tests:[],kw:['Hemoglobin','WBC','RBC','Platelets','Hematocrit','MCV','MCH','MCHC','RDW','Neutrophil','Lymphocyte','Monocyte','Eosinophil','Basophil','Ferritin']},
    diabetes:{label:'🩸 Diabetes / Blood Sugar',tests:[],kw:['HbA1c','Glucose','Sugar','PPBS','Insulin','Prediab']},
    lipid:{label:'🫀 Lipid Profile',tests:[],kw:['Cholesterol','HDL','LDL','Triglyceride','VLDL','Lipoprotein']},
    liver:{label:'🟤 Liver Function',tests:[],kw:['ALT','AST','Bilirubin','Albumin','ALP','GGT','Protein','SGPT','SGOT']},
    kidney:{label:'🫘 Kidney / Electrolytes',tests:[],kw:['Creatinine','BUN','Urea','Uric Acid','eGFR','Potassium','Sodium','Calcium','Chloride']},
    thyroid:{label:'🦋 Thyroid',tests:[],kw:['TSH','T3','T4','Thyroid']},
    vitamins:{label:'💊 Vitamins & Minerals',tests:[],kw:['Vitamin','Iron','Zinc','Magnesium','Folate','Folic','Ferritin']},
    other:{label:'🧪 Other Tests',tests:[],kw:[]}
  };

  for(const v of vals){
    let placed=false;
    for(const [key,cat] of Object.entries(categories)){
      if(key==='other') continue;
      if(cat.kw.some(kw=>v.name.toLowerCase().includes(kw.toLowerCase()))){cat.tests.push(v);placed=true;break;}
    }
    if(!placed) categories.other.tests.push(v);
  }

  const PC={Normal:'p-n',High:'p-h',Low:'p-l','Critical High':'p-c','Critical Low':'p-c'};
  const IC={Normal:'✓',High:'↑',Low:'↓','Critical High':'⚠','Critical Low':'⚠'};
  const VC={Normal:'var(--txt)',High:'var(--red)',Low:'var(--ylw)','Critical High':'var(--red)','Critical Low':'var(--ylw)'};

  let html='';
  for(const [key,cat] of Object.entries(categories)){
    if(!cat.tests.length) continue;
    const highs=cat.tests.filter(t=>['High','Critical High'].includes(t.status));
    const lows=cat.tests.filter(t=>['Low','Critical Low'].includes(t.status));
    const normals=cat.tests.filter(t=>t.status==='Normal');
    html+='<div class="test-category-card">';
    html+='<div class="test-cat-header">'+cat.label;
    if(highs.length) html+=' <span class="test-cat-badge badge-high">'+highs.length+' High</span>';
    if(lows.length) html+=' <span class="test-cat-badge badge-low">'+lows.length+' Low</span>';
    if(normals.length) html+=' <span class="test-cat-badge badge-normal">'+normals.length+' Normal</span>';
    html+='</div>';
    if(highs.length){html+='<div class="test-group"><div class="test-group-title" style="color:var(--red)">⬆ High Values</div>'+highs.map(v=>renderTestRow(v,VC,PC,IC)).join('')+'</div>';}
    if(lows.length){html+='<div class="test-group"><div class="test-group-title" style="color:var(--ylw)">⬇ Low Values</div>'+lows.map(v=>renderTestRow(v,VC,PC,IC)).join('')+'</div>';}
    if(normals.length){html+='<div class="test-group test-group-normal"><div class="test-group-title" style="color:var(--grn)">✓ Normal Values</div>'+normals.map(v=>renderTestRow(v,VC,PC,IC)).join('')+'</div>';}
    html+='</div>';
  }
  wrap.innerHTML=html;
}

function renderTestRow(v,VC,PC,IC){
  return '<div class="test-row">'+
    '<div class="test-name">'+v.name+'</div>'+
    '<div class="test-value" style="color:'+(VC[v.status]||'var(--txt)')+'">'+v.value+'</div>'+
    '<div class="test-range">'+v.normal_range+'</div>'+
    '<div><span class="pill '+(PC[v.status]||'p-n')+'">'+(IC[v.status]||'•')+' '+(v.strans||v.status)+'</span></div>'+
    (v.note&&v.status!=='Normal'?'<div class="test-note">'+v.note+'</div>':'')+
  '</div>';
}

// ── SUGGESTIONS (language-aware) ──────────────────────────────
function renderSuggestions(r){
  const lang=r.language||'English';
  const TITLE={English:'💡 Diet & Health Recommendations',Hindi:'💡 आहार और स्वास्थ्य सुझाव',Marathi:'💡 आहार आणि आरोग्य सूचना',Bengali:'💡 খাদ্য ও স্বাস্থ্য পরামর্শ',Tamil:'💡 உணவு மற்றும் ஆரோக்கிய பரிந்துரைகள்',Telugu:'💡 ఆహారం మరియు ఆరోగ్య సిఫారసులు'};
  const NO_SUGG={English:'Keep up your healthy habits! ✅',Hindi:'अपनी स्वस्थ आदतें जारी रखें! ✅',Marathi:'आरोग्यदायी सवयी चालू ठेवा! ✅',Bengali:'আপনার স্বাস্থ্যকর অভ্যাস চালিয়ে যান! ✅',Tamil:'உங்கள் ஆரோக்கியமான பழக்கங்களை தொடருங்கள்! ✅',Telugu:'మీ ఆరోగ్యకరమైన అలవాట్లను కొనసాగించండి! ✅'};
  const titleEl=document.getElementById('suggTitle');
  if(titleEl) titleEl.textContent=TITLE[lang]||TITLE.English;
  const suggEl=document.getElementById('suggList');
  if(!suggEl) return;
  const suggs=r.suggestions||[];
  suggEl.innerHTML=suggs.length?suggs.map(s=>'<div class="sugg-item"><div class="sugg-ico">'+s.icon+'</div><div class="sugg-txt"><strong>'+s.title+'</strong>'+s.detail+'</div></div>').join(''):'<p style="color:var(--mut)">'+(NO_SUGG[lang]||NO_SUGG.English)+'</p>';
}

// ── DOCTOR CONSULTATION SECTION ───────────────────────────────
function renderDoctorSection(r){
  const lang=r.language||'English';
  const TITLE={English:'🏥 Doctor Consultation & Advice',Hindi:'🏥 डॉक्टर परामर्श',Marathi:'🏥 डॉक्टर सल्लामसलत',Bengali:'🏥 চিকিৎসক পরামর্শ',Tamil:'🏥 மருத்துவர் ஆலோசனை',Telugu:'🏥 వైద్యుడి సలహా'};
  const URGENCY_TITLE={English:'⏱ Urgency Level',Hindi:'⏱ तात्कालिकता',Marathi:'⏱ तातडीची पातळी',Bengali:'⏱ জরুরি মাত্রা',Tamil:'⏱ அவசர நிலை',Telugu:'⏱ అత్యవసర స్థాయి'};
  const SPEC_TITLE={English:'👨‍⚕️ Suggested Specialist',Hindi:'👨‍⚕️ सुझाए गए विशेषज्ञ',Marathi:'👨‍⚕️ सुचवलेले तज्ज्ञ',Bengali:'👨‍⚕️ পরামর্শকৃত বিশেষজ্ঞ',Tamil:'👨‍⚕️ பரிந்துரைக்கப்பட்ட நிபுணர்',Telugu:'👨‍⚕️ సూచించిన నిపుణుడు'};
  const TEST_TITLE={English:'🔁 Recommended Follow-up Tests',Hindi:'🔁 अनुशंसित परीक्षण',Marathi:'🔁 शिफारस केलेल्या चाचण्या',Bengali:'🔁 প্রস্তাবিত পরীক্ষা',Tamil:'🔁 பரிந்துரைக்கப்பட்ட சோதனைகள்',Telugu:'🔁 సిఫారసు పరీక్షలు'};
  const BRING={English:'📋 Bring this report to your appointment.',Hindi:'📋 यह रिपोर्ट साथ लाएं।',Marathi:'📋 हा अहवाल सोबत आणा.',Bengali:'📋 এই রিপোর্ট নিয়ে যান।',Tamil:'📋 இந்த அறிக்கையை கொண்டு வாருங்கள்.',Telugu:'📋 ఈ నివేదికను తీసుకువెళ్ళండి.'};

  const urgencyInfo=getUrgencyInfo(r,lang);
  const specialists=getSuggestedSpecialists(r,lang);
  const followupTests=getFollowupTests(r,lang);

  const titleEl=document.getElementById('doctorSectionTitle');
  if(titleEl) titleEl.textContent=TITLE[lang]||TITLE.English;

  const contentEl=document.getElementById('doctorContent');
  if(!contentEl) return;

  contentEl.innerHTML=
    '<div class="doctor-advice-text">'+(r.doctor_advice||'')+'</div>'+
    '<div class="doctor-urgency"><strong>'+(URGENCY_TITLE[lang]||URGENCY_TITLE.English)+':</strong> <span class="urgency-badge urgency-'+urgencyInfo.level+'">'+urgencyInfo.label+'</span></div>'+
    (specialists.length?'<div class="doctor-specialists"><strong>'+(SPEC_TITLE[lang]||SPEC_TITLE.English)+':</strong> '+specialists.map(s=>'<span class="spec-pill">'+s+'</span>').join(' ')+'</div>':'')+
    (followupTests.length?'<div class="doctor-followup"><strong>'+(TEST_TITLE[lang]||TEST_TITLE.English)+':</strong><ul class="followup-list">'+followupTests.map(t=>'<li>'+t+'</li>').join('')+'</ul></div>':'')+
    '<div class="bring-report-note">'+(BRING[lang]||BRING.English)+'</div>';
}

function getUrgencyInfo(r,lang){
  const U={
    English:{emergency:{level:'emergency',label:'🚨 Emergency — Go Now'},asap:{level:'asap',label:'🏥 Within 2-3 Days'},soon:{level:'soon',label:'📅 Within 1-2 Weeks'},routine:{level:'routine',label:'✅ Routine Checkup'}},
    Hindi:{emergency:{level:'emergency',label:'🚨 आपातकाल — अभी जाएं'},asap:{level:'asap',label:'🏥 2-3 दिन में'},soon:{level:'soon',label:'📅 1-2 हफ्ते में'},routine:{level:'routine',label:'✅ नियमित जाँच'}},
    Marathi:{emergency:{level:'emergency',label:'🚨 आणीबाणी — आत्ताच जा'},asap:{level:'asap',label:'🏥 2-3 दिवसांत'},soon:{level:'soon',label:'📅 1-2 आठवड्यांत'},routine:{level:'routine',label:'✅ नियमित तपासणी'}},
    Bengali:{emergency:{level:'emergency',label:'🚨 জরুরি — এখনই যান'},asap:{level:'asap',label:'🏥 ২-৩ দিনের মধ্যে'},soon:{level:'soon',label:'📅 ১-২ সপ্তাহে'},routine:{level:'routine',label:'✅ নিয়মিত চেকআপ'}},
    Tamil:{emergency:{level:'emergency',label:'🚨 அவசரம் — இப்போது போங்கள்'},asap:{level:'asap',label:'🏥 2-3 நாட்களில்'},soon:{level:'soon',label:'📅 1-2 வாரங்களில்'},routine:{level:'routine',label:'✅ வழக்கமான பரிசோதனை'}},
    Telugu:{emergency:{level:'emergency',label:'🚨 అత్యవసరం — ఇప్పుడే వెళ్ళండి'},asap:{level:'asap',label:'🏥 2-3 రోజుల్లో'},soon:{level:'soon',label:'📅 1-2 వారాల్లో'},routine:{level:'routine',label:'✅ సాధారణ తనిఖీ'}}
  };
  const Ul=U[lang]||U.English;
  if(r.status_key==='Critical') return Ul.emergency;
  if(r.status_key==='Attention') return Ul.asap;
  if(r.status_key==='Fair') return Ul.soon;
  return Ul.routine;
}

function getSuggestedSpecialists(r,lang){
  const vals=r.lab_values||[];
  const specs=new Set();
  const S={
    English:{endo:'Endocrinologist',cardio:'Cardiologist',hemo:'Hematologist',nephro:'Nephrologist',gastro:'Gastroenterologist',general:'General Physician'},
    Hindi:{endo:'एंडोक्रिनोलॉजिस्ट',cardio:'कार्डियोलॉजिस्ट',hemo:'हेमेटोलॉजिस्ट',nephro:'नेफ्रोलॉजिस्ट',gastro:'गैस्ट्रोएंटेरोलॉजिस्ट',general:'सामान्य चिकित्सक'},
    Marathi:{endo:'एंडोक्रिनोलॉजिस्ट',cardio:'कार्डियोलॉजिस्ट',hemo:'हेमॅटोलॉजिस्ट',nephro:'नेफ्रोलॉजिस्ट',gastro:'गॅस्ट्रोएन्टेरोलॉजिस्ट',general:'सामान्य वैद्य'},
    Bengali:{endo:'এন্ডোক্রিনোলজিস্ট',cardio:'কার্ডিওলজিস্ট',hemo:'হেমাটোলজিস্ট',nephro:'নেফ্রোলজিস্ট',gastro:'গ্যাস্ট্রোএন্টেরোলজিস্ট',general:'সাধারণ চিকিৎসক'},
    Tamil:{endo:'நாளமில்லா நிபுணர்',cardio:'இதய நிபுணர்',hemo:'இரத்த நிபுணர்',nephro:'சிறுநீரக நிபுணர்',gastro:'இரைப்பை நிபுணர்',general:'பொது மருத்துவர்'},
    Telugu:{endo:'ఎండోక్రినాలజిస్ట్',cardio:'కార్డియాలజిస్ట్',hemo:'హేమటాలజిస్ట్',nephro:'నెఫ్రాలజిస్ట్',gastro:'గ్యాస్ట్రోఎంటరాలజిస్ట్',general:'జనరల్ ఫిజీషియన్'}
  };
  const Sp=S[lang]||S.English;
  for(const v of vals){
    const n=v.name.toLowerCase();
    if(n.includes('hba1c')||n.includes('glucose')||n.includes('tsh')||n.includes('t3')||n.includes('t4')) specs.add(Sp.endo);
    if(n.includes('cholesterol')||n.includes('ldl')||n.includes('hdl')||n.includes('triglyceride')) specs.add(Sp.cardio);
    if(n.includes('hemoglobin')||n.includes('wbc')||n.includes('rbc')||n.includes('platelet')||n.includes('ferritin')) specs.add(Sp.hemo);
    if(n.includes('creatinine')||n.includes('bun')||n.includes('urea')) specs.add(Sp.nephro);
    if(n.includes('alt')||n.includes('ast')||n.includes('bilirubin')||n.includes('alp')) specs.add(Sp.gastro);
  }
  if(!specs.size) specs.add(Sp.general);
  return Array.from(specs);
}

function getFollowupTests(r,lang){
  const vals=r.lab_values||[];
  const tests=new Set();
  const T={
    English:{hba1c:'Repeat HbA1c in 3 months',ogtt:'Oral Glucose Tolerance Test (OGTT)',lipid:'Full Lipid Panel in 6 weeks',echo:'Echocardiogram',tft:'Thyroid Function Test (TFT)',ferritin:'Serum Ferritin & Iron Studies',kidney:'Urine Routine + Creatinine Clearance',liver:'Complete LFT Panel',vitd:'Vitamin D3 retest in 3 months',b12:'Vitamin B12 + Folate levels'},
    Hindi:{hba1c:'3 महीने में HbA1c',ogtt:'OGTT परीक्षण',lipid:'लिपिड पैनल',echo:'इकोकार्डियोग्राम',tft:'थायरॉइड फंक्शन टेस्ट',ferritin:'फेरिटिन और आयरन',kidney:'यूरिन + क्रिएटिनिन क्लियरेंस',liver:'पूर्ण LFT',vitd:'विटामिन D3 दोबारा',b12:'विटामिन B12 + फोलेट'}
  };
  const Tt=T[lang]||T.English;
  for(const v of vals){
    if(v.status==='Normal') continue;
    const n=v.name.toLowerCase();
    if(n.includes('hba1c')) tests.add(Tt.hba1c);
    if(n.includes('glucose')) tests.add(Tt.ogtt);
    if(n.includes('cholesterol')||n.includes('ldl')){tests.add(Tt.lipid);tests.add(Tt.echo);}
    if(n.includes('tsh')||n.includes('t3')||n.includes('t4')) tests.add(Tt.tft);
    if(n.includes('hemoglobin')||n.includes('ferritin')) tests.add(Tt.ferritin);
    if(n.includes('creatinine')||n.includes('bun')) tests.add(Tt.kidney);
    if(n.includes('alt')||n.includes('ast')||n.includes('bilirubin')) tests.add(Tt.liver);
    if(n.includes('vitamin d')) tests.add(Tt.vitd);
    if(n.includes('b12')) tests.add(Tt.b12);
  }
  return Array.from(tests);
}

// ── FULL SUMMARY ─────────────────────────────────────────────
function renderFullSummary(r){
  const lang=r.language||'English';
  const TITLE={English:'📊 Full Report Summary',Hindi:'📊 पूर्ण रिपोर्ट सारांश',Marathi:'📊 संपूर्ण अहवाल सारांश',Bengali:'📊 সম্পূর্ণ রিপোর্ট সারসংক্ষেপ',Tamil:'📊 முழு அறிக்கை சுருக்கம்',Telugu:'📊 పూర్తి నివేదిక సారాంశం'};
  const titleEl=document.getElementById('fullSummaryTitle');
  if(titleEl) titleEl.textContent=TITLE[lang]||TITLE.English;
  const el=document.getElementById('fullSummaryContent');
  if(!el) return;
  const p=r.patient||{};
  const SC={Good:'var(--grn)',Fair:'var(--ylw)',Attention:'var(--org)',Critical:'var(--red)'};
  const sc=SC[r.status_key]||'var(--ylw)';
  const highs=(r.lab_values||[]).filter(v=>['High','Critical High'].includes(v.status));
  const lows=(r.lab_values||[]).filter(v=>['Low','Critical Low'].includes(v.status));
  const normals=(r.lab_values||[]).filter(v=>v.status==='Normal');
  el.innerHTML=
    '<div class="summary-grid">'+
      '<div class="summary-item"><span class="summary-label">Patient</span><span class="summary-val">'+(p.name||'—')+'</span></div>'+
      '<div class="summary-item"><span class="summary-label">Age / Gender</span><span class="summary-val">'+(p.age||'—')+' / '+(p.gender||'—')+'</span></div>'+
      '<div class="summary-item"><span class="summary-label">Report Type</span><span class="summary-val">'+r.report_type+'</span></div>'+
      '<div class="summary-item"><span class="summary-label">Status</span><span class="summary-val" style="color:'+sc+'">'+r.status_label+'</span></div>'+
      '<div class="summary-item"><span class="summary-label">Total Tests</span><span class="summary-val">'+r.total_tests+'</span></div>'+
      '<div class="summary-item"><span class="summary-label">Normal</span><span class="summary-val" style="color:var(--grn)">'+normals.length+'</span></div>'+
      '<div class="summary-item"><span class="summary-label">High</span><span class="summary-val" style="color:var(--red)">'+highs.length+'</span></div>'+
      '<div class="summary-item"><span class="summary-label">Low</span><span class="summary-val" style="color:var(--ylw)">'+lows.length+'</span></div>'+
    '</div>'+
    (highs.length?'<div class="summary-section"><div class="summary-sec-title" style="color:var(--red)">⬆ Elevated</div>'+highs.map(v=>'<span class="summary-pill summary-pill-high">'+v.name+': '+v.value+'</span>').join('')+'</div>':'')+
    (lows.length?'<div class="summary-section"><div class="summary-sec-title" style="color:var(--ylw)">⬇ Low</div>'+lows.map(v=>'<span class="summary-pill summary-pill-low">'+v.name+': '+v.value+'</span>').join('')+'</div>':'')+
    '<div class="summary-explanation">'+r.explanation+'</div>';
}

function resetApp(){
  reportCtx=null;
  document.getElementById('heroSec').style.display='block';
  document.getElementById('dashSec').style.display='none';
  document.getElementById('loadSec').style.display='none';
  document.getElementById('extractMsg').style.display='none';
  document.getElementById('saveRptBtn').style.display='none';
  document.getElementById('fileTag').style.display='none';
  document.getElementById('fi').value='';
  const ta=document.getElementById('reportTxt'); ta.value=''; ta.placeholder='Paste your lab report here...';
  document.getElementById('analyzeBtn').disabled=true;
  window.scrollTo({top:0,behavior:'smooth'});
}
function resetForm(){ document.getElementById('fileTag').style.display='none'; document.getElementById('fi').value=''; document.getElementById('extractMsg').style.display='none'; }

async function saveCurrentReport(){
  if(!currentUser||currentUser.isGuest){showPage('signup');return;}
  if(!reportCtx) return;
  const r=await API('/api/report/save',{method:'POST',body:JSON.stringify({result:reportCtx,raw_text:reportCtx.rawText||''})});
  if(r.id){ document.getElementById('saveRptBtn').style.display='none'; showToast('Report saved to history! 💾','ok'); }
}

// ── HISTORY ───────────────────────────────────────────────────
async function loadHistory(){
  const el=document.getElementById('histList');
  if(!currentUser){
    el.innerHTML='<div class="hist-empty"><div class="hist-empty-icon">🔒</div><h3>Sign in to view history</h3><p>Create a free account to save your reports.</p><button class="btn-sm btn-primary" onclick="goSignup()" style="margin-top:.8rem">Create Free Account</button></div>';
    return;
  }
  if(currentUser.isGuest){
    allHistory=LS.getGuestHistory();
    renderHist(allHistory,true);
    return;
  }
  const d=await API('/api/history');
  allHistory=d.reports||[];
  renderHist(allHistory,false);
}

function filterHist(f,btn){
  document.querySelectorAll('.flt-btn').forEach(b=>b.classList.remove('active')); btn.classList.add('active');
  renderHist(f==='all'?allHistory:allHistory.filter(r=>r.overall_status===f),currentUser?.isGuest);
}

function renderHist(rpts,isGuest){
  const el=document.getElementById('histList');
  if(!rpts||!rpts.length){
    el.innerHTML='<div class="hist-empty"><div class="hist-empty-icon">📋</div><h3>No reports yet</h3><p>Analyze your first report to see it here.</p><button class="btn-sm btn-primary" onclick="goHome()" style="margin-top:.8rem">Analyze a Report</button></div>';
    return;
  }
  const sIco={Good:'🟢',Fair:'🟡',Attention:'🟠',Critical:'🔴'};
  const sCol={Good:'var(--grn)',Fair:'var(--ylw)',Attention:'var(--org)',Critical:'var(--red)'};
  const sBg={Good:'rgba(52,211,153,.1)',Fair:'rgba(251,191,36,.1)',Attention:'rgba(251,146,60,.1)',Critical:'rgba(248,113,113,.1)'};
  el.innerHTML='<div style="display:grid;gap:.9rem">'+rpts.map((r,i)=>{
    const ico=sIco[r.overall_status]||'⚪',col=sCol[r.overall_status]||'var(--mut)',bg=sBg[r.overall_status]||'rgba(56,189,248,.08)';
    const d=r.uploaded_at?new Date(r.uploaded_at).toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'}):'?';
    const viewFn=isGuest?`loadGuestHistReport('${r.id}')`:`loadHistReport(${r.id})`;
    const delFn=isGuest?`delGuestHistReport('${r.id}',${i})`:`delHistReport(${r.id},${i})`;
    return '<div class="hcard" id="hc'+i+'" style="animation-delay:'+i*.06+'s">'+
      '<div class="hcard-hdr" onclick="toggleHcard('+i+')">'+
      '<div class="hcard-ico" style="background:'+bg+'">'+ico+'</div>'+
      '<div style="flex:1;min-width:0"><div class="hcard-title">'+r.report_type+'</div>'+
      '<div class="hcard-meta"><span>'+d+'</span><span>'+r.total_tests+' tests</span>'+(r.patient_name&&r.patient_name!=='Unknown'?'<span>'+r.patient_name+'</span>':'')+'</div></div>'+
      '<div class="hcard-right"><span class="pill" style="color:'+col+';background:'+bg+'">'+ico+' '+r.overall_status+'</span>'+
      '<button class="expand-btn" id="eb'+i+'">▾</button></div></div>'+
      '<div class="hcard-body">'+
      '<div class="hcard-actions"><button class="hact hact-view" onclick="'+viewFn+'">View Analysis</button>'+
      '<button class="hact hact-del" onclick="'+delFn+'">Delete</button></div></div></div>';
  }).join('')+'</div>';
}

function toggleHcard(i){ const c=document.getElementById('hc'+i); c.classList.toggle('expanded'); document.getElementById('eb'+i).textContent=c.classList.contains('expanded')?'▴':'▾'; }

async function loadHistReport(id){
  const d=await API('/api/report/'+id);
  if(d.result){ reportCtx=d.result; showPage('home'); document.getElementById('heroSec').style.display='none'; setTimeout(()=>renderDash(d.result),100); }
}
function loadGuestHistReport(id){
  const entry=LS.getGuestHistory().find(r=>r.id===id);
  if(entry&&entry.result){ reportCtx=entry.result; showPage('home'); document.getElementById('heroSec').style.display='none'; setTimeout(()=>renderDash(entry.result),100); }
}
async function delHistReport(id,i){
  if(!confirm('Delete this report?')) return;
  await API('/api/report/'+id,{method:'DELETE'});
  allHistory=allHistory.filter(r=>r.id!==id);
  renderHist(allHistory,false); showToast('Report deleted','info');
}
function delGuestHistReport(id,i){
  if(!confirm('Delete this report?')) return;
  LS.deleteGuestReport(id);
  allHistory=LS.getGuestHistory();
  renderHist(allHistory,true); showToast('Report deleted','info');
}

// ── TOAST ─────────────────────────────────────────────────────
function showToast(msg,type){
  const wrap=document.getElementById('toastWrap');
  const icons={ok:'✅',err:'❌',info:'ℹ️'};
  const d=document.createElement('div'); d.className='toast '+(type||'info');
  d.innerHTML=(icons[type]||'ℹ️')+' '+msg; wrap.appendChild(d);
  setTimeout(()=>{d.style.opacity='0';d.style.transform='translateX(16px)';d.style.transition='all .3s';setTimeout(()=>{if(d.parentNode)d.parentNode.removeChild(d);},320);},3200);
}

// ── CHATBOT ───────────────────────────────────────────────────
async function checkOllamaStatus(){
  try {
    const r=await fetch('/api/chat/status'); const d=await r.json();
    const st=document.getElementById('botSt'); const notice=document.getElementById('ollamaNotice');
    if(d.status==='ready'){st.textContent='🟢 phi3 ready — local AI active';st.style.color='var(--grn)';if(notice)notice.style.display='none';}
    else if(d.status==='phi3_not_pulled'){st.textContent='⚠️ phi3 not pulled';st.style.color='var(--ylw)';if(notice)notice.style.display='block';}
    else{st.textContent='⚠️ Ollama offline — basic Q&A mode';st.style.color='var(--ylw)';if(notice)notice.style.display='block';}
  } catch(e){ const st=document.getElementById('botSt'); if(st) st.textContent='Basic Q&A mode'; }
}

function toggleChat(){
  chatOpen=!chatOpen;
  document.getElementById('chatPanel').classList.toggle('open',chatOpen);
  document.getElementById('chatFab').textContent=chatOpen?'✕':'💬';
  if(chatOpen){ document.getElementById('chatIn').focus(); checkOllamaStatus(); }
}

function addMsg(txt,type){ const msgs=document.getElementById('chatMsgs'); const d=document.createElement('div'); d.className='msg '+type; d.innerHTML=txt.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\n/g,'<br>'); msgs.appendChild(d); msgs.scrollTop=msgs.scrollHeight; }
function showTyping(){ const msgs=document.getElementById('chatMsgs'); const d=document.createElement('div'); d.className='msg bot'; d.id='typing'; d.innerHTML='<div class="typing"><span></span><span></span><span></span></div>'; msgs.appendChild(d); msgs.scrollTop=msgs.scrollHeight; }

async function sendChat(){
  const inp=document.getElementById('chatIn'); const msg=inp.value.trim(); if(!msg) return;
  inp.value=''; addMsg(msg,'user'); showTyping();
  document.getElementById('sendBtn').disabled=true;
  const lang=document.getElementById('langSel').value;
  const msgs=document.getElementById('chatMsgs');
  let botDiv=null;
  try {
    const resp=await fetch('/api/chat/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,language:lang,report_context:reportCtx})});
    document.getElementById('typing')?.remove();
    const reader=resp.body.getReader(); const decoder=new TextDecoder(); let fullText='';
    while(true){
      const {done,value}=await reader.read(); if(done) break;
      const chunk=decoder.decode(value); const lines=chunk.split('\n');
      for(const line of lines){
        if(line.startsWith('data: ')){
          const token=line.slice(6); if(token==='[DONE]') break;
          fullText+=token;
          if(!botDiv){botDiv=document.createElement('div');botDiv.className='msg bot';msgs.appendChild(botDiv);}
          botDiv.innerHTML=fullText.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\n/g,'<br>');
          msgs.scrollTop=msgs.scrollHeight;
        }
      }
    }
    if(!fullText) addMsg('⏳ phi3 is loading. Please try again.','bot');
  } catch(e){ document.getElementById('typing')?.remove(); addMsg('⚠️ Connection error: '+e.message,'bot'); }
  document.getElementById('sendBtn').disabled=false;
  document.getElementById('chatIn').focus();
}
