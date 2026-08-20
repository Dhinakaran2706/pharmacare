let medicines=[], suppliers=[], customers=[];

const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));

document.querySelectorAll('.nav-item').forEach(btn=>btn.addEventListener('click',()=>showSection(btn.dataset.section)));
function showSection(name){
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(b=>b.classList.toggle('active',b.dataset.section===name));
  $(name)?.classList.add('active');
  const title=name.charAt(0).toUpperCase()+name.slice(1);
  $('sectionTitle').textContent=title;
  if(name==='medicines') renderMedicines();
  if(name==='suppliers') renderGeneric('supplier');
  if(name==='customers') renderGeneric('customer');
  document.getElementById('sidebar').classList.remove('open');
}
$('menuBtn').onclick=()=> $('sidebar').classList.toggle('open');

async function api(url, options={}){
  const res=await fetch(url,{headers:{'Content-Type':'application/json'},...options});
  const data=await res.json().catch(()=>({}));
  if(!res.ok) throw new Error(data.error||'Request failed');
  return data;
}
async function loadAll(){
  try{
    [medicines,suppliers,customers]=await Promise.all([api('/api/medicines'),api('/api/suppliers'),api('/api/customers')]);
    renderMedicines(); renderGeneric('supplier'); renderGeneric('customer'); updateDashboard();
  }catch(e){toast(e.message)}
}
async function loadMedicines(){try{medicines=await api('/api/medicines');renderMedicines();updateDashboard();toast('Inventory refreshed')}catch(e){toast(e.message)}}

function medicineStatus(m){
  const days=(new Date(m.expiry)-new Date())/86400000;
  if(days<=90) return ['Expiring','exp'];
  if(Number(m.stock)<=10) return ['Low stock','low'];
  return ['Healthy','ok'];
}
function renderMedicines(){
  const q=($('medicineSearch')?.value||'').toLowerCase(), cat=$('categoryFilter')?.value||'';
  const list=medicines.filter(m=>(!q||`${m.name} ${m.category} ${m.batch}`.toLowerCase().includes(q))&&(!cat||m.category===cat));
  $('medicineRows').innerHTML=list.length?list.map(m=>{
    const [st,cl]=medicineStatus(m);
    return `<tr><td><span class="medicine-name">${esc(m.name)}</span></td><td>${esc(m.category)}</td><td>${esc(m.batch)}</td><td>₹${Number(m.price).toFixed(2)}</td><td><b>${m.stock}</b></td><td>${esc(m.expiry)}</td><td><span class="badge ${cl}">${st}</span></td><td><div class="actions"><button class="action" onclick="editMedicine('${m.id}')">✎</button><button class="action" onclick="deleteMedicine('${m.id}')">🗑</button></div></td></tr>`
  }).join(''):`<tr><td colspan="8" style="text-align:center;padding:35px">No medicines found.</td></tr>`;
}
function updateDashboard(){
  const low=medicines.filter(m=>Number(m.stock)<=10).length;
  const exp=medicines.filter(m=>(new Date(m.expiry)-new Date())/86400000<=90).length;
  const healthy=Math.max(medicines.length-low-exp,0), pct=medicines.length?Math.round(healthy/medicines.length*100):0;
  $('statMedicines').textContent=medicines.length;$('statLow').textContent=low;$('statExpiry').textContent=exp;
  $('healthPercent').textContent=pct+'%';$('healthyCount').textContent=healthy;$('lowCount').textContent=low;$('expiryCount').textContent=exp;
  $('healthText').textContent=`${healthy} of ${medicines.length} medicines are in healthy stock.`;
  $('donut')?.style.setProperty('background',`conic-gradient(#7c3aed ${pct*3.6}deg,#e5e7eb ${pct*3.6}deg)`);
  $('dashboardMedicineRows').innerHTML=medicines.slice(0,6).map(m=>{const [st,cl]=medicineStatus(m);return `<tr><td class="medicine-name">${esc(m.name)}</td><td>${esc(m.category)}</td><td>${m.stock}</td><td>${esc(m.expiry)}</td><td><span class="badge ${cl}">${st}</span></td></tr>`}).join('')||`<tr><td colspan="5" style="text-align:center;padding:30px">No medicines added yet.</td></tr>`;
}
function openMedicineModal(id=null){
  $('medicineForm').reset();$('medicineId').value='';$('medicineModalTitle').textContent='Add Medicine';
  if(id){const m=medicines.find(x=>x.id===id);if(!m)return;$('medicineModalTitle').textContent='Edit Medicine';$('medicineId').value=m.id;['name','category','batch','price','stock','expiry','supplier'].forEach(k=>$(k).value=m[k]??"")}
  $('medicineModal').classList.add('show');
}
function editMedicine(id){openMedicineModal(id)}
async function deleteMedicine(id){
  if(!confirm('Delete this medicine?'))return;
  try{await api('/api/medicines/'+id,{method:'DELETE'});await loadMedicines();toast('Medicine deleted')}catch(e){toast(e.message)}
}
$('medicineForm').onsubmit=async e=>{
  e.preventDefault();
  const id=$('medicineId').value;
  const payload={name:$('name').value,category:$('category').value,batch:$('batch').value,price:Number($('price').value),stock:Number($('stock').value),expiry:$('expiry').value,supplier:$('supplier').value};
  try{await api('/api/medicines'+(id?'/'+id:''),{method:id?'PUT':'POST',body:JSON.stringify(payload)});closeModal('medicineModal');await loadMedicines();toast(id?'Medicine updated':'Medicine added')}catch(err){toast(err.message)}
};

function openGenericModal(type,id=null){
  $('genericForm').reset();$('genericId').value=id||'';$('genericType').value=type;
  $('genericTitle').textContent=(id?'Edit ':'Add ')+(type==='supplier'?'Supplier':'Customer');
  const list=type==='supplier'?suppliers:customers;
  if(id){const x=list.find(v=>v.id===id);if(x){$('genericName').value=x.name||'';$('genericPhone').value=x.phone||'';$('genericEmail').value=x.email||'';$('genericExtra').value=x.extra||""}}
  $('genericExtraLabel').firstChild.textContent=type==='supplier'?'Company / ':'Address / ';
  $('genericModal').classList.add('show');
}
$('genericForm').onsubmit=async e=>{
  e.preventDefault();const type=$('genericType').value,id=$('genericId').value;
  const payload={name:$('genericName').value,phone:$('genericPhone').value,email:$('genericEmail').value,extra:$('genericExtra').value};
  try{await api('/api/'+type+'s'+(id?'/'+id:''),{method:id?'PUT':'POST',body:JSON.stringify(payload)});closeModal('genericModal');if(type==='supplier')suppliers=await api('/api/suppliers');else customers=await api('/api/customers');renderGeneric(type);toast('Record saved')}catch(err){toast(err.message)}
};
function renderGeneric(type){
  const list=type==='supplier'?suppliers:customers,id=type==='supplier'?'supplierRows':'customerRows';
  $(id).innerHTML=list.length?list.map(x=>`<tr><td class="medicine-name">${esc(x.name)}</td><td>${esc(x.phone)}</td><td>${esc(x.email)}</td><td>${esc(x.extra)}</td><td><div class="actions"><button class="action" onclick="openGenericModal('${type}','${x.id}')">✎</button><button class="action" onclick="deleteGeneric('${type}','${x.id}')">🗑</button></div></td></tr>`).join(''):`<tr><td colspan="5" style="text-align:center;padding:35px">No records found.</td></tr>`;
}
async function deleteGeneric(type,id){if(!confirm('Delete this record?'))return;try{await api('/api/'+type+'s/'+id,{method:'DELETE'});if(type==='supplier')suppliers=await api('/api/suppliers');else customers=await api('/api/customers');renderGeneric(type);toast('Record deleted')}catch(e){toast(e.message)}}

function closeModal(id){$(id).classList.remove('show')}
document.querySelectorAll('.modal-backdrop').forEach(x=>x.addEventListener('click',e=>{if(e.target===x)x.classList.remove('show')}));
function toast(msg){const t=$('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2400)}
$('globalSearch').addEventListener('keydown',e=>{if(e.key==='Enter'){showSection('medicines');$('medicineSearch').value=e.target.value;renderMedicines()}});

loadAll();