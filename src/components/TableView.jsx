import React from 'react';

export default function TableView({ docs, onEdit }) {
  return (
    <table>
      <thead>
        <tr><th>ID</th><th>Category</th><th>Title</th><th>Action</th></tr>
      </thead>
      <tbody>
        {docs.map(doc => (
          <tr key={doc.id}>
            <td>{doc.id}</td>
            <td>{doc.category}</td>
            <td>{doc.title}</td>
            <td><button onClick={() => onEdit(doc)}>Edit</button></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
