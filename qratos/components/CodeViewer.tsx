import { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { GEOMETRY_PY, QUANTUM_ENGINE_PY, MAIN_PY } from '../constants';

const CodeBlock = ({ code, language }: { code: string; language: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group rounded-lg overflow-hidden border border-slate-800 bg-slate-950">
      <div className="absolute right-4 top-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <button 
          onClick={handleCopy}
          className="p-2 bg-slate-800 rounded-md text-slate-400 hover:text-white"
        >
          {copied ? <Check size={16} /> : <Copy size={16} />}
        </button>
      </div>
      <pre className="p-6 overflow-x-auto text-sm font-mono leading-relaxed">
        <code className="text-slate-300">
          {code}
        </code>
      </pre>
    </div>
  );
};

export const CodeViewer = () => {
  const [activeFile, setActiveFile] = useState<'geometry' | 'quantum' | 'main'>('main');

  const files = [
    { id: 'main', name: 'backend/main.py', content: MAIN_PY },
    { id: 'geometry', name: 'backend/geometry.py', content: GEOMETRY_PY },
    { id: 'quantum', name: 'backend/quantum_engine.py', content: QUANTUM_ENGINE_PY },
  ];

  return (
    <div className="h-full flex flex-col gap-6">
      <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Deep Research Backend</h2>
            <p className="text-slate-400">
              The production Python implementation for the Hybrid Riemannian-Quantum architecture.
            </p>
          </div>
          <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800">
            {files.map((file) => (
              <button
                key={file.id}
                onClick={() => setActiveFile(file.id as any)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  activeFile === file.id 
                    ? 'bg-slate-800 text-white' 
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {file.name}
              </button>
            ))}
          </div>
        </div>

        <CodeBlock 
          code={files.find(f => f.id === activeFile)?.content || ''} 
          language="python" 
        />
      </div>
    </div>
  );
};
