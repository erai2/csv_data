import React, { useState } from 'react';
import { updateDocument, deleteDocument, getAllDocuments } from '../hooks/useIndexedDB';

export default function EditorModal({ doc, setDocs, onClose }) {
  const [title, setTitle] = useState(doc.title);
  const [content, setContent] = useState(doc.content);

  const handleSave = async () => {
    await updateDocument(doc.id, { title, content });
    setDocs(await getAllDocuments());
    onClose();
  };

  const handleDelete = async () => {
    await deleteDocument(doc.id);
    setDocs(await getAllDocuments());
    onClose();
  };

  return (
    <div className="modal">
      <h3>Edit Document</h3>
      <input value={title} onChange={(e) => setTitle(e.target.value)} />
      <textarea value={content} onChange={(e) => setContent(e.target.value)} />
      <button onClick={handleSave}>Save</button>
      <button onClick={handleDelete}>Delete</button>
      <button onClick={onClose}>Close</button>
    </div>
  );
}
