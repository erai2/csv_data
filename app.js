let docs = [];
let currentId = null;

const fileInput = document.getElementById('fileInput');
const tableBody = document.querySelector('#docTable tbody');
const modal = document.getElementById('modal');
const editTitle = document.getElementById('editTitle');
const editContent = document.getElementById('editContent');
const saveBtn = document.getElementById('saveBtn');
const deleteBtn = document.getElementById('deleteBtn');
const closeBtn = document.getElementById('closeBtn');

fileInput.addEventListener('change', async (e) => {
  const files = e.target.files;
  for (let file of files) {
    const text = await file.text();
    const category = detectCategory(text);
    const doc = { id: Date.now() + Math.random(), title: file.name, category, content: text };
    docs.push(doc);
  }
  renderTable();
});

function detectCategory(text) {
  if (text.includes('규칙')) return 'rules';
  if (text.includes('사례')) return 'cases';
  return 'concepts';
}

function renderTable() {
  tableBody.innerHTML = '';
  docs.forEach((doc) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${doc.id}</td>
      <td>${doc.category}</td>
      <td>${doc.title}</td>
      <td><button onclick="editDoc(${doc.id})">Edit</button></td>
    `;
    tableBody.appendChild(row);
  });
}

window.editDoc = (id) => {
  const doc = docs.find(d => d.id === id);
  currentId = id;
  editTitle.value = doc.title;
  editContent.value = doc.content;
  modal.classList.remove('hidden');
};

saveBtn.addEventListener('click', () => {
  const idx = docs.findIndex(d => d.id === currentId);
  docs[idx].title = editTitle.value;
  docs[idx].content = editContent.value;
  modal.classList.add('hidden');
  renderTable();
});

deleteBtn.addEventListener('click', () => {
  docs = docs.filter(d => d.id !== currentId);
  modal.classList.add('hidden');
  renderTable();
});

closeBtn.addEventListener('click', () => {
  modal.classList.add('hidden');
});
