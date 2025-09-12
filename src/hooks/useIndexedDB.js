import Dexie from 'dexie';

export const db = new Dexie('sajuDB');
db.version(1).stores({
  documents: '++id, category, title, content, createdAt'
});

export async function addDocument(doc) {
  return await db.documents.add({ ...doc, createdAt: new Date() });
}
export async function getAllDocuments() {
  return await db.documents.toArray();
}
export async function updateDocument(id, data) {
  return await db.documents.update(id, data);
}
export async function deleteDocument(id) {
  return await db.documents.delete(id);
}
