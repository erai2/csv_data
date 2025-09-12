import { addDoc, getAllDocs, updateDoc, deleteDoc } from './db.js';
import { searchDocs } from './search.js';

document.addEventListener("DOMContentLoaded", init);

async function init() {
  renderTable(await getAllDocs());
  
  document.getElementById("uploadInput").addEventListener("change", handleUpload);
  document.getElementById("searchBox").addEventListener("input", async (e)=>{
    const keyword = e.target.value.trim();
    renderTable(await searchDocs(keyword));
  });
}

async function handleUpload(e){
  const files = e.target.files;
  for(let f of files){
    const text = await f.text();
    const category = detectCategory(text);
    await addDoc({ category, title: f.name, content: text });
  }
  renderTable(await getAllDocs());
}

function detectCategory(text){
  if(text.includes("규칙")) return "rules";
  if(text.includes("사례")) return "cases";
  return "concepts";
}

async function renderTable(docs){
  const tbody = document.getElementById("docTableBody");
  tbody.innerHTML = "";
  docs.forEach(doc=>{
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${doc.id}</td>
      <td>${doc.category}</td>
      <td>${doc.title}</td>
      <td><button onclick="viewDoc(${doc.id})">보기</button></td>`;
    tbody.appendChild(row);
  });
}

window.viewDoc = async function(id){
  const doc = (await getAllDocs()).find(d=>d.id===id);
  document.getElementById("editorTitle").value = doc.title;
  document.getElementById("editorContent").value = doc.content;
  document.getElementById("saveBtn").onclick = async ()=>{
    await updateDoc(id,{ title: editorTitle.value, content: editorContent.value });
    renderTable(await getAllDocs());
  };
  document.getElementById("deleteBtn").onclick = async ()=>{
    await deleteDoc(id);
    renderTable(await getAllDocs());
  };
  document.getElementById("editor").style.display="block";
}
