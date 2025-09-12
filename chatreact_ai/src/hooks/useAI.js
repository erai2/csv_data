export async function askAI(question, context) {
  const API_KEY = import.meta.env.VITE_OPENAI_API_KEY;
  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "gpt-4",
      messages: [
        { role: "system", content: "You are a helpful assistant summarizing Saju documents." },
        { role: "user", content: `Context:\n${context}\n\nQuestion:\n${question}` }
      ]
    })
  });
  const data = await response.json();
  return data.choices[0].message.content;
}

export async function summarizeText(content) {
  return await askAI("Summarize this document in Korean.", content);
}
