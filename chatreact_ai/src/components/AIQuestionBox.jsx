import React, { useState } from 'react';
import { askAI } from '../hooks/useAI';

export default function AIQuestionBox({ docs }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleAsk = async () => {
    const context = docs.map(d => `${d.title}\n${d.content}`).join("\n\n");
    const res = await askAI(question, context);
    setAnswer(res);
  };

  return (
    <div className="ai-box">
      <h3>AI 질문</h3>
      <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="질문 입력..." />
      <button onClick={handleAsk}>Ask</button>
      {answer && <div><h4>답변</h4><p>{answer}</p></div>}
    </div>
  );
}
