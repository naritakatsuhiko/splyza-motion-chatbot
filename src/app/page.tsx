"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function MotionChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();
      if (data.text) {
        setMessages((prev) => [...prev, { role: "assistant", content: data.text }]);
      } else if (data.error) {
        throw new Error(data.error);
      }
    } catch (error: any) {
      console.error("Error:", error);
      
      // デフォルトのエラーメッセージ
      let errorMessage = "エラーが発生しました。";
      
      // 安全にエラー内容を文字列化して判定
      const errorContent = error?.message || (typeof error === 'object' ? JSON.stringify(error) : String(error));
      const errorStr = errorContent.toLowerCase();
      
      // Gemini API の制限（429: Quota Exceeded）を判定してメッセージを差し替え
      if (errorStr.includes("429") || errorStr.includes("quota") || errorStr.includes("resource_exhausted")) {
        errorMessage = "申し訳ありません。ただいまアクセスが集中しており、回答を生成できません。\n\n少し待ってから再度お試しいただくか、お急ぎの場合は以下のサポート窓口までお問い合わせください。\n\n▼SPLYZAカスタマーサポート\nmotion.support@splyza.com";
      } else {
        errorMessage = `エラーが発生しました: ${error.message || "予期せぬエラー"}`;
      }
      
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: errorMessage },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderContent = (content: string) => {
    const lines = content.split('\n');
    return lines.map((line, lineIndex) => {
      const regex = /(https?:\/\/[^\s]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
      const parts = line.split(regex);

      const renderedLine = parts.map((part, i) => {
        if (part.match(/^https?:\/\//)) {
          return (
            <a key={`${lineIndex}-${i}`} href={part} target="_blank" rel="noopener noreferrer"
              style={{ color: '#18A3F2', textDecoration: 'underline', wordBreak: 'break-all', cursor: 'pointer' }}>
              {part}
            </a>
          );
        } else if (part.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)) {
          return (
            <a key={`${lineIndex}-${i}`} href={`mailto:${part}`}
              onClick={(e) => { window.location.href = `mailto:${part}`; }}
              style={{ color: '#18A3F2', textDecoration: 'underline', wordBreak: 'break-all', cursor: 'pointer', display: 'inline', position: 'relative', zIndex: 100 }}>
              {part}
            </a>
          );
        }
        return part;
      });

      return (
        <div key={lineIndex} style={{ minHeight: '1.5em' }}>
          {renderedLine.length > 0 ? renderedLine : ' '}
        </div>
      );
    });
  };

  const renderInputForm = (isCenter: boolean = false) => (
    <div style={{ 
      width: '100%', 
      maxWidth: isCenter ? '672px' : '672px', 
      margin: isCenter ? '32px auto 0 auto' : '0 auto', 
      position: 'relative' 
    }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', position: 'relative' }}>
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder="メッセージを入力..." 
          style={{ 
            width: '100%', 
            padding: '16px 50px 16px 20px', 
            backgroundColor: '#ffffff', 
            border: '2px solid #e5e7eb', 
            borderRadius: '16px', 
            fontSize: '16px', 
            outline: 'none', 
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', 
            boxSizing: 'border-box' 
          }} 
          onFocus={(e) => e.target.style.borderColor = '#18A3F2'} 
          onBlur={(e) => e.target.style.borderColor = '#e5e7eb'} 
          disabled={isLoading} 
        />
        <button 
          type="submit" 
          disabled={isLoading || !input.trim()} 
          style={{ 
            position: 'absolute', 
            right: '12px', 
            top: '50%', 
            transform: 'translateY(-50%)', 
            background: 'none', 
            border: 'none', 
            color: input.trim() ? '#18A3F2' : '#cccccc', 
            cursor: input.trim() ? 'pointer' : 'default', 
            padding: '8px' 
          }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
          </svg>
        </button>
      </form>
      {!isCenter && (
        <p style={{ fontSize: '10px', textAlign: 'center', color: '#999999', marginTop: '8px' }}>
          AIは間違いを犯すことがあります。重要な情報はヘルプセンターでご確認ください。
        </p>
      )}
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100%', backgroundColor: '#ffffff', color: '#333333', fontFamily: '"Inter", "Segoe UI", sans-serif', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: '16px', left: '16px', fontSize: '12px', color: '#999999', zIndex: 10 }}>
        SPLYZA Motion
      </div>
      <div ref={scrollRef} style={{ flex: 1, overflowY: 'auto', width: '100%', maxWidth: '768px', margin: '0 auto', padding: '80px 16px 140px 16px', boxSizing: 'border-box' }}>
        {messages.length === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', textAlign: 'center' }}>
            <div style={{ marginBottom: '24px' }}>
              <img src="/assets/motion_logo.png" alt="SPLYZA Motion Logo" style={{ width: '120px', height: 'auto', margin: '0 auto', opacity: 0.9 }} />
            </div>
            <h1 style={{ fontSize: '20px', fontWeight: '600', color: '#444444' }}>お手伝いできることはありますか？</h1>
            {renderInputForm(true)}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {messages.map((msg, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', width: '100%' }}>
                <div style={{ maxWidth: '85%', padding: '16px 20px', borderRadius: '20px', borderTopRightRadius: msg.role === 'user' ? '4px' : '20px', borderTopLeftRadius: msg.role === 'assistant' ? '4px' : '20px', backgroundColor: msg.role === 'user' ? '#18A3F2' : '#ffffff', color: msg.role === 'user' ? '#ffffff' : '#333333', fontSize: '15px', lineHeight: '1.7', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.08)', border: msg.role === 'assistant' ? '1px solid #f0f0f0' : 'none' }}>
                  {renderContent(msg.content)}
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{ padding: '12px 16px', borderRadius: '16px', borderTopLeftRadius: '0px', backgroundColor: '#f3f4f6', color: '#999999', boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
                  回答生成中...
                </div>
              </div>
            )}
          </div>
        )}
      </div>
      {messages.length > 0 && (
        <div style={{ position: 'absolute', bottom: '0', left: '0', right: '0', padding: '20px 16px 30px 16px', background: 'linear-gradient(to top, white 70%, transparent)', zIndex: 20 }}>
          {renderInputForm(false)}
        </div>
      )}
    </div>
  );
}
