# GHURI – Smart Travel & Safety Platform 🌍

**GHURI** is a smart travel and safety platform designed to connect travelers, property owners, and administrators through a unified digital solution. Combining mobile application development, backend services, and IoT technology, GHURI aims to improve travel management and enhance traveler safety through GPS tracking and an SOS emergency alert system.

## ✨ Key Features

- **Travel Management:** A digital platform for travelers to access travel-related services.
- **Property Owner Connectivity:** Connects travelers with property owners through the platform.
- **Admin Management:** Supports centralized platform administration.
- **IoT-Based GPS Tracking:** Integrates ESP32-based hardware for location tracking.
- **SOS Emergency System:** Provides an emergency alert mechanism to support traveler safety.
- **RESTful Backend API:** Uses FastAPI to handle application requests and backend operations.
- **Database Management:** Uses SQLite for structured data storage.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Flutter | Cross-platform mobile application development |
| FastAPI | Backend API development |
| SQLite | Database management |
| ESP32 | IoT hardware integration |
| GPS | Location tracking and positioning |

## 🏗️ System Architecture

GHURI combines three main components:

1. **Mobile Application — Flutter:** Provides the user-facing interface for the travel and safety platform.
2. **Backend Server — FastAPI:** Handles API requests and communication between the mobile application and database.
3. **IoT Tracking System — ESP32 + GPS:** Supports location tracking and integration with the SOS emergency workflow.

**Data flow:**

`Flutter App ↔ FastAPI Backend ↔ SQLite Database`

`ESP32 + GPS → Location Data → Backend / Safety Workflow`

*The exact communication flow depends on the implemented hardware and backend integration.*

## 🚀 Getting Started

### Prerequisites

Install the following tools before setting up the project:

- Flutter SDK
- Dart SDK
- Python 3.10+
- pip
- Git
- An ESP32 development board and compatible GPS module (for hardware integration)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/GHURI-Smart-Travel-Safety-Platform.git
cd GHURI-Smart-Travel-Safety-Platform
```

**2. Set up the backend**

Navigate to the backend directory (adjust the path to match your repository structure):

```bash
cd backend
python -m venv venv
```

Activate the virtual environment.

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI server:

```bash
uvicorn main:app --reload
```

Once running, the interactive API documentation is typically available at:

`http://127.0.0.1:8000/docs`

**3. Set up the Flutter application**

Open a new terminal and navigate to the Flutter project directory:

```bash
cd frontend
flutter pub get
flutter run
```

Replace `backend` and `frontend` with your actual directory names if they differ.

## 📁 Suggested Repository Structure

```text
GHURI-Smart-Travel-Safety-Platform/
├── frontend/              # Flutter mobile application
├── backend/               # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── iot/                   # ESP32 and GPS firmware
├── docs/                  # Documentation and diagrams
├── screenshots/           # Application screenshots
├── .gitignore
└── README.md
```

*This is a suggested structure; adapt it to the files in your actual project.*

## 🔐 Safety and Privacy

GHURI is designed with traveler safety in mind. The GPS tracking and SOS features should be implemented with appropriate user consent, access controls, and protection of sensitive location data.

## 🔮 Future Improvements

- Live map-based location visualization
- Real-time emergency notifications
- Travel itinerary and destination management
- Property discovery and booking integration
- Improved location-sharing and emergency contact workflows
- Enhanced authentication and access control

## 👨‍💻 Project Information

**Project Name:** GHURI – Smart Travel & Safety Platform  
**Year:** 2026  
**Category:** Mobile Application Development, Backend Engineering, IoT, GPS Tracking, and Travel Safety

## 📄 License

Choose an appropriate open-source license before distributing this project. For example, you may use the MIT License if its terms fit your goals.

---

*GHURI combines mobile technology, backend engineering, and IoT-based tracking to explore safer and smarter travel experiences.*
