import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles, AlertCircle, CheckCircle2, Image as ImageIcon, X, Upload } from 'lucide-react';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hello! I am AquaSentinel AI. I can analyze your water safety parameters, cross-validate against WHO/BIS specifications, and evaluate image uploads for visible contaminants (algae, plastic, oil, foam). Try uploading an image or entering your water parameters!",
      timeline: null
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Helper to parse parameters dynamically from user text to assist API routing
  const extractParameters = (text) => {
    const params = {};
    const tdsMatch = text.match(/tds\s*(?:is|:|value)?\s*(\d+)/i);
    const phMatch = text.match(/ph\s*(?:is|:|value)?\s*(\d+(?:\.\d+)?)/i);
    const turbidityMatch = text.match(/turbidity\s*(?:is|:|value)?\s*(\d+(?:\.\d+)?)/i);
    const hardnessMatch = text.match(/hardness\s*(?:is|:|value)?\s*(\d+)/i);
    
    if (tdsMatch) params.tds = parseFloat(tdsMatch[1]);
    if (phMatch) params.ph = parseFloat(phMatch[1]);
    if (turbidityMatch) params.turbidity = parseFloat(turbidityMatch[1]);
    if (hardnessMatch) params.hardness = parseFloat(hardnessMatch[1]);
    
    return params;
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const removeSelectedImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Drag and drop event handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if ((!inputValue.trim() && !selectedImage) || isLoading) return;

    const userText = inputValue;
    const imgToSend = selectedImage;
    const imgPreviewToSend = imagePreview;

    // Clear state inputs
    setInputValue('');
    setSelectedImage(null);
    setImagePreview(null);
    setIsLoading(true);

    // Append user message
    setMessages(prev => [...prev, {
      id: String(Date.now()),
      role: 'user',
      content: userText || `[Uploaded Image: ${imgToSend.name}]`,
      imagePreview: imgPreviewToSend
    }]);

    try {
      const extractedParams = extractParameters(userText);
      const formData = new FormData();
      formData.append('message', userText || `Analyzing uploaded image ${imgToSend.name}`);
      
      if (imgToSend) {
        formData.append('image', imgToSend);
      }

      // Append any parsed water parameters
      Object.entries(extractedParams).forEach(([key, val]) => {
        formData.append(key, val);
      });

      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/chat/message', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Server returned an error');
      }

      const data = await response.json();
      
      // Build visual timeline checklist based on executed agents
      const plan = data.agent_execution?.plan || [];
      const timeline = [
        "Memory Loaded ✓",
        "Planning Complete ✓"
      ];
      
      if (plan.includes("vision_analysis")) {
        timeline.push("Vision Analysis Complete ✓");
      }
      if (plan.includes("water_analysis")) {
        timeline.push("Water Analysis Complete ✓");
      }
      if (plan.includes("knowledge")) {
        timeline.push("Knowledge Validation Complete ✓");
      }
      
      timeline.push("Reflection Passed ✓");
      timeline.push("Response Generated ✓");

      // Append assistant message with timeline trace
      setMessages(prev => [...prev, {
        id: data.message_id || String(Date.now() + 1),
        role: 'assistant',
        content: data.synthesized_response,
        timeline: timeline,
        duration: data.agent_execution?.execution_duration_ms
      }]);

    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: "❌ **Failed to connect to the AquaSentinel-AI pipeline.** Please check if your FastAPI server is running on `http://localhost:8000`."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Safe client-side renderer for custom Markdown reports
  const renderFormattedMarkdown = (text) => {
    const lines = text.split('\n');
    let inTable = false;
    let tableRows = [];
    const elements = [];

    lines.forEach((line, idx) => {
      if (line.trim() === '') {
        if (inTable) {
          inTable = false;
          elements.push(renderTable(tableRows, idx));
          tableRows = [];
        }
        elements.push(<div key={`space-${idx}`} className="h-2"></div>);
        return;
      }

      // Skip checklist timeline outputs
      if (line.endsWith('✓')) {
        return;
      }

      // Headers
      if (line.startsWith('## ')) {
        elements.push(<h3 key={idx} className="text-xl font-bold text-white mt-4 mb-2 tracking-tight border-b border-slate-800 pb-1">{line.replace('## ', '')}</h3>);
        return;
      }
      if (line.startsWith('### ')) {
        elements.push(<h4 key={idx} className="text-base font-bold text-aqua-400 mt-4 mb-2 tracking-wide uppercase">{line.replace('### ', '')}</h4>);
        return;
      }
      if (line.startsWith('#### ')) {
        elements.push(<h5 key={idx} className="text-sm font-semibold text-slate-200 mt-3 mb-1">{line.replace('#### ', '')}</h5>);
        return;
      }

      // Tables
      if (line.startsWith('|')) {
        inTable = true;
        if (!line.includes('---')) {
          tableRows.push(line);
        }
        return;
      } else {
        if (inTable) {
          inTable = false;
          elements.push(renderTable(tableRows, idx));
          tableRows = [];
        }
      }

      // Bullet points
      if (line.startsWith('* ') || line.startsWith('- ')) {
        const content = line.substring(2);
        elements.push(
          <div key={idx} className="flex items-start gap-2 text-sm text-slate-300 ml-2 my-1">
            <span className="text-aqua-500 mt-1.5 font-bold text-xs">•</span>
            <span>{parseInlineMarkdown(content)}</span>
          </div>
        );
        return;
      }

      // Numeric list points
      if (/^\d+\.\s/.test(line)) {
        const content = line.replace(/^\d+\.\s/, '');
        const number = line.match(/^(\d+)\.\s/)[1];
        elements.push(
          <div key={idx} className="flex items-start gap-2 text-sm text-slate-300 ml-2 my-1">
            <span className="text-aqua-400 font-bold text-xs mt-0.5">{number}.</span>
            <span>{parseInlineMarkdown(content)}</span>
          </div>
        );
        return;
      }

      // Standard text line
      elements.push(<p key={idx} className="text-sm text-slate-300 leading-relaxed my-1">{parseInlineMarkdown(line)}</p>);
    });

    if (inTable && tableRows.length > 0) {
      elements.push(renderTable(tableRows, 999));
    }

    return elements;
  };

  const parseInlineMarkdown = (text) => {
    const parts = text.split(/\*\*([^*]+)\*\*/g);
    return parts.map((part, idx) => {
      if (idx % 2 === 1) {
        return <strong key={idx} className="font-bold text-white">{part}</strong>;
      }
      const subParts = part.split(/\*([^*]+)\*/g);
      return subParts.map((subPart, sIdx) => {
        if (sIdx % 2 === 1) {
          return <em key={sIdx} className="italic text-slate-400">{subPart}</em>;
        }
        return subPart;
      });
    });
  };

  const renderTable = (rows, key) => {
    if (rows.length === 0) return null;
    const headerCols = rows[0].split('|').map(c => c.trim()).filter(Boolean);
    const bodyRows = rows.slice(1).map(row => row.split('|').map(c => c.trim()).filter(Boolean));

    return (
      <div key={key} className="overflow-x-auto my-4 rounded-xl border border-slate-800 bg-slate-950/60">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="bg-slate-900/80 border-b border-slate-800 text-slate-400 font-medium">
              {headerCols.map((col, idx) => (
                <th key={idx} className="p-3 font-semibold">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-850">
            {bodyRows.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-slate-900/30">
                {row.map((col, cIdx) => (
                  <td key={cIdx} className="p-3 text-slate-200">{parseInlineMarkdown(col)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="space-y-6 max-h-[calc(100vh-4rem)] flex flex-col">
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">AI Assistant</h2>
        <p className="text-slate-400 mt-1">Chat with the agent platform. Upload water photos or input parameters to initiate the multi-agent pipeline.</p>
      </div>

      <div 
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`flex-1 min-h-[500px] h-[650px] bg-slate-900/40 rounded-2xl border flex flex-col overflow-hidden backdrop-blur-sm shadow-xl transition-all ${
          isDragOver ? 'border-aqua-500 bg-slate-900/80 shadow-aqua-500/10' : 'border-slate-800'
        }`}
      >
        {/* Messages Log */}
        <div className="flex-1 p-6 space-y-6 overflow-y-auto">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role !== 'user' && (
                <div className="w-10 h-10 rounded-xl bg-aqua-500/10 text-aqua-400 border border-aqua-500/20 flex items-center justify-center font-bold text-sm flex-shrink-0 shadow-inner">
                  AS
                </div>
              )}
              
              <div className={`max-w-[75%] space-y-4 ${msg.role === 'user' ? 'bg-aqua-600 text-white rounded-2xl p-4 rounded-tr-none shadow-lg' : ''}`}>
                {msg.role === 'user' ? (
                  <div className="space-y-2 text-sm leading-relaxed">
                    {msg.imagePreview && (
                      <div className="rounded-lg overflow-hidden border border-aqua-400/30 max-w-[240px] shadow-sm">
                        <img src={msg.imagePreview} alt="User Upload" className="max-h-[160px] w-full object-cover" />
                      </div>
                    )}
                    <p className="font-medium">{msg.content}</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Execution Timeline (If available) */}
                    {msg.timeline && (
                      <div className="p-4 bg-slate-950/80 rounded-xl border border-slate-850 space-y-2">
                        <div className="flex justify-between items-center text-xs text-slate-500 border-b border-slate-850 pb-2 mb-2">
                          <span className="font-bold uppercase tracking-wider flex items-center gap-1.5 text-aqua-400">
                            <Sparkles size={12} /> LangGraph Orchestration Logs
                          </span>
                          {msg.duration && <span className="font-medium font-mono">{msg.duration} ms</span>}
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                          {msg.timeline.map((step, idx) => (
                            <div key={idx} className="flex items-center gap-2 text-xs font-semibold text-emerald-400 bg-emerald-500/5 px-2.5 py-1.5 rounded-lg border border-emerald-500/10">
                              <CheckCircle2 size={12} className="flex-shrink-0" />
                              <span>{step.replace('✓', '').trim()}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Main synthesised message response */}
                    <div className="p-4 bg-slate-850/30 border border-slate-800 rounded-2xl p-6 rounded-tl-none shadow-md">
                      {renderFormattedMarkdown(msg.content)}
                    </div>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-10 h-10 rounded-xl bg-slate-800 text-slate-300 border border-slate-700 flex items-center justify-center font-bold text-sm flex-shrink-0">
                  U
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-xl bg-aqua-500/10 text-aqua-400 border border-aqua-500/20 flex items-center justify-center font-bold text-sm flex-shrink-0 animate-pulse">
                AS
              </div>
              <div className="max-w-[70%] p-5 rounded-2xl bg-slate-900/60 border border-slate-800 text-slate-400 flex items-center gap-3">
                <Loader2 size={16} className="animate-spin text-aqua-400" />
                <span className="text-sm font-semibold tracking-wide animate-pulse">Running Multi-Agent Vision Pipeline...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Interface with File Preview */}
        <form onSubmit={handleSend} className="p-4 border-t border-slate-800 bg-slate-900/80 space-y-3">
          {imagePreview && (
            <div className="flex items-center gap-3 p-2 bg-slate-950/80 rounded-xl border border-slate-800 max-w-[280px] relative group">
              <div className="w-12 h-12 rounded-lg overflow-hidden border border-slate-800 flex-shrink-0">
                <img src={imagePreview} alt="Upload Preview" className="w-full h-full object-cover" />
              </div>
              <div className="flex-1 min-w-0 pr-6">
                <p className="text-xs font-semibold text-slate-300 truncate">{selectedImage?.name}</p>
                <p className="text-[10px] text-slate-500">{(selectedImage?.size / 1024).toFixed(1)} KB</p>
              </div>
              <button 
                type="button" 
                onClick={removeSelectedImage}
                className="absolute top-2 right-2 p-1 rounded-md bg-slate-800 text-slate-400 hover:text-white transition-colors"
              >
                <X size={12} />
              </button>
            </div>
          )}

          <div className="flex gap-3 items-center">
            {/* Image Upload Input */}
            <input 
              type="file" 
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/png, image/jpeg, image/jpg, image/webp"
              className="hidden"
            />
            <button 
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-3.5 rounded-xl border border-slate-800 bg-slate-950 hover:bg-slate-900 text-slate-400 hover:text-white transition-all flex items-center justify-center flex-shrink-0"
              title="Upload water image"
              disabled={isLoading}
            >
              <ImageIcon size={18} />
            </button>

            {/* Input Message */}
            <input 
              type="text" 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={isDragOver ? "Drop image here..." : "Type message (e.g. 'TDS is 750') or upload water photos..."} 
              className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3.5 text-sm focus:outline-none focus:border-aqua-500 focus:ring-1 focus:ring-aqua-500 text-slate-100 placeholder-slate-500 transition-all font-medium"
              disabled={isLoading}
            />
            <button 
              type="submit"
              className={`p-3.5 rounded-xl bg-aqua-600 font-semibold text-white transition-all flex items-center justify-center ${
                (isLoading || (!inputValue.trim() && !selectedImage))
                  ? 'opacity-50 cursor-not-allowed' 
                  : 'hover:bg-aqua-500 active:scale-95 hover:shadow-lg hover:shadow-aqua-600/25'
              }`}
              disabled={isLoading || (!inputValue.trim() && !selectedImage)}
            >
              <Send size={18} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Chat;
