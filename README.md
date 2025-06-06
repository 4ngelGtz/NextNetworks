# Sistema de Registro de Camiones con QR

Sistema completo para el control de entrada de camiones mediante códigos QR. Incluye generación de códigos QR para choferes y validación en tiempo real para personal de seguridad.

## 🚀 Características

- **Generación de QR**: Interfaz simple para crear códigos QR únicos por chofer
- **Validación de entrada**: Sistema de escaneo para personal de seguridad
- **Registro de logs**: Almacenamiento automático en JSON y CSV
- **Interfaz web moderna**: Diseño responsive y fácil de usar
- **Almacenamiento local**: Todo funciona sin conexión a internet
- **Backend robusto**: API REST con FastAPI

## 🛠️ Tecnologías

- **Backend**: Python FastAPI
- **Frontend**: HTML5, CSS3, JavaScript
- **Base de datos**: Archivos JSON/CSV locales
- **QR**: Biblioteca qrcode de Python
- **Estilos**: CSS moderno con gradientes y animaciones

## 📋 Requisitos

- Python 3.8+
- Navegador web moderno
- Cámara web (opcional, para escaneo automático)

## 🚀 Instalación y Uso

### 1. Instalar dependencias de Python

```bash
pip install fastapi uvicorn qrcode[pil] python-multipart opencv-python-headless pillow pandas Jinja2
```

### 2. Crear directorios necesarios

```bash
mkdir -p data static/qr_codes
```

### 3. Ejecutar el servidor

```bash
python backend/main.py
```

### 4. Acceder a la aplicación

- **Página principal**: http://localhost:8000
- **Generar QR**: http://localhost:8000/generate
- **Escanear QR**: http://localhost:8000/scan  
- **Ver registros**: http://localhost:8000/logs

## 📱 Uso del Sistema

### Para Administradores - Generar QR

1. Acceder a la sección "Generar Código QR"
2. Ingresar nombre y apellidos del chofer
3. Generar y descargar/imprimir el código QR
4. Entregar el QR al chofer

### Para Personal de Seguridad - Validar Entrada

1. Acceder a la sección "Escanear QR - Entrada"
2. Usar lector QR del móvil o ingresar manualmente el código
3. El sistema validará automáticamente y registrará la entrada
4. Respuesta visual inmediata (verde = válido, rojo = inválido)

### Para Supervisores - Ver Registros

1. Acceder a "Ver Registros" 
2. Revisar estadísticas y historial completo
3. Los datos también están disponibles en archivos CSV/JSON

## 📁 Estructura de Archivos

```
proyecto/
├── backend/
│   ├── main.py              # Servidor FastAPI principal
│   └── requirements.txt     # Dependencias Python
├── data/
│   ├── drivers.json         # Base de datos de choferes
│   ├── entry_logs.json      # Logs en formato JSON
│   └── entry_logs.csv       # Logs en formato CSV
├── static/
│   └── qr_codes/           # Imágenes de códigos QR generados
└── README.md
```

## 🔒 Seguridad

- Códigos QR únicos con hash MD5
- Validación de timestamps
- Registro completo de todos los intentos de acceso
- Sistema de logs detallado para auditoría

## 📊 Formatos de Datos

### JSON de Choferes (drivers.json)
```json
{
  "abc123def456": {
    "name": "Juan Pérez",
    "code": "abc123def456", 
    "generated_at": "2024-01-15T10:30:00",
    "qr_image": "static/qr_codes/qr_abc123def456.png",
    "used": false
  }
}
```

### CSV de Logs (entry_logs.csv)
```csv
timestamp,driver_name,qr_code,status,notes
2024-01-15 10:35:22,Juan Pérez,abc123def456,Entrada válida,QR generado el 2024-01-15T10:30:00
```

## 🎨 Personalización

El sistema usa CSS moderno con variables que pueden modificarse fácilmente:
- Colores corporativos
- Tamaños de fuente
- Espaciado y diseño responsive
- Animaciones y transiciones

## 🔧 Desarrollo

Para desarrollo local:

1. El servidor se reinicia automáticamente con cambios (`reload=True`)
2. Los logs se actualizan en tiempo real
3. Las imágenes QR se almacenan permanentemente
4. Base de datos JSON permite inspección manual

## 📞 Soporte

Sistema diseñado para uso industrial en plantas y almacenes. Interfaz optimizada para:
- Tablets en casetas de vigilancia
- Dispositivos móviles para generación de QR
- Computadoras de escritorio para administración

---

🚛 **Sistema desarrollado para control eficiente de entrada de camiones**