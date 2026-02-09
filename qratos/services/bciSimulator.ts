import { BCIData } from '../types';

export class BCIService {
  private intervalId: number | null = null;
  private ws: WebSocket | null = null;
  private currentIntent: 'Left Hand' | 'Right Hand' | 'Idle' = 'Idle';
  private subscribers: ((data: BCIData) => void)[] = [];
  
  // Simulation state
  private timeStep = 0;

  public connect(callback: (data: BCIData) => void) {
    this.subscribers.push(callback);
    
    // Attempt to connect to the Python Quantum Backend
    try {
      this.ws = new WebSocket('ws://127.0.0.1:8000/ws/brain-stream');
      
      this.ws.onopen = () => {
        console.log('[Hybrid Q] Uplink established with Quantum Backend.');
        // If we have a pending intent, send it immediately
        this.sendIntentToBackend(this.currentIntent);
        
        // Ensure simulation is stopped if backend is alive
        if (this.intervalId) {
          window.clearInterval(this.intervalId);
          this.intervalId = null;
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Inject local timestamp for UI synchronization
          const packet: BCIData = {
            ...data,
            timestamp: Date.now(),
            dataSource: data.dataSource || 'Real Dataset'
          };
          this.subscribers.forEach(cb => cb(packet));
        } catch (e) {
          console.error('Failed to parse quantum telemetry:', e);
        }
      };

      this.ws.onerror = (error) => {
        console.warn('[Hybrid Q] Backend unreachable. Engaging onboard simulation.', error);
        if (!this.intervalId) {
          this.startSimulation();
        }
      };

      this.ws.onclose = () => {
        console.log('[Hybrid Q] Uplink closed.');
        this.ws = null;
      };

    } catch (e) {
      console.warn('[Hybrid Q] WebSocket init failed, starting simulation.');
      this.startSimulation();
    }

    return () => this.disconnect(callback);
  }

  public disconnect(callback: (data: BCIData) => void) {
    this.subscribers = this.subscribers.filter(cb => cb !== callback);
    
    if (this.subscribers.length === 0) {
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }
      if (this.intervalId) {
        window.clearInterval(this.intervalId);
        this.intervalId = null;
      }
    }
  }

  public setIntent(intent: 'Left Hand' | 'Right Hand' | 'Idle') {
    this.currentIntent = intent;
    this.sendIntentToBackend(intent);
  }

  public setAutoMode() {
    this.currentIntent = 'Idle';
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ intent: 'Auto' }));
    }
  }

  private sendIntentToBackend(intent: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ intent: intent }));
    }
  }

  private startSimulation() {
    if (this.intervalId) return; // Already running
    
    console.log('[Hybrid Q] Simulation Engine Active');
    this.intervalId = window.setInterval(() => {
      const data = this.generatePacket();
      this.subscribers.forEach(cb => cb(data));
      this.timeStep++;
    }, 100); // 10Hz update rate
  }

  private generatePacket(): BCIData {
    // Simulate metrics based on intent
    let baseConfidence = 0.5;
    let baseMetric = 10;
    
    if (this.currentIntent !== 'Idle') {
      baseConfidence = 0.85; // Higher confidence when active
      baseMetric = 25; // Higher complexity
    }

    // Add noise and oscillation
    const noise = Math.random() * 0.1;
    const oscillation = Math.sin(this.timeStep * 0.1) * 0.05;
    
    const confidence = Math.min(0.99, Math.max(0.1, baseConfidence + noise + oscillation));
    
    return {
      intent: this.currentIntent,
      confidence: parseFloat(confidence.toFixed(2)),
      activity: parseFloat((Math.random() * 0.5 + 0.3).toFixed(2)),
      riemannMetric: parseFloat((baseMetric + Math.random() * 5).toFixed(2)),
      entropy: parseFloat((3.0 + Math.random()).toFixed(1)),
      noiseLevel: parseFloat((Math.abs(Math.sin(this.timeStep * 0.05)) * 10).toFixed(1)),
      compressionRatio: parseFloat((4.5 + Math.random() * 0.2).toFixed(2)), // Simulated Kipu Stats
      timestamp: Date.now(),
      dataSource: 'Synthetic'
    };
  }
}

export const bciService = new BCIService();