# NEXUS: Neural Executive Utility System
Status: Phase 1 (Core Integration)

Persona: Hybrid JARVIS/FRIDAY Strategy Interface

NEXUS is a private, cross-device AI ecosystem designed to function as a tactical partner. It bridges the gap between local Large Language Models (LLMs), system-level automation, and physical hardware interfaces.

### 🧠 System Philosophy
NEXUS is built to be proactive rather than reactive. By fusing the poise of a classic butler with the high-velocity data processing of a tactical co-pilot, the system manages everything from terminal commands to IoT sensor arrays.

### 🏗️ Architecture
The project follows a Polyglot Client-Server model to ensure low-latency performance across all devices.

Brain (Local Server): High-parameter LLM (Ministral-3 or better non thinking llm) running via Ollama on specialized AI hardware.

Limbs (Clients): Lightweight Python/C++ nodes on Pop!_OS (Desktop), ESP32 (Robotics), and Mobile.

Nervous System: Secure private mesh (Tailscale) with MQTT for real-time hardware communication.

### 📂 Project Structure
ai_infrastructure/
├── src/ai_infrastructure/
│   ├── main.py           # Logic Gate & Agentic Loop
│   ├── components/       # LLM Providers & Toolsets
│   └── data/             # JSON State & Memory Management
├── tests/                # Integration & Hardware simulation
└── docs/                 # Schematics for Robotics & API

🚀 Key Features (Active & Planned)
[ ] Agentic Loop: Self-aware status checking via [STATE] and [USER] tags.

[ ] OS Integration: Direct terminal execution on Linux.

[ ] Physical Node: Integration with Raspberry Pi 5 / ESP32 sensor dress project.

[ ] Vision Layer: Real-time analysis for smart glasses.

### 🛠️ Hardware Requirements
To run NEXUS at full capacity, the following hardware is targeted:

Primary GPU: NVIDIA RTX 50-series (Targeting 24GB+ VRAM) or AMD RX 9000-series.

Otherwise any GPU supporting Ministral-3 or better.

Microcontrollers: Raspberry Pi 5 (System Control), ESP32.

Developpement: Pop!_OS with Cosmic DE.
Environnement: Not tested

🔧 Installation & Setup
Clone the Repo:

Bash
git clone https://github.com/R3D70RD/NEXUS.git

Setup Virtual Environment:
Bash
python -m venv venv
source venv/bin/activate
pip install -e .
Configure Ollama: Ensure your selected LLM is pulled and running locally.

### 📜 Personal Protocol
NEXUS is a private development. All logic, memory, and personal data logs are strictly local and encrypted. Zero-cloud dependency is a core requirement.
