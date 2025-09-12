import Dexie from './libs/dexie.min.js';

export const db = new Dexie("sajuDB");
db.version(1).stores({
  documents: "++id, category, title, content, createdAt"
});

export async function addDoc(doc) {
  return await db.documents.add({...doc, createdAt: new Date()});
}
export async function getAllDocs() {
  return await db.documents.toArray();
}
export async function updateDoc(id, data) {
  return await db.documents.update(id, data);
}
export async function deleteDoc(id) {
  return await db.documents.delete(id);
}
