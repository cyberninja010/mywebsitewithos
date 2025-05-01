import { io } from 'socket.io-client';
import type { CyberState, CyberCommand } from '../types/cyber';

export const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to cyber assistant server');
});

socket.on('error', (error) => {
  console.error('Socket error:', error);
});

export const sendCommand = (command: CyberCommand) => {
  socket.emit('command', command);
};

export const subscribeToState = (callback: (state: CyberState) => void) => {
  socket.on('stateUpdate', callback);
  return () => {
    socket.off('stateUpdate', callback);
  };
};

export const startPenetrationTest = (target: string, options: any) => {
  socket.emit('pentest', { target, options });
};

export const activateDefense = (level: number) => {
  socket.emit('defense', { level });
};

export const monitorTraffic = (enabled: boolean) => {
  socket.emit('monitor', { enabled });
};