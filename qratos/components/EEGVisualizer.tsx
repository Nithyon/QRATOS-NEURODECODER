import { useEffect, useState, useRef } from 'react';
import { LineChart, Line, ResponsiveContainer, YAxis, XAxis } from 'recharts';

interface EEGVisualizerProps {
  active: boolean;
  intent: string;
}

export const EEGVisualizer = ({ active, intent }: EEGVisualizerProps) => {
  const [data, setData] = useState<{ time: number; ch1: number; ch2: number; ch3: number; ch4: number }[]>([]);
  const frameRef = useRef(0);

  useEffect(() => {
    // Initialize data
    const initialData = Array.from({ length: 50 }, (_, i) => ({
      time: i,
      ch1: 0, ch2: 0, ch3: 0, ch4: 0
    }));
    setData(initialData);
  }, []);

  useEffect(() => {
    if (!active) return;

    const interval = setInterval(() => {
      setData(prevData => {
        const newData = [...prevData.slice(1)];
        frameRef.current += 1;
        
        // t is time factor. 
        // We use a specific multiplier to simulate ~10Hz Mu Rhythm speed relative to frame rate
        const t = frameRef.current * 0.15;

        // --- SCIENTIFIC LOGIC ---
        // IDLE = High Amplitude Synchronized Waves (Mu Rhythm ~10Hz)
        // ACTIVE = Low Amplitude Desynchronized Waves (ERD)
        
        // Base Amplitude (Idle state)
        let ampL = 35; // C3
        let ampR = 35; // C4

        // Apply ERD (Suppression) based on intent
        // Note: Contralateral suppression (Left Hand -> Right Brain ERD)
        if (intent === 'Left Hand') {
            ampR = 10; // C4 Desynchronizes (Amplitude drops)
        } else if (intent === 'Right Hand') {
            ampL = 10; // C3 Desynchronizes (Amplitude drops)
        }

        const noise = () => (Math.random() - 0.5) * 8;
        
        // C3 (Left Motor) - Mu Rhythm simulation
        // The Math.sin represents the synchronized firing.
        const ch1 = (Math.sin(t) + Math.sin(t * 2.1) * 0.2) * ampL + noise(); 
        
        // C4 (Right Motor) - Mu Rhythm simulation
        const ch2 = (Math.sin(t + 1) + Math.sin(t * 2.1 + 1) * 0.2) * ampR + noise();
        
        // Pz (Parietal) - Alpha Hub (Always high alpha in relaxed state)
        const ch3 = (Math.sin(t * 0.9) * 30) + noise();
        
        // Fz (Frontal) - Executive control (More noise/beta, less alpha)
        const ch4 = (Math.sin(t * 0.4) * 10) + (Math.random() * 10) - 5;

        newData.push({
          time: frameRef.current,
          ch1, ch2, ch3, ch4
        });
        return newData;
      });
    }, 40); // 25 FPS

    return () => clearInterval(interval);
  }, [active, intent]);

  return (
    <div className="h-full w-full flex flex-col gap-2 p-4 bg-black/20 rounded-lg relative">
      <div className="text-xs font-mono text-slate-500 mb-2 flex justify-between items-center">
        <span>RAW EEG STREAM (10-20 SYSTEM)</span>
        <div className="flex items-center gap-2">
            {intent === 'Idle' && active && (
                <span className="text-[10px] text-quantum-400 bg-quantum-900/30 px-2 py-0.5 rounded border border-quantum-500/30">
                    DETECTING MU RHYTHM (IDLE)
                </span>
            )}
            <span className={`w-2 h-2 rounded-full ${active ? 'bg-quantum-400 animate-pulse' : 'bg-slate-700'}`}></span>
        </div>
      </div>
      
      {[
        { id: 'ch1', name: 'C3 (Left Motor)', color: '#00ccff' },
        { id: 'ch2', name: 'C4 (Right Motor)', color: '#b026ff' },
        { id: 'ch3', name: 'Pz (Parietal)', color: '#00ff9d' },
        { id: 'ch4', name: 'Fz (Frontal)', color: '#f59e0b' },
      ].map((channel) => (
        <div key={channel.id} className="flex-1 min-h-0 relative border-b border-slate-800/50 group">
           <div className="absolute left-2 top-1 text-[10px] text-slate-400 font-mono z-10 flex gap-2">
              <span className="font-bold text-slate-300">{channel.name}</span>
              {/* Contextual help for the user */}
              {intent === 'Idle' && (channel.id === 'ch1' || channel.id === 'ch2') && active && (
                 <span className="hidden group-hover:inline text-[9px] text-emerald-400 bg-black/80 px-1 rounded">
                    Synch (High Amp)
                 </span>
              )}
              {intent === 'Right Hand' && channel.id === 'ch1' && active && (
                 <span className="text-[9px] text-rose-400 bg-black/80 px-1 rounded animate-pulse">
                    ERD: Desynchronized
                 </span>
              )}
              {intent === 'Left Hand' && channel.id === 'ch2' && active && (
                 <span className="text-[9px] text-rose-400 bg-black/80 px-1 rounded animate-pulse">
                    ERD: Desynchronized
                 </span>
              )}
           </div>
           <ResponsiveContainer width="100%" height="100%">
             <LineChart data={data}>
               <YAxis domain={[-80, 80]} hide />
               <XAxis dataKey="time" hide />
               <Line 
                 type="monotone" 
                 dataKey={channel.id} 
                 stroke={channel.color} 
                 strokeWidth={1.5} 
                 dot={false} 
                 isAnimationActive={false} 
               />
             </LineChart>
           </ResponsiveContainer>
        </div>
      ))}
    </div>
  );
};