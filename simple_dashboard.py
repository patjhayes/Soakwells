#!/usr/bin/env python3
"""
Simple Web-based Soakwell Dashboard
Alternative to Streamlit using basic HTML/Python server
"""

import http.server
import socketserver
import json
import urllib.parse
import math
import os

class SoakwellHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_dashboard_html()
        elif self.path.startswith('/api/analyze'):
            self.handle_analysis()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/upload':
            self.handle_file_upload()
        else:
            self.send_error(404)
    
    def send_dashboard_html(self):
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>🌧️ Soakwell Design Dashboard</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .controls { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .results { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .input-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 200px; padding: 5px; border: 1px solid #ddd; border-radius: 3px; }
        button { background: #0066cc; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0052a3; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #0066cc; }
        .metric-value { font-size: 24px; font-weight: bold; color: #0066cc; }
        .metric-label { font-size: 14px; color: #666; }
        .file-upload { border: 2px dashed #ddd; padding: 20px; text-align: center; border-radius: 5px; margin-bottom: 15px; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌧️ Soakwell Design Dashboard</h1>
            <p>Interactive tool for analyzing soakwell performance with storm hydrograph data</p>
        </div>
        
        <div class="controls">
            <h2>📁 Upload Storm Data</h2>
            <div class="file-upload">
                <input type="file" id="fileInput" accept=".ts1" multiple>
                <p>Drop .ts1 files here or click to browse</p>
            </div>
            
            <h2>⚙️ Soakwell Parameters</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
                <div>
                    <h3>Geometry</h3>
                    <div class="input-group">
                        <label for="diameter">Diameter (m):</label>
                        <input type="number" id="diameter" min="1" max="8" step="0.1" value="3.0">
                    </div>
                    <div class="input-group">
                        <label for="height">Height (m):</label>
                        <input type="number" id="height" min="1" max="5" step="0.1" value="3.0">
                    </div>
                </div>
                
                <div>
                    <h3>Soil Properties</h3>
                    <div class="input-group">
                        <label for="soilType">Soil Type:</label>
                        <select id="soilType" onchange="updateSoilProperties()">
                            <option value="medium">Medium Soil</option>
                            <option value="sandy">Sandy Soil</option>
                            <option value="clay">Clay Soil</option>
                            <option value="custom">Custom</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label for="ks">Hydraulic Conductivity (m/s):</label>
                        <input type="number" id="ks" step="1e-6" value="0.00001" style="width: 150px;">
                    </div>
                </div>
                
                <div>
                    <h3>Analysis</h3>
                    <div class="input-group">
                        <label for="Sr">Soil Moderation Factor:</label>
                        <input type="number" id="Sr" min="0.5" max="2" step="0.1" value="1.0">
                    </div>
                    <div class="input-group">
                        <button onclick="runAnalysis()">🔍 Analyze Performance</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="results" id="results" style="display: none;">
            <h2>📊 Analysis Results</h2>
            <div id="metrics"></div>
            <div id="recommendations"></div>
        </div>
    </div>

    <script>
        // Sample data for demonstration
        const demoData = {
            time_min: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
            total_flow: [0, 0.001, 0.004, 0.008, 0.012, 0.015, 0.010, 0.006, 0.003, 0.001, 0, 0, 0]
        };
        
        function updateSoilProperties() {
            const soilType = document.getElementById('soilType').value;
            const ksInput = document.getElementById('ks');
            
            switch(soilType) {
                case 'sandy':
                    ksInput.value = 0.0001;
                    break;
                case 'medium':
                    ksInput.value = 0.00001;
                    break;
                case 'clay':
                    ksInput.value = 0.000001;
                    break;
            }
        }
        
        function calculateSoakwellOutflow(diameter, ks, Sr) {
            const height = diameter;
            const baseArea = Math.PI * Math.pow(diameter/2, 2);
            const wallArea = Math.PI * diameter * height;
            const totalArea = baseArea + wallArea;
            return ks * totalArea / Sr;
        }
        
        function simulatePerformance(hydrographData, diameter, ks, Sr, maxHeight) {
            if (!maxHeight) maxHeight = diameter;
            
            const maxVolume = Math.PI * Math.pow(diameter/2, 2) * maxHeight;
            const maxOutflowRate = calculateSoakwellOutflow(diameter, ks, Sr);
            
            let storedVolume = 0;
            let cumulativeInflow = 0;
            let cumulativeOutflow = 0;
            let maxStorage = 0;
            let peakOverflow = 0;
            
            for (let i = 1; i < hydrographData.time_min.length; i++) {
                const dt = (hydrographData.time_min[i] - hydrographData.time_min[i-1]) * 60; // seconds
                const inflow = hydrographData.total_flow[i];
                
                // Calculate outflow based on current water level
                const currentLevel = storedVolume / (Math.PI * Math.pow(diameter/2, 2));
                const levelFactor = Math.min(currentLevel / maxHeight, 1.0);
                const currentOutflowRate = storedVolume > 0 ? maxOutflowRate * levelFactor : 0;
                
                // Volume changes
                const volumeIn = inflow * dt;
                const volumeOut = currentOutflowRate * dt;
                
                // Update storage
                let newVolume = storedVolume + volumeIn - volumeOut;
                let overflow = 0;
                
                if (newVolume > maxVolume) {
                    overflow = (newVolume - maxVolume) / dt;
                    newVolume = maxVolume;
                    peakOverflow = Math.max(peakOverflow, overflow);
                }
                
                storedVolume = Math.max(0, newVolume);
                maxStorage = Math.max(maxStorage, storedVolume);
                cumulativeInflow += volumeIn;
                cumulativeOutflow += volumeOut;
            }
            
            return {
                maxStorage: maxStorage,
                maxVolume: maxVolume,
                cumulativeInflow: cumulativeInflow,
                cumulativeOutflow: cumulativeOutflow,
                peakOverflow: peakOverflow,
                storageEfficiency: cumulativeInflow > 0 ? cumulativeOutflow / cumulativeInflow : 0,
                volumeUtilization: maxStorage / maxVolume
            };
        }
        
        function runAnalysis() {
            const diameter = parseFloat(document.getElementById('diameter').value);
            const height = parseFloat(document.getElementById('height').value);
            const ks = parseFloat(document.getElementById('ks').value);
            const Sr = parseFloat(document.getElementById('Sr').value);
            
            // Use demo data for now
            const results = simulatePerformance(demoData, diameter, ks, Sr, height);
            
            displayResults(results);
        }
        
        function displayResults(results) {
            const resultsDiv = document.getElementById('results');
            const metricsDiv = document.getElementById('metrics');
            const recommendationsDiv = document.getElementById('recommendations');
            
            // Show results
            resultsDiv.style.display = 'block';
            
            // Display metrics
            metricsDiv.innerHTML = `
                <div class="metric">
                    <div class="metric-value">${(results.storageEfficiency * 100).toFixed(1)}%</div>
                    <div class="metric-label">Storage Efficiency</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${results.maxStorage.toFixed(1)} m³</div>
                    <div class="metric-label">Max Storage Used</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${(results.volumeUtilization * 100).toFixed(0)}%</div>
                    <div class="metric-label">Volume Utilization</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${results.peakOverflow.toFixed(4)} m³/s</div>
                    <div class="metric-label">Peak Overflow</div>
                </div>
            `;
            
            // Display recommendations
            let recommendations = '';
            if (results.peakOverflow > 0) {
                recommendations += '<div class="warning">⚠️ Overflow detected. Consider increasing diameter or using multiple soakwells.</div>';
            } else {
                recommendations += '<div class="success">✅ No overflow detected for this design.</div>';
            }
            
            if (results.storageEfficiency < 0.2) {
                recommendations += '<div class="warning">💡 Low storage efficiency. Consider improving soil conditions or increasing infiltration area.</div>';
            }
            
            if (results.volumeUtilization < 0.5) {
                recommendations += '<div class="warning">📏 Low volume utilization. Soakwell may be oversized for this storm.</div>';
            }
            
            recommendationsDiv.innerHTML = '<h3>💡 Recommendations:</h3>' + recommendations;
        }
        
        // Initialize
        updateSoilProperties();
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())

def start_server():
    PORT = 8505
    
    print("🌧️ Starting Simple Soakwell Dashboard...")
    print(f"📱 Open your browser to: http://localhost:{PORT}")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 60)
    
    with socketserver.TCPServer(("", PORT), SoakwellHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    start_server()
