import './App.css'
import TarotShuffle from './components/TarotShuffle'
import Login from './components/Login'

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="title-area">
            <h1>Tarot Journal</h1>
          </div>
          <div className="utility-icons">
            <Login />
          </div>
        </div>
      </header>

      <main>
        <TarotShuffle />
      </main>

      <footer className="app-footer">
        <p>&copy; 2026 Tarot Journal App</p>
      </footer>
    </div>
  )
}

export default App
