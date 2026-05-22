"use client";

import { useState } from "react";
import { Send, Bot, User, Settings2, Paperclip } from "lucide-react";

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hello! I am ElseaAI. How can I assist you today? You can ask me about documents you've uploaded or general questions." }
  ]);
  const [input, setInput] = useState("");
  const [model, setModel] = useState("llama3.2");

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { role: "user", content: input }]);
    setInput("");
    
    // Simulate streaming response
    setTimeout(() => {
      setMessages((prev) => [...prev, { role: "assistant", content: "This is a simulated response. The real backend will stream Ollama output here." }]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/50">
        <div className="flex items-center space-x-2">
          <Bot className="w-6 h-6 text-blue-500" />
          <h2 className="text-lg font-semibold text-white">AI Assistant</h2>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-slate-400">Model:</span>
          <select 
            className="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-1.5 outline-none focus:ring-2 focus:ring-blue-500"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            <option value="llama3.2">Llama 3.2</option>
            <option value="qwen2.5">Qwen 2.5</option>
            <option value="deepseek">Deepseek Coder</option>
          </select>
          <button className="p-1.5 hover:bg-slate-800 rounded-lg transition-colors">
            <Settings2 className="w-5 h-5 text-slate-400" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`flex items-start max-w-[80%] ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
              <div className={`p-2 rounded-lg flex-shrink-0 ${msg.role === "user" ? "bg-blue-600 ml-4" : "bg-slate-800 mr-4"}`}>
                {msg.role === "user" ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-blue-400" />}
              </div>
              <div className={`p-4 rounded-2xl ${msg.role === "user" ? "bg-blue-600 text-white rounded-tr-sm" : "bg-slate-800 text-slate-200 rounded-tl-sm border border-slate-700"}`}>
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 bg-slate-900 border-t border-slate-800">
        <div className="flex items-end bg-slate-800 rounded-xl border border-slate-700 focus-within:ring-2 focus-within:ring-blue-500 p-2">
          <button className="p-2 text-slate-400 hover:text-white transition-colors">
            <Paperclip className="w-5 h-5" />
          </button>
          <textarea 
            className="flex-1 max-h-32 bg-transparent border-none outline-none text-white text-sm resize-none px-3 py-2"
            placeholder="Type your message..."
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <button 
            className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors ml-2"
            onClick={handleSend}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
