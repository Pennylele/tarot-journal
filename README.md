# Tarot Journal

A full-stack web application for logging and analyzing tarot readings. This project demonstrates a decoupled architecture with a Python/FastAPI backend and a React frontend, focused on clean API design and smooth user experience.

## 🏗️ Project Structure
- **`backend/`**: FastAPI server handling business logic, randomized card drawing engines, and data persistence.
- **`frontend/`**: React application built with modern hooks and state management for a responsive journaling interface.

## 🚀 Tech Stack
- **Backend:** Python, FastAPI, SQLAlchemy
- **Frontend:** React.js
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Architecture:** RESTful API Design, JWT Authentication

## ✨ Key Features
- **Decoupled Architecture:** Clean separation between the client and server, allowing for independent scaling and testing.
- **Dynamic Drawing Engine:** Backend logic to handle randomized card selection, including upright and reversed orientations.
- **Journal Application:** Handle user login, authentication and authorization, entry management. 
- **Modern UI:** Responsive design using Tailwind CSS for a seamless journaling experience across devices.

## 🛠️ Getting Started

### Backend
1. Navigate to `/backend`
2. Install dependencies: `uv sync`
3. Start the server: `uv run fastapi dev main`

### Frontend
1. Navigate to `/frontend`
2. Install dependencies: `npm install`
3. Start the app: `npm run dev`

## 🎯 Future Roadmap
- Integration of Generative AI to provide automated card interpretation summaries.
- Advanced visualization of drawing history trends.