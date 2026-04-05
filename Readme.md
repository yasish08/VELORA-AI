# 🌊 Velora AI - Ocean Intelligence Platform

> **AI-powered natural language interface for ocean data analysis and climate predictions.**
> Built to bridge the gap between complex ARGO oceanic data and actionable insights using modern LLMs and predictive modeling.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://reactjs.org)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://python.org)

---

## 🏗 What is Velora AI?

Velora AI is a comprehensive ocean intelligence platform designed to bridge the gap between complex climate data and human understanding. It allows users to query millions of oceanic measurements using simple, natural language.

By leveraging the **ARGO ocean fleet data**, Velora translates raw telemetry into intuitive visualizations, predictive trends, and deep marine insights.

### ✨ Core Features
- 🗣️ **Natural Language Interface**: "Analyze temperature trend in Indian Ocean from 2015-2024."
- 🧠 **AI-Powered Query Parsing**: Automatically extracts geographical coordinates, parameters (temperature, salinity, oxygen), and timeframes from user prompts.
- 📉 **Predictive Forecasting**: Integrated Machine Learning models (Scikit-learn / Linear Regression) to predict future ocean trends based on historical ARGO data.
- 📊 **Dynamic Visualizations**: High-performance interactive charts (Recharts) and geospatial maps (Leaflet) for data exploration.
- 🐚 **Marine Stress Analysis**: Identifies regions at high risk from climate change using anomaly detection algorithms.

---

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: Scikit-Learn, NumPy, pandas for telemetry processing.
- **LLM**: Groq / OpenAI for query intent extraction.
- **Database**: SQLite (local optimization for high-performance telemetry storage).

### Frontend
- **Framework**: React.js with Vite.
- **Styling**: Vanilla CSS with modern dark mode and glassmorphic components.
- **Visuals**: Recharts (Graphs), Leaflet (Maps), Framer Motion (Animations).

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Git**

### 2. Installation
Clone the repository and install dependencies for both the frontend and backend.

```bash
# Clone the repository
git clone https://github.com/Neemasree/VELORA-AI.git
cd VELORA-AI

# Installation is handled by our automation scripts, or manually:
# Backend: cd backend && pip install -r requirements.txt
# Frontend: cd frontend && npm install
```

### 3. Launching the Platform

Use the provided automation scripts for a quick-start experience:

- Run `.\start-backend.bat`
- Run `.\start-frontend.bat`

The platform will be available at **[http://localhost:5173](http://localhost:5173)**.

---

## 🔬 Sample Queries to Try
- `Show temperature trend in Indian Ocean from 2010 to 2024`
- `Analyze salinity levels in the Pacific Ocean`
- `What are the oxygen levels in the Atlantic?`
- `Predict temperature for the next 5 years in the Arctic Ocean`

---

## 📂 Project Structure

```text
velora-ai/
├── backend/              # FastAPI Python Server
│   ├── ai/               # AI & ML logic (Parsing, Prediction, Insights)
│   ├── data/             # Database & CSV datasets (ARGO Telemetry)
│   ├── main.py           # API Endpoints
│   └── requirements.txt  # Python Dependencies
├── frontend/             # React + Vite Application
│   ├── src/              # Components (Charts, Maps, Chat UI)
│   └── .env              # Front-end API Configuration
├── start-backend.bat     # Windows bootstrapper
└── start-frontend.bat    # Windows bootstrapper
```

---

## 👥 Contributors
- **Neemasree** ([GitHub](https://github.com/Neemasree))
- **yasish** ([GitHub](https://github.com/yasish08))

---

## 📞 Support & Contribution

If you find this project useful, feel free to **Fork** it and submit a **Pull Request**! Built with ❤️ for ocean intelligence and climate monitoring.
