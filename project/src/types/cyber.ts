export interface WifiNetwork {
  ssid: string;
  bssid: string;
  signal: number;
  security: string;
}

export interface IoTDevice {
  ip: string;
  mac: string;
  vendor: string;
}

export interface SecurityScan {
  target: string;
  vulnerabilities: Vulnerability[];
  timestamp: string;
}

export interface Vulnerability {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  recommendation: string;
}

export interface NetworkTraffic {
  timestamp: string;
  source: string;
  destination: string;
  protocol: string;
  size: number;
  flags: string[];
}

export interface SystemStats {
  cpuUsage: number;
  memoryUsage: number;
  networkSpeed: {
    download: number;
    upload: number;
  };
  activeConnections: number;
  suspiciousProcesses: string[];
}

export interface CyberState {
  flipperZeroConnected: boolean;
  wifiNetworks: WifiNetwork[];
  iotDevices: IoTDevice[];
  smartHomeDevices: Record<string, boolean>;
  cyberModeEnabled: boolean;
  voiceAssistantActive: boolean;
  systemStats: SystemStats;
  securityScanResults: {
    timestamp: string;
    findings: string[];
  };
  networkTraffic: NetworkTraffic[];
  activeThreats: {
    level: number;
    description: string;
    timestamp: string;
  }[];
  penetrationTestResults: SecurityScan[];
}

export interface CyberCommand {
  type: 'flipper' | 'wifi' | 'iot' | 'home' | 'security' | 'voice' | 'pentest' | 'defense';
  action: string;
  payload?: any;
}