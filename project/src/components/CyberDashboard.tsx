import React, { useState, useEffect } from 'react';
import { Wifi, Cpu, Home, Shield, Zap, Mic, Activity, Network, Lock, AlertTriangle, Target, Eye } from 'lucide-react';
import type { CyberState, WifiNetwork, IoTDevice, SecurityScan, NetworkTraffic } from '../types/cyber';
import { socket, sendCommand, startPenetrationTest, activateDefense, monitorTraffic } from '../lib/socket';

export function CyberDashboard() {
  const [state, setState] = useState<CyberState>({
    flipperZeroConnected: false,
    wifiNetworks: [],
    iotDevices: [],
    smartHomeDevices: {},
    cyberModeEnabled: false,
    voiceAssistantActive: false,
    systemStats: {
      cpuUsage: 0,
      memoryUsage: 0,
      networkSpeed: {
        download: 0,
        upload: 0
      },
      activeConnections: 0,
      suspiciousProcesses: []
    },
    securityScanResults: {
      timestamp: '',
      findings: []
    },
    networkTraffic: [],
    activeThreats: [],
    penetrationTestResults: []
  });

  useEffect(() => {
    socket.on('stateUpdate', (newState: CyberState) => {
      setState(newState);
    });

    return () => {
      socket.off('stateUpdate');
    };
  }, []);

  const toggleCyberMode = () => {
    sendCommand({ type: 'security', action: 'toggleCyberMode' });
  };

  const toggleVoiceAssistant = () => {
    sendCommand({ type: 'voice', action: 'toggle' });
  };

  const connectFlipperZero = () => {
    sendCommand({ type: 'flipper', action: 'connect' });
  };

  const scanNetworks = () => {
    sendCommand({ type: 'wifi', action: 'scan' });
  };

  const runSecurityScan = () => {
    sendCommand({ type: 'security', action: 'scan' });
  };

  const startPenTest = (target: string) => {
    startPenetrationTest(target, { type: 'full' });
  };

  const toggleDefense = (level: number) => {
    activateDefense(level);
  };

  const toggleMonitoring = () => {
    monitorTraffic(!state.cyberModeEnabled);
  };

  const toggleLight = (deviceId: string) => {
    sendCommand({ 
      type: 'home',
      action: 'light',
      payload: {
        device: deviceId,
        state: !state.smartHomeDevices[deviceId]
      }
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Cyber Security Dashboard</h1>
          <div className="flex gap-4">
            <button
              onClick={toggleCyberMode}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                state.cyberModeEnabled ? 'bg-red-500' : 'bg-gray-500'
              } text-white`}
            >
              <Shield size={20} />
              Cyber Defense Mode
            </button>
            <button
              onClick={toggleMonitoring}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                state.cyberModeEnabled ? 'bg-blue-500' : 'bg-gray-500'
              } text-white`}
            >
              <Eye size={20} />
              Network Monitor
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Threat Monitor */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Active Threats</h2>
              <AlertTriangle className={state.activeThreats.length > 0 ? "text-red-500" : "text-gray-400"} />
            </div>
            <div className="space-y-2">
              {state.activeThreats.map((threat, index) => (
                <div key={index} className="p-2 bg-red-50 text-red-700 rounded">
                  <div className="font-medium">Threat Level: {threat.level}</div>
                  <div className="text-sm">{threat.description}</div>
                  <div className="text-xs text-gray-500">{threat.timestamp}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Network Traffic Analysis */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Network Traffic</h2>
              <Activity />
            </div>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {state.networkTraffic.map((traffic, index) => (
                <div key={index} className="text-sm p-2 border-b">
                  <div className="flex justify-between">
                    <span>{traffic.source} → {traffic.destination}</span>
                    <span className="text-gray-500">{traffic.protocol}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Size: {traffic.size}b | Flags: {traffic.flags.join(', ')}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Penetration Testing */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Penetration Tests</h2>
              <Target />
            </div>
            <button
              onClick={() => startPenTest('localhost')}
              className="w-full bg-purple-500 text-white py-2 rounded hover:bg-purple-600 mb-4"
            >
              Start New Test
            </button>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {state.penetrationTestResults.map((scan, index) => (
                <div key={index} className="p-2 bg-gray-50 rounded">
                  <div className="font-medium">{scan.target}</div>
                  <div className="text-sm text-gray-500">{scan.timestamp}</div>
                  <div className="mt-1">
                    {scan.vulnerabilities.map((vuln, vIndex) => (
                      <div key={vIndex} className={`text-sm p-1 mt-1 rounded ${
                        vuln.severity === 'critical' ? 'bg-red-100 text-red-700' :
                        vuln.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                        vuln.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {vuln.type}: {vuln.description}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* System Stats */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">System Stats</h2>
              <Cpu className="text-blue-500" />
            </div>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>CPU Usage</span>
                <span className="font-mono">{state.systemStats.cpuUsage}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Memory Usage</span>
                <span className="font-mono">{state.systemStats.memoryUsage}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Network Speed</span>
                <div className="text-right">
                  <div>↓ {state.systemStats.networkSpeed.download} Mbps</div>
                  <div>↑ {state.systemStats.networkSpeed.upload} Mbps</div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span>Active Connections</span>
                <span className="font-mono">{state.systemStats.activeConnections}</span>
              </div>
              {state.systemStats.suspiciousProcesses.length > 0 && (
                <div className="mt-2">
                  <div className="text-red-500 font-medium">Suspicious Processes:</div>
                  <div className="text-sm space-y-1">
                    {state.systemStats.suspiciousProcesses.map((process, index) => (
                      <div key={index} className="bg-red-50 p-1 rounded">
                        {process}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Flipper Zero Status */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Flipper Zero</h2>
              <Zap className={state.flipperZeroConnected ? "text-green-500" : "text-gray-400"} />
            </div>
            <button
              onClick={connectFlipperZero}
              className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
            >
              {state.flipperZeroConnected ? "Connected" : "Connect Flipper Zero"}
            </button>
          </div>

          {/* WiFi Networks */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">WiFi Networks</h2>
              <Wifi />
            </div>
            <button
              onClick={scanNetworks}
              className="mb-4 bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
            >
              Scan Networks
            </button>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {state.wifiNetworks.map((network) => (
                <div key={network.bssid} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                  <div>
                    <div className="font-medium">{network.ssid}</div>
                    <div className="text-sm text-gray-500">{network.bssid}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {network.security}
                    </span>
                    <span className="text-sm text-gray-500">
                      {network.signal}dBm
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* IoT Devices */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">IoT Devices</h2>
              <Network />
            </div>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {state.iotDevices.map((device) => (
                <div key={device.mac} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                  <div>
                    <div className="font-medium">{device.vendor}</div>
                    <div className="text-sm text-gray-500">{device.mac}</div>
                  </div>
                  <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                    {device.ip}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Smart Home Controls */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Smart Home</h2>
              <Home />
            </div>
            <div className="space-y-4">
              {Object.entries(state.smartHomeDevices).map(([id, isOn]) => (
                <button
                  key={id}
                  onClick={() => toggleLight(id)}
                  className={`w-full py-2 px-4 rounded flex items-center justify-between ${
                    isOn ? 'bg-green-500' : 'bg-gray-300'
                  } text-white`}
                >
                  <span>{id}</span>
                  <span>{isOn ? 'ON' : 'OFF'}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Security Monitor */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Security</h2>
              <Shield />
            </div>
            <button
              onClick={runSecurityScan}
              className="w-full bg-red-500 text-white py-2 rounded hover:bg-red-600 mb-4"
            >
              Run Security Scan
            </button>
            {state.securityScanResults.findings.length > 0 && (
              <div className="mt-4">
                <div className="text-sm text-gray-500 mb-2">
                  Last scan: {state.securityScanResults.timestamp}
                </div>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {state.securityScanResults.findings.map((finding, index) => (
                    <div key={index} className="text-sm p-2 bg-red-50 text-red-700 rounded">
                      {finding}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}