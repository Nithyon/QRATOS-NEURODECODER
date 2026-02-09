import { useEffect, useState, useRef } from 'react';
import { Activity, Brain, Radio, Server, PlayCircle, StopCircle, Cpu, RefreshCw, BoxSelect, Target, Database, UploadCloud, Loader2 } from 'lucide-react';
import { BCIData } from '../types';
import { bciService } from '../services/bciSimulator';
import { MetricsCard } from './MetricsCard';
import { EEGVisualizer } from './EEGVisualizer';
import { HumanFigure } from './HumanFigure';

export const Dashboard = () => {
  const [data, setData] = useState<BCIData | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [manualMode, setManualMode] = useState(false);
  const [calibrationProgress, setCalibrationProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let unsubscribe: () => void;
    if (isRunning) {
      unsubscribe = bciService.connect((newData) => {
        setData(newData);
      });
    }
    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, [isRunning]);

  const handleIntentClick = (intent: 'Left Hand' | 'Right Hand' | 'Idle') => {
    if (!isRunning) return;
    setManualMode(true);
    bciService.setIntent(intent);
  };

  const handleAutoMode = () => {
    if (!isRunning) return;
    setManualMode(false);
    bciService.setAutoMode();
  };

  const handleCalibrate = () => {
    if (!isRunning) return;
    setCalibrationProgress(10);
    
    const interval = setInterval(() => {
        setCalibrationProgress(prev => {
            if (prev >= 100) {
                clearInterval(interval);
                return 0;
            }
            return prev + 5;
        });
    }, 100);
  };

  const toggleSimulation = () => {
    if (isRunning) {
      bciService.disconnect(() => {});
      setIsRunning(false);
    } else {
      setIsRunning(true);
      setManualMode(false);
    }
  };

  const handleUploadClick = () => {
    if (fileInputRef.current) {
        fileInputRef.current.click();
    }
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/upload-dataset', {
            method: 'POST',
            body: formData,
        });
        const result = await response.json();
        if (result.status === 'success') {
            alert(`Dataset Uploaded Successfully! ${result.message}`);
        } else {
            alert(`Upload Failed: ${result.message}`);
        }
    } catch (error) {
        console.error("Upload error:", error);
        alert("Failed to connect to backend upload service.");
    } finally {
        setIsUploading(false);
        // Reset input
        if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="h-full flex flex-col gap-6">
      {/* Control Bar */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-center bg-slate-900/40 p-4 rounded-xl border border-slate-800">
        <div className="flex items-center gap-4">
          <button
            onClick={toggleSimulation}
            className={`flex items-center gap-2 px-6 py-2 rounded-full font-bold transition-all ${
              isRunning 
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/50 hover:bg-rose-500/20' 
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/50 hover:bg-emerald-500/20'
            }`}
          >
            {isRunning ? <><StopCircle size={18} /> STOP STREAM</> : <><PlayCircle size={18} /> START STREAM</>}
          </button>
          
          <div className="h-8 w-px bg-slate-700 mx-2 hidden md:block"></div>
          
          <div className="flex gap-2 bg-slate-950 p-1 rounded-lg border border-slate-800">
            <button
              onClick={handleAutoMode}
              disabled={!isRunning}
              className={`px-4 py-1.5 rounded-md text-sm font-medium flex items-center gap-2 transition-all ${
                !manualMode 
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/50' 
                  : 'text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-50'
              }`}
            >
              <RefreshCw size={14} className={!manualMode && isRunning ? "animate-spin-slow" : ""} />
              Auto Seq
            </button>

            {['Idle', 'Left Hand', 'Right Hand'].map((intent) => (
              <button
                key={intent}
                onClick={() => handleIntentClick(intent as any)}
                disabled={!isRunning}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                  manualMode && data?.intent === intent
                    ? 'bg-quantum-600 text-white shadow-lg shadow-quantum-900/50' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-50'
                }`}
              >
                {intent}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-4">
             {/* Data Source Indicator */}
             <div className={`flex items-center gap-2 px-3 py-1 rounded border text-xs font-mono uppercase ${
                 data?.dataSource?.includes('Real') || data?.dataSource?.includes('Uploaded')
                 ? 'bg-blue-500/10 border-blue-500/50 text-blue-400'
                 : 'bg-slate-800 border-slate-700 text-slate-500'
             }`}>
                <Database size={12} />
                {data?.dataSource ? `SRC: ${data.dataSource}` : 'SRC: STANDBY'}
             </div>

             {/* Upload Button */}
             <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                className="hidden" 
                multiple
                // @ts-ignore
                webkitdirectory="" 
                directory="" 
             />
             <button
                onClick={handleUploadClick}
                disabled={isUploading}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono border border-slate-700 disabled:opacity-50 transition-colors"
                title="Upload CSV Folder"
             >
                {isUploading ? <Loader2 size={12} className="animate-spin" /> : <UploadCloud size={14} />}
                UPLOAD DATA
             </button>

             {/* Calibration Button */}
             <button 
                onClick={handleCalibrate}
                disabled={!isRunning || calibrationProgress > 0}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono border border-slate-700 disabled:opacity-50"
             >
                <Target size={14} />
                {calibrationProgress > 0 ? `CALIBRATING ${calibrationProgress}%` : "RE-CALIBRATE KERNEL"}
             </button>

             <div className="flex items-center gap-3 text-sm text-slate-400 font-mono pl-4 border-l border-slate-800">
                <Server size={14} />
                <span className={isRunning ? "text-emerald-400" : "text-rose-400"}>
                    {isRunning ? 'ONLINE' : 'OFFLINE'}
                </span>
             </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        
        {/* Left Column: Visuals */}
        <div className="lg:col-span-2 flex flex-col gap-6">
           
           {/* Top: EEG Chart */}
           <div className="h-1/3 bg-slate-900/30 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-sm relative min-h-[160px]">
             <div className="absolute top-4 right-4 z-10 flex gap-2">
                <div className="bg-black/50 backdrop-blur-md px-3 py-1 rounded-full border border-slate-700 text-xs font-mono text-quantum-400 flex items-center gap-2">
                    <Cpu size={12} />
                    KIPU DAQC KERNEL ACTIVE
                </div>
             </div>
             <EEGVisualizer active={isRunning} intent={data?.intent || 'Idle'} />
           </div>
           
           {/* Bottom: Split View (Decoder & Body) */}
           <div className="h-2/3 grid grid-cols-1 md:grid-cols-2 gap-6 min-h-0">
              
              {/* Intent Banner Box */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-quantum-900/10 to-transparent"></div>
                  
                  <div>
                    <h3 className="text-slate-400 text-sm uppercase tracking-wider mb-2 flex items-center gap-2">
                        Real-time Decoder
                        {isRunning && <span className="inline-block w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>}
                    </h3>
                    <div className="text-4xl font-black text-white tracking-tight leading-tight">
                      {data?.intent || "WAITING..."}
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="h-px w-full bg-slate-800"></div>
                    <div className="flex justify-between items-end">
                       <div>
                         <div className="text-xs text-slate-500 uppercase tracking-widest mb-1">Confidence</div>
                         <div className="text-5xl font-mono font-bold text-quantum-400">
                           {data ? (data.confidence * 100).toFixed(0) : 0}<span className="text-2xl text-quantum-600">%</span>
                         </div>
                       </div>
                    </div>
                  </div>
              </div>

              {/* Human Figure Visualizer */}
              <div className="bg-slate-950/80 border border-slate-800 rounded-2xl overflow-hidden relative shadow-inner shadow-black">
                 <HumanFigure intent={data?.intent || 'Idle'} confidence={data?.confidence || 0} />
              </div>

           </div>
        </div>

        {/* Right Column: Metrics */}
        <div className="flex flex-col gap-4">
          <MetricsCard 
            label="Riemannian Manifold Energy"
            value={data?.riemannMetric.toFixed(2) || "0.00"}
            unit="tr(Σ)"
            trend={data?.intent !== 'Idle' ? 'down' : 'up'} 
            icon={<Activity size={18} />}
            color="text-neon-purple"
          />
          <MetricsCard 
            label="Kipu Compression Ratio"
            value={data?.compressionRatio ? `${data.compressionRatio.toFixed(1)}x` : "0.0x"}
            unit="DAQC"
            icon={<BoxSelect size={18} />}
            color="text-quantum-400"
            trend="up"
          />
          
          <div className="grid grid-cols-2 gap-4">
            <MetricsCard 
                label="Signal Noise"
                value={data?.noiseLevel.toFixed(1) || "0.0"}
                unit="dB"
                trend="down"
                icon={<Radio size={18} />}
            />
            <MetricsCard 
                label="Entropy"
                value={data?.entropy.toFixed(2) || "0.00"}
                unit="bits"
                icon={<Brain size={18} />}
                color="text-neon-green"
            />
          </div>
          
        </div>
      </div>
    </div>
  );
};