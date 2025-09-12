import Fuse from './libs/fuse.min.js';
import { getAllDocs } from './db.js';

export async function searchDocs(keyword) {
  const docs = await getAllDocs();
  const fuse = new Fuse(docs, { keys: ["title","content"], threshold: 0.3 });
  return keyword ? fuse.search(keyword).map(r=>r.item) : docs;
}
