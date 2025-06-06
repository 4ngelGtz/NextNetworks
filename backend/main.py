from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import qrcode
import json
import csv
import os
from datetime import datetime
import hashlib
import base64
from PIL import Image
import io
import pandas as pd

app = FastAPI(title="Sistema de Registro de Camiones")

# Configurar directorios
os.makedirs("data", exist_ok=True)
os.makedirs("static/qr_codes", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Archivos de datos
DRIVERS_FILE = "data/drivers.json"
LOGS_FILE = "data/entry_logs.json"
LOGS_CSV_FILE = "data/entry_logs.csv"

# Inicializar archivos si no existen
def init_data_files():
    if not os.path.exists(DRIVERS_FILE):
        with open(DRIVERS_FILE, 'w') as f:
            json.dump({}, f)
    
    if not os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(LOGS_CSV_FILE):
        with open(LOGS_CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'driver_name', 'qr_code', 'status', 'notes'])

init_data_files()

def load_drivers():
    with open(DRIVERS_FILE, 'r') as f:
        return json.load(f)

def save_drivers(drivers):
    with open(DRIVERS_FILE, 'w') as f:
        json.dump(drivers, f, indent=2)

def load_logs():
    with open(LOGS_FILE, 'r') as f:
        return json.load(f)

def save_log_entry(log_entry):
    # Guardar en JSON
    logs = load_logs()
    logs.append(log_entry)
    with open(LOGS_FILE, 'w') as f:
        json.dump(logs, f, indent=2)
    
    # Guardar en CSV
    with open(LOGS_CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            log_entry['timestamp'],
            log_entry['driver_name'],
            log_entry['qr_code'],
            log_entry['status'],
            log_entry.get('notes', '')
        ])

def generate_qr_code(driver_name: str):
    # Crear un hash único basado en el nombre y timestamp
    timestamp = datetime.now().isoformat()
    unique_string = f"{driver_name}_{timestamp}"
    qr_hash = hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    # Crear el código QR
    qr_data = {
        "driver_name": driver_name,
        "code": qr_hash,
        "generated_at": timestamp
    }
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar imagen
    qr_filename = f"qr_{qr_hash}.png"
    qr_path = f"static/qr_codes/{qr_filename}"
    img.save(qr_path)
    
    # Guardar información del conductor
    drivers = load_drivers()
    drivers[qr_hash] = {
        "name": driver_name,
        "code": qr_hash,
        "generated_at": timestamp,
        "qr_image": qr_path,
        "used": False
    }
    save_drivers(drivers)
    
    return qr_hash, qr_path

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema de Registro de Camiones</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }
            
            .logo {
                width: 80px;
                height: 80px;
                background: #2a5298;
                border-radius: 50%;
                margin: 0 auto 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 36px;
                color: white;
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 28px;
            }
            
            .subtitle {
                color: #7f8c8d;
                margin-bottom: 40px;
                font-size: 16px;
            }
            
            .btn-group {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            
            .btn {
                padding: 20px 30px;
                font-size: 18px;
                font-weight: 600;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                text-decoration: none;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
            }
            
            .btn-secondary {
                background: linear-gradient(135deg, #27ae60, #229954);
                color: white;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }
            
            .icon {
                font-size: 24px;
            }
            
            @media (max-width: 600px) {
                .container {
                    padding: 30px 20px;
                }
                
                h1 {
                    font-size: 24px;
                }
                
                .btn {
                    padding: 18px 25px;
                    font-size: 16px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🚛</div>
            <h1>Sistema de Registro</h1>
            <p class="subtitle">Control de Entrada de Camiones</p>
            
            <div class="btn-group">
                <a href="/generate" class="btn btn-primary">
                    <span class="icon">📱</span>
                    Generar Código QR
                </a>
                
                <a href="/scan" class="btn btn-secondary">
                    <span class="icon">📷</span>
                    Escanear QR - Entrada
                </a>
                
                <a href="/logs" class="btn" style="background: linear-gradient(135deg, #8e44ad, #7d3c98); color: white;">
                    <span class="icon">📊</span>
                    Ver Registros
                </a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/generate", response_class=HTMLResponse)
async def generate_page():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Generar Código QR</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            .back-btn {
                position: absolute;
                top: 30px;
                left: 30px;
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                cursor: pointer;
                text-decoration: none;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            
            .back-btn:hover {
                background: rgba(255,255,255,0.3);
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 28px;
            }
            
            .form-group {
                margin-bottom: 25px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #2c3e50;
                font-weight: 600;
                font-size: 16px;
            }
            
            input[type="text"] {
                width: 100%;
                padding: 15px;
                border: 2px solid #e1e8ed;
                border-radius: 10px;
                font-size: 16px;
                transition: border-color 0.3s ease;
            }
            
            input[type="text"]:focus {
                outline: none;
                border-color: #3498db;
            }
            
            .btn {
                width: 100%;
                padding: 18px;
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
            }
            
            .result {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 12px;
                text-align: center;
                display: none;
            }
            
            .qr-code {
                max-width: 250px;
                height: auto;
                margin: 20px auto;
                border: 3px solid #e1e8ed;
                border-radius: 10px;
            }
            
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
        </style>
    </head>
    <body>
        <a href="/" class="back-btn">← Volver</a>
        
        <div class="container">
            <div class="header">
                <h1>Generar Código QR</h1>
                <p>Ingrese el nombre completo del chofer</p>
            </div>
            
            <form id="qrForm">
                <div class="form-group">
                    <label for="firstName">Nombre(s):</label>
                    <input type="text" id="firstName" name="firstName" required>
                </div>
                
                <div class="form-group">
                    <label for="lastName">Apellidos:</label>
                    <input type="text" id="lastName" name="lastName" required>
                </div>
                
                <button type="submit" class="btn">Generar Código QR</button>
            </form>
            
            <div id="result" class="result">
                <h3>¡Código QR Generado!</h3>
                <img id="qrImage" class="qr-code" alt="Código QR">
                <p><strong>Chofer:</strong> <span id="driverName"></span></p>
                <p><strong>Código:</strong> <span id="qrCode"></span></p>
                <p style="margin-top: 15px; color: #666;">Guarde o imprima este código QR</p>
            </div>
        </div>
        
        <script>
            document.getElementById('qrForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const firstName = document.getElementById('firstName').value;
                const lastName = document.getElementById('lastName').value;
                const fullName = `${firstName} ${lastName}`.trim();
                
                if (!fullName) {
                    alert('Por favor ingrese el nombre completo');
                    return;
                }
                
                try {
                    const response = await fetch('/api/generate-qr', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `driver_name=${encodeURIComponent(fullName)}`
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        document.getElementById('driverName').textContent = fullName;
                        document.getElementById('qrCode').textContent = data.qr_code;
                        document.getElementById('qrImage').src = '/' + data.qr_image;
                        document.getElementById('result').style.display = 'block';
                        document.getElementById('result').classList.add('success');
                        
                        // Limpiar formulario
                        document.getElementById('qrForm').reset();
                    } else {
                        alert('Error al generar el código QR: ' + data.message);
                    }
                } catch (error) {
                    alert('Error de conexión: ' + error.message);
                }
            });
        </script>
    </body>
    </html>
    """

@app.get("/scan", response_class=HTMLResponse)
async def scan_page():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Escanear QR - Control de Entrada</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }
            
            .back-btn {
                position: absolute;
                top: 30px;
                left: 30px;
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                cursor: pointer;
                text-decoration: none;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            
            .back-btn:hover {
                background: rgba(255,255,255,0.3);
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 28px;
            }
            
            .scan-section {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .manual-input {
                background: #f8f9fa;
                padding: 30px;
                border-radius: 15px;
                margin-top: 30px;
            }
            
            .input-group {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
            }
            
            input[type="text"] {
                flex: 1;
                padding: 15px;
                border: 2px solid #e1e8ed;
                border-radius: 10px;
                font-size: 16px;
            }
            
            .btn {
                padding: 15px 30px;
                background: linear-gradient(135deg, #27ae60, #229954);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(39, 174, 96, 0.3);
            }
            
            .result {
                margin-top: 30px;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                font-size: 18px;
                font-weight: 600;
                display: none;
            }
            
            .success {
                background: #d4edda;
                color: #155724;
                border: 2px solid #c3e6cb;
            }
            
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 2px solid #f5c6cb;
            }
            
            .driver-info {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-top: 15px;
                border-left: 4px solid #27ae60;
            }
            
            .timestamp {
                font-size: 14px;
                color: #666;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <a href="/" class="back-btn">← Volver</a>
        
        <div class="container">
            <div class="header">
                <h1>🛡️ Control de Entrada</h1>
                <p>Escanee o ingrese el código QR del chofer</p>
            </div>
            
            <div class="scan-section">
                <p style="color: #666; margin-bottom: 20px;">
                    📱 Use un lector de códigos QR en su dispositivo móvil o ingrese manualmente el código
                </p>
            </div>
            
            <div class="manual-input">
                <h3 style="margin-bottom: 20px; color: #2c3e50;">Ingreso Manual</h3>
                <form id="validateForm">
                    <div class="input-group">
                        <input type="text" id="qrCode" placeholder="Código QR o datos escaneados" required>
                        <button type="submit" class="btn">Validar Entrada</button>
                    </div>
                </form>
            </div>
            
            <div id="result" class="result">
                <div id="resultContent"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('validateForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const qrCode = document.getElementById('qrCode').value.trim();
                
                if (!qrCode) {
                    alert('Por favor ingrese el código QR');
                    return;
                }
                
                try {
                    const response = await fetch('/api/validate-qr', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `qr_data=${encodeURIComponent(qrCode)}`
                    });
                    
                    const data = await response.json();
                    const resultDiv = document.getElementById('result');
                    const contentDiv = document.getElementById('resultContent');
                    
                    resultDiv.style.display = 'block';
                    
                    if (data.success) {
                        resultDiv.className = 'result success';
                        contentDiv.innerHTML = `
                            <div style="font-size: 24px; margin-bottom: 15px;">✅ ENTRADA VÁLIDA</div>
                            <div class="driver-info">
                                <div style="font-size: 20px; margin-bottom: 10px;">
                                    <strong>Chofer:</strong> ${data.driver_name}
                                </div>
                                <div style="font-size: 16px; color: #666;">
                                    <strong>Código:</strong> ${data.qr_code}
                                </div>
                                <div class="timestamp">
                                    Registrado: ${new Date().toLocaleString('es-ES')}
                                </div>
                            </div>
                        `;
                        
                        // Limpiar campo después del éxito
                        document.getElementById('qrCode').value = '';
                        
                        // Auto-ocultar resultado después de 5 segundos
                        setTimeout(() => {
                            resultDiv.style.display = 'none';
                        }, 5000);
                        
                    } else {
                        resultDiv.className = 'result error';
                        contentDiv.innerHTML = `
                            <div style="font-size: 24px; margin-bottom: 15px;">❌ QR INVÁLIDO</div>
                            <div style="font-size: 16px;">
                                ${data.message}
                            </div>
                            <div class="timestamp">
                                Intento registrado: ${new Date().toLocaleString('es-ES')}
                            </div>
                        `;
                    }
                } catch (error) {
                    const resultDiv = document.getElementById('result');
                    const contentDiv = document.getElementById('resultContent');
                    
                    resultDiv.style.display = 'block';
                    resultDiv.className = 'result error';
                    contentDiv.innerHTML = `
                        <div style="font-size: 24px; margin-bottom: 15px;">⚠️ ERROR DE CONEXIÓN</div>
                        <div style="font-size: 16px;">
                            ${error.message}
                        </div>
                    `;
                }
            });
            
            // Auto-focus en el campo de entrada
            document.getElementById('qrCode').focus();
        </script>
    </body>
    </html>
    """

@app.get("/logs", response_class=HTMLResponse)
async def logs_page():
    logs = load_logs()
    logs.reverse()  # Mostrar los más recientes primero
    
    logs_html = ""
    for log in logs[:50]:  # Mostrar últimos 50 registros
        status_class = "success" if log['status'] == "Entrada válida" else "error"
        status_icon = "✅" if log['status'] == "Entrada válida" else "❌"
        
        logs_html += f"""
        <tr class="{status_class}">
            <td>{log['timestamp']}</td>
            <td>{log['driver_name']}</td>
            <td>{log['qr_code'][:12]}...</td>
            <td>{status_icon} {log['status']}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Registros de Entrada</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #8e44ad 0%, #7d3c98 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }}
            
            .back-btn {{
                position: absolute;
                top: 30px;
                left: 30px;
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                cursor: pointer;
                text-decoration: none;
                font-size: 16px;
                transition: all 0.3s ease;
            }}
            
            .back-btn:hover {{
                background: rgba(255,255,255,0.3);
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            h1 {{
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 28px;
            }}
            
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            
            .stat-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                border-left: 4px solid #3498db;
            }}
            
            .stat-number {{
                font-size: 32px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            
            .stat-label {{
                color: #666;
                font-size: 14px;
            }}
            
            .table-container {{
                overflow-x: auto;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}
            
            th {{
                background: #34495e;
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }}
            
            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #eee;
            }}
            
            tr:hover {{
                background: #f8f9fa;
            }}
            
            .success {{
                background: rgba(212, 237, 218, 0.3);
            }}
            
            .error {{
                background: rgba(248, 215, 218, 0.3);
            }}
            
            .no-data {{
                text-align: center;
                padding: 40px;
                color: #666;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <a href="/" class="back-btn">← Volver</a>
        
        <div class="container">
            <div class="header">
                <h1>📊 Registros de Entrada</h1>
                <p>Últimos movimientos registrados</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(logs)}</div>
                    <div class="stat-label">Total Registros</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([l for l in logs if l['status'] == 'Entrada válida'])}</div>
                    <div class="stat-label">Entradas Válidas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([l for l in logs if l['status'] != 'Entrada válida'])}</div>
                    <div class="stat-label">QR Inválidos</div>
                </div>
            </div>
            
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Fecha y Hora</th>
                            <th>Chofer</th>
                            <th>Código QR</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs_html if logs_html else '<tr><td colspan="4" class="no-data">No hay registros disponibles</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/api/generate-qr")
async def api_generate_qr(driver_name: str = Form(...)):
    try:
        qr_code, qr_path = generate_qr_code(driver_name)
        return {
            "success": True,
            "qr_code": qr_code,
            "qr_image": qr_path,
            "driver_name": driver_name
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/validate-qr")
async def api_validate_qr(qr_data: str = Form(...)):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Intentar parsear como JSON (datos del QR generado)
        try:
            qr_json = json.loads(qr_data)
            if "code" in qr_json and "driver_name" in qr_json:
                qr_code = qr_json["code"]
                driver_name = qr_json["driver_name"]
            else:
                raise ValueError("Formato de QR inválido")
        except json.JSONDecodeError:
            # Si no es JSON, asumir que es solo el código
            qr_code = qr_data.strip()
            driver_name = "Desconocido"
        
        # Verificar en la base de datos de conductores
        drivers = load_drivers()
        
        if qr_code in drivers:
            driver_info = drivers[qr_code]
            log_entry = {
                "timestamp": timestamp,
                "driver_name": driver_info["name"],
                "qr_code": qr_code,
                "status": "Entrada válida",
                "notes": f"QR generado el {driver_info['generated_at']}"
            }
            
            save_log_entry(log_entry)
            
            return {
                "success": True,
                "driver_name": driver_info["name"],
                "qr_code": qr_code,
                "message": "Entrada autorizada"
            }
        else:
            log_entry = {
                "timestamp": timestamp,
                "driver_name": driver_name,
                "qr_code": qr_code,
                "status": "QR inválido",
                "notes": "Código no encontrado en la base de datos"
            }
            
            save_log_entry(log_entry)
            
            return {
                "success": False,
                "message": "Código QR no válido o no registrado",
                "qr_code": qr_code
            }
            
    except Exception as e:
        log_entry = {
            "timestamp": timestamp,
            "driver_name": "Error",
            "qr_code": qr_data[:50],
            "status": "Error del sistema",
            "notes": str(e)
        }
        
        save_log_entry(log_entry)
        
        return {
            "success": False,
            "message": f"Error al procesar el código QR: {str(e)}"
        }

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n🚛 Sistema de Registro de Camiones")
    print("=================================")
    print("📱 Generar QR: http://localhost:8000/generate")
    print("📷 Escanear QR: http://localhost:8000/scan")
    print("📊 Ver Registros: http://localhost:8000/logs")
    print("🏠 Inicio: http://localhost:8000")
    print("\n⚡ Iniciando servidor...")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)