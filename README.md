# VIKO-Intelligence: Zero-Click Business AI

VIKO-Intelligence es una plataforma SaaS de análisis predictivo y Business Intelligence diseñada por VIKOTECH Solutions a cargo de Marcos Hernández lead developer. Transforma archivos de datos crudos (ventas, inventarios, tickets) en decisiones estratégicas instantáneas y paneles visuales interactivos.

El proyecto implementa una arquitectura Zero-Click BI: el usuario sube un archivo y el motor autodescubre las métricas financieras clave, limpia los datos y entrena un modelo de Machine Learning en tiempo real, eliminando por completo la fricción de configuración manual.

## Características Principales

* Auto-Descubrimiento de Métricas: Algoritmo heurístico que identifica automáticamente la columna de mayor impacto financiero (target column) en cualquier dataset.
* Feature Engineering al Vuelo: Extracción automática de inteligencia temporal (estacionalidad mensual, días de la semana, fines de semana) y codificación One-Hot para variables categóricas.
* Motor Predictivo (V4): Implementación de RandomForestRegressor para estimar el valor de las próximas transacciones comerciales basándose en patrones históricos.
* Dashboard Ejecutivo Interactivo: Visualización simétrica de KPIs, gráficas de área para tendencias históricas y gráficas de barras para el Top de Productos, todo responsivo y adaptable.

## Stack Tecnológico

Backend (Motor Analítico)
* Python 3.11+
* FastAPI & Uvicorn (API RESTful)
* Pandas & NumPy (Procesamiento de datos)
* Scikit-Learn (Machine Learning)

Frontend (Interfaz de Usuario)
* Next.js 14 (React)
* TypeScript
* Tailwind CSS (Estilos y diseño fluido)
* Recharts (Visualización de datos empresariales)

## Instalación y Despliegue Local

### 1. Clonar el repositorio
```bash
git clone [https://github.com/TuUsuario/viko-intelligence.git](https://github.com/TuUsuario/Intelligence_AI.git)
cd viko-intelligence
```

### 2. Configurar el Backend
```bash
# Navegar al directorio del backend
cd backend

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar el servidor FastAPI
python -m api.main
```
El backend estará corriendo en http://127.0.0.1:8000

### 3. Configurar el Frontend
```bash
# Navegar al directorio del frontend
cd frontend

# Instalar paquetes
npm install

# Configurar variables de entorno
# Crear archivo .env.local y agregar: NEXT_PUBLIC_API_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)

# Iniciar el servidor de desarrollo
npm run dev
```
La aplicación web estará disponible en http://localhost:3000



## Roadmap Futuro
- [ ] Exportación de Reportes Ejecutivos a formato PDF.
- [ ] Integración mediante API con sistemas de Punto de Venta (POS).
- [ ] Módulo específico para predicción de inventarios y rotura de stock.

## Autor

Desarrollado y mantenido por Marcos Gael Hernández Cruz.
Fundador de VIKOTECH Solutions.
Ingeniería en Computación - Universidad Tecnológica de la Mixteca (UTM).
