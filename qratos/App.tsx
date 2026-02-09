import { useState } from 'react';
import { LayoutDashboard, FileCode, Cpu, Github, Share2 } from 'lucide-react';
import { Dashboard } from './components/Dashboard';
import { CodeViewer } from './components/CodeViewer';

const App = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'code'>('dashboard');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 selection:bg-quantum-500/30">
      {/* Navbar */}
      <nav className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-tr from-quantum-500 to-neon-purple rounded-lg flex items-center justify-center shadow-lg shadow-quantum-500/20">
              <Cpu className="text-white" size={20} />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight text-white">Hybrid Q</h1>
              <div className="text-[10px] text-quantum-400 font-mono tracking-wider uppercase">Team Qratos • Quantathon 3.0</div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex bg-slate-900 rounded-full p-1 border border-slate-800">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                  activeTab === 'dashboard'
                    ? 'bg-slate-800 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <LayoutDashboard size={16} />
                Live Mission HUD
              </button>
              <button
                onClick={() => setActiveTab('code')}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                  activeTab === 'code'
                    ? 'bg-slate-800 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <FileCode size={16} />
                Backend Source
              </button>
            </div>
            
            <div className="h-6 w-px bg-slate-800"></div>

            <div className="flex gap-3">
               <button className="text-slate-400 hover:text-white transition-colors">
                 <Github size={20} />
               </button>
               <button className="text-slate-400 hover:text-white transition-colors">
                 <Share2 size={20} />
               </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 h-[calc(100vh-4rem)]">
        {activeTab === 'dashboard' ? (
          <Dashboard />
        ) : (
          <CodeViewer />
        )}
      </main>
    </div>
  );
};

export default App;
