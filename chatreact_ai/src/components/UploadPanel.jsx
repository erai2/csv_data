import React from 'react';
import { addDocument, getAllDocuments } from '../hooks/useIndexedDB';

export default function UploadPanel({ setDocs }) {
  const handleUpload = async (e) => {
    const files = e.target.files;
    for (let file of files) {
      const text = await file.text();
      const category = detectCategory(text);
      await addDocument({ title: file.name, category, content: text });
    }
    setDocs(await getAllDocuments());
  };

  const detectCategory = (text) => {
    if (text.includes('규칙')) return 'rules';
    if (text.includes('사례')) return 'cases';
    return 'concepts';
  };

  return (
    <div>
      <input type="file" multiple onChange={handleUpload} />
    </div>
  );
}
