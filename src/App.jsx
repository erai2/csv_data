import React, { useEffect, useState } from 'react';
import { getAllDocuments } from './hooks/useIndexedDB';
import UploadPanel from './components/UploadPanel';
import TableView from './components/TableView';
import EditorModal from './components/EditorModal';
import AIQuestionBox from './components/AIQuestionBox';

export default function App() {
  const [docs, setDocs] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);

  useEffect(() => {
    getAllDocuments().then(setDocs);
  }, []);

  return (
    <div>
      <h1>📂 문서 관리 + AI</h1>
      <UploadPanel setDocs={setDocs} />
      <AIQuestionBox docs={docs} />
      <TableView docs={docs} onEdit={setSelectedDoc} />
      {selectedDoc && (
        <EditorModal doc={selectedDoc} setDocs={setDocs} onClose={() => setSelectedDoc(null)} />
      )}
    </div>
  );
}
