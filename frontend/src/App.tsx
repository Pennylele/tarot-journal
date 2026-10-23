import { useState } from 'react'
import './App.css'
import TarotShuffle from './components/TarotShuffle'
import JournalHistory from './components/JournalHistory'
import Login from './components/Login'
import { useAuth } from './AuthContext'

function App() {
  const [activeTab, setActiveTab] = useState<'draw' | 'history'>('draw')
  const { isAuthenticated, openLogin } = useAuth()

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="title-area">
            <h1>Tarot Journal</h1>
          </div>

          <nav className="header-nav">
            <button
              className={`nav-btn ${activeTab === 'draw' ? 'active' : ''}`}
              onClick={() => setActiveTab('draw')}
            >
              DRAW CARD
            </button>
            <button
              className={`nav-btn ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => {
                if (!isAuthenticated) {
                  openLogin()
                } else {
                  setActiveTab('history')
                }
              }}
            >
              MY ENTRIES
            </button>
          </nav>

          <div className="utility-icons">
            <Login />
          </div>
        </div>
      </header>

      <main>
        {activeTab === 'draw' ? (
          <TarotShuffle onViewEntries={() => setActiveTab('history')} />
        ) : (
          <JournalHistory onDrawNew={() => setActiveTab('draw')} />
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; 2026 Tarot Journal App</p>
      </footer>
    </div>
  )
}

export default App
