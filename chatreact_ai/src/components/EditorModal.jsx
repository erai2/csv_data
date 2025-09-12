import React, { useState } from 'react';
import { updateDocument, deleteDocument, getAllDocuments } from '../hooks/useIndexedDB';
import { summarizeText } from '../hooks/useAI';

export default function EditorModal({ doc, setDocs, onClose }) {
  const [title, setTitle] = useState(doc.title);
  const [content, setContent] = useState(doc.content);
  const [summary, setSummary] = useState("");

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

  const handleSummarize = async () => {
    const result = await summarizeText(content);
    setSummary(result);
  };

  return (
    <div className="modal">
      <h3>Edit Document</h3>
      <input value={title} onChange={(e) => setTitle(e.target.value)} />
      <textarea value={content} onChange={(e) => setContent(e.target.value)} />
      <div>
        <button onClick={handleSave}>Save</button>
        <button onClick={handleDelete}>Delete</button>
        <button onClick={handleSummarize}>AI 요약</button>
        <button onClick={onClose}>Close</button>
      </div>
      {summary && <div><h4>AI Summary</h4><p>{summary}</p></div>}
    </div>
  );
}
