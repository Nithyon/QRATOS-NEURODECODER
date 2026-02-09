

interface HumanFigureProps {
  intent: 'Left Hand' | 'Right Hand' | 'Idle';
  confidence: number;
}

export const HumanFigure = ({ intent, confidence }: HumanFigureProps) => {
  // Styles for active vs inactive limbs
  const getLimbStyle = (isActive: boolean) => {
    return isActive 
      ? "stroke-neon-blue stroke-[3px] filter drop-shadow-[0_0_8px_rgba(0,204,255,0.8)] transition-all duration-300"
      : "stroke-slate-700 stroke-[1px] transition-all duration-500";
  };

  const getJointStyle = (isActive: boolean) => {
    return isActive
      ? "fill-white filter drop-shadow-[0_0_10px_rgba(255,255,255,1)] r-2 transition-all duration-300"
      : "fill-slate-800 r-1.5 transition-all duration-500";
  };
  
  const isLeft = intent === 'Left Hand';
  const isRight = intent === 'Right Hand';

  return (
    <div className="relative w-full h-full flex items-center justify-center p-4">
      {/* Background Grid Effect */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(14,165,233,0.1)_0%,transparent_70%)]"></div>
      
      <svg viewBox="0 0 200 300" className="w-full h-full max-h-[400px]">
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {/* --- HEAD & BRAIN (Cross-Lateral Control Visualization) --- */}
        {/* Head Outline */}
        <circle cx="100" cy="30" r="14" className="fill-slate-950 stroke-slate-700 stroke-1" />
        
        {/* Left Hemisphere (Controls Right Side) */}
        <path 
          d="M 100 18 A 12 12 0 0 0 100 42" 
          className={`stroke-none transition-all duration-300 ${isRight ? 'fill-quantum-500 animate-pulse filter drop-shadow-[0_0_5px_rgba(14,165,233,0.8)]' : 'fill-slate-900 opacity-50'}`}
        />
        
        {/* Right Hemisphere (Controls Left Side) */}
        <path 
          d="M 100 18 A 12 12 0 0 1 100 42" 
          className={`stroke-none transition-all duration-300 ${isLeft ? 'fill-quantum-500 animate-pulse filter drop-shadow-[0_0_5px_rgba(14,165,233,0.8)]' : 'fill-slate-900 opacity-50'}`}
        />
        
        {/* Brain Divider */}
        <line x1="100" y1="18" x2="100" y2="42" className="stroke-slate-800 stroke-[1px]" />

        
        {/* Spine */}
        <line x1="100" y1="44" x2="100" y2="140" className="stroke-slate-600 stroke-[1px]" />
        
        {/* Hips */}
        <line x1="80" y1="140" x2="120" y2="140" className="stroke-slate-600 stroke-[1px]" />

        {/* Legs (Always Idle for this demo) */}
        <line x1="80" y1="140" x2="80" y2="220" className="stroke-slate-700 stroke-[1px]" />
        <line x1="120" y1="140" x2="120" y2="220" className="stroke-slate-700 stroke-[1px]" />
        <line x1="80" y1="220" x2="70" y2="290" className="stroke-slate-700 stroke-[1px]" />
        <line x1="120" y1="220" x2="130" y2="290" className="stroke-slate-700 stroke-[1px]" />

        {/* --- LEFT ARM (Right Hemisphere Control) --- */}
        {/* Shoulder L */}
        <line x1="100" y1="50" x2="70" y2="50" className={getLimbStyle(isLeft)} />
        {/* Upper Arm L */}
        <line x1="70" y1="50" x2="50" y2="100" className={getLimbStyle(isLeft)} />
        {/* Forearm L */}
        <line x1="50" y1="100" x2="30" y2="130" className={getLimbStyle(isLeft)} />
        
        {/* Joints L */}
        <circle cx="70" cy="50" r="2" className={getJointStyle(isLeft)} />
        <circle cx="50" cy="100" r="2" className={getJointStyle(isLeft)} />
        <circle cx="30" cy="130" r="3" className={getJointStyle(isLeft)} />

        {/* --- RIGHT ARM (Left Hemisphere Control) --- */}
        
        {/* Shoulder R */}
        <line x1="100" y1="50" x2="130" y2="50" className={getLimbStyle(isRight)} />
        {/* Upper Arm R */}
        <line x1="130" y1="50" x2="150" y2="100" className={getLimbStyle(isRight)} />
        {/* Forearm R */}
        <line x1="150" y1="100" x2="170" y2="130" className={getLimbStyle(isRight)} />
        
        {/* Joints R */}
        <circle cx="130" cy="50" r="2" className={getJointStyle(isRight)} />
        <circle cx="150" cy="100" r="2" className={getJointStyle(isRight)} />
        <circle cx="170" cy="130" r="3" className={getJointStyle(isRight)} />

        {/* --- DECORATIVE RINGS --- */}
        {isLeft && (
             <circle cx="30" cy="130" r="10" className="stroke-neon-blue stroke-1 fill-none animate-ping opacity-75" />
        )}
        {isRight && (
             <circle cx="170" cy="130" r="10" className="stroke-neon-blue stroke-1 fill-none animate-ping opacity-75" />
        )}

      </svg>
      
      {/* Label Overlay */}
      <div className="absolute bottom-4 left-0 right-0 text-center">
         <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500 mb-1">Neuromotor Mirror</div>
         <div className={`font-mono text-sm font-bold transition-colors duration-300 ${intent === 'Idle' ? 'text-slate-600' : 'text-white'}`}>
            {intent === 'Idle' ? 'NO SIGNAL' : `${intent.toUpperCase()} DETECTED`}
         </div>
      </div>
    </div>
  );
};