'use strict';
const $ = id => document.getElementById(id);
const stages = ['','Ý tưởng','SPEC','Thiết kế','Lập trình','Kiểm thử','Kiểm toán','Phê duyệt','Triển khai'];
function cell(row, value) {const td = document.createElement('td');td.textContent = value ?? '';row.appendChild(td);return td;}
function emptyRow(tbody, columns, message){const tr=document.createElement('tr');const td=cell(tr,message);td.colSpan=columns;tbody.appendChild(tr);}
async function selectProject(id){
  try{
    const res=await fetch('/api/projects/'+encodeURIComponent(id));if(!res.ok)throw Error('Không tải được chi tiết');
    const data=await res.json();$('detail').hidden=false;
    $('detail-title').textContent=data.project.name+' ('+data.project.id+')';
    $('detail-stage').textContent=stages[data.project.stage]||'Không rõ';
    const tasks=$('task-list');tasks.replaceChildren();
    for(const t of data.tasks){const row=document.createElement('tr');cell(row,t.id);cell(row,t.title);cell(row,t.owner);cell(row,t.status);tasks.appendChild(row);}
    if(!data.tasks.length)emptyRow(tasks,4,'Chưa có nhiệm vụ.');
    const gates=$('gate-list');gates.replaceChildren();
    for(const g of data.gates){const item=document.createElement('div');item.className='gate';const name=document.createElement('b');name.textContent='GATE '+g.gate_number;const status=document.createElement('span');status.textContent=g.decision;item.append(name,status);gates.appendChild(item);}
  }catch(err){$('feedback').textContent=String(err.message)}
}
(async ()=>{try{
  const res=await fetch('/api/projects');if(!res.ok)throw Error('Không đọc được danh mục');
  const projects=await res.json();$('count-projects').textContent=projects.length;
  $('count-completed').textContent=projects.filter(p=>p.status==='COMPLETE').length;
  $('count-active').textContent=projects.filter(p=>p.status!=='COMPLETE').length;
  $('feedback').textContent=projects.length?'Chọn một dự án để xem nhiệm vụ và Quality Gate.':'Chưa có dự án. Dùng công cụ CLI để tạo dự án đầu tiên.';
  const tbody=$('project-list');
  for(const p of projects){const tr=document.createElement('tr');const td=document.createElement('td');const link=document.createElement('button');link.className='link';link.textContent=p.id;link.addEventListener('click',()=>selectProject(p.id));td.appendChild(link);tr.appendChild(td);cell(tr,p.name);cell(tr,p.owner);cell(tr,stages[p.stage]);cell(tr,p.status);tbody.appendChild(tr);}
  if(!projects.length)emptyRow(tbody,5,'Danh sách trống');
}catch(err){$('feedback').textContent='Lỗi: '+String(err.message)}})();
