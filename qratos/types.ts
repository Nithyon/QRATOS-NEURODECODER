export interface BCIData {
  intent: 'Left Hand' | 'Right Hand' | 'Idle';
  confidence: number;
  activity: number;
  riemannMetric: number;
  entropy: number;
  noiseLevel: number;
  compressionRatio: number;
  timestamp: number;
  dataSource: string;
}

export interface EEGChannel {
  name: string;
  data: { time: number; value: number }[];
  color: string;
}

