import React, { useState, useEffect, useRef } from 'react';

const CantoneseeTutor = () => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [taskCompleted, setTaskCompleted] = useState(false);
  const messagesEndRef = useRef(null);

  const API_BASE = 'http://localhost:5000/api/dmapi';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startNewSession = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/start-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSessionId(data.session_id);
        setMessages([{
          speaker: 'claude',
          message: data.message,
          timestamp: new Date().toLocaleTimeString()
        }]);
        setTaskCompleted(false);
      } else {
        console.error('Error starting session:', data.error);
      }
    } catch (error) {
      console.error('Network error:', error);
    }
    setIsLoading(false);
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !sessionId || isLoading) return;

    const userMessage = {
      speaker: 'student',
      message: currentMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: currentMessage
        })
      });

      const data = await response.json();

      if (response.ok) {
        const claudeMessage = {
          speaker: 'claude',
          message: data.message,
          timestamp: new Date().toLocaleTimeString()
        };

        setMessages(prev => [...prev, claudeMessage]);
        
        if (data.task_completed) {
          setTaskCompleted(true);
        }
      } else {
        console.error('Error sending message:', data.error);
      }
    } catch (error) {
      console.error('Network error:', error);
    }
    setIsLoading(false);
  };

  const completeTask = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${API_BASE}/complete-task`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });

      if (response.ok) {
        setSessionId(null);
        setMessages([]);
        setTaskCompleted(false);
        // Auto-start next task
        setTimeout(startNewSession, 1000);
      }
    } catch (error) {
      console.error('Error completing task:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="cantonese-tutor" style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <div className="tutor-header" style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h2>🈶️ 粵語學習系統</h2>
        <p>Cantonese Learning System - Direct Method</p>
      </div>

      {!sessionId ? (
        <div className="start-section" style={{ textAlign: 'center', padding: '40px' }}>
          <button 
            onClick={startNewSession}
            disabled={isLoading}
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            {isLoading ? '準備中...' : '開始新任務'}
          </button>
        </div>
      ) : (
        <>
          <div 
            className="messages-container" 
            style={{
              height: '400px',
              overflowY: 'auto',
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '15px',
              marginBottom: '20px',
              backgroundColor: '#f9f9f9'
            }}
          >
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`message ${msg.speaker}`}
                style={{
                  marginBottom: '15px',
                  padding: '10px',
                  borderRadius: '8px',
                  backgroundColor: msg.speaker === 'claude' ? '#e3f2fd' : '#f1f8e9',
                  border: `1px solid ${msg.speaker === 'claude' ? '#bbdefb' : '#c8e6c9'}`
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  {msg.speaker === 'claude' ? '老師' : '你'} 
                  <span style={{ fontSize: '12px', color: '#666', marginLeft: '10px' }}>
                    {msg.timestamp}
                  </span>
                </div>
                <div style={{ fontSize: '16px', lineHeight: '1.5' }}>
                  {msg.message}
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{ textAlign: 'center', padding: '10px', color: '#666' }}>
                老師正在回應...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-section">
            <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
              <textarea
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="用粵語回應..."
                disabled={isLoading}
                style={{
                  flex: 1,
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  fontSize: '16px',
                  resize: 'none',
                  height: '60px'
                }}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !currentMessage.trim()}
                style={{
                  padding: '12px 20px',
                  backgroundColor: '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                發送
              </button>
            </div>

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
              {taskCompleted && (
                <button
                  onClick={completeTask}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#ffc107',
                    color: 'black',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  完成任務 & 下一個
                </button>
              )}
              
              <button
                onClick={startNewSession}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
              >
                新任務
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CantoneseeTutor;
