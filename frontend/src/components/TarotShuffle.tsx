import React, { useState, useEffect } from 'react';
import './TarotShuffle.css';
import { useAuth } from '../AuthContext';

interface Card {
  id: number;
  name: string;
  slug: string;
  arcana: string;
  suit: string | null;
  meaning_upright: string;
  meaning_reversed: string;
  image_file: string;
}

const TarotShuffle: React.FC = () => {
  const { token, isAuthenticated, openLogin } = useAuth();
  const [isShuffling, setIsShuffling] = useState(false);
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [journalContent, setJournalContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [pendingSave, setPendingSave] = useState(false);

  useEffect(() => {
    if (isAuthenticated && pendingSave) {
      handleSave();
      setPendingSave(false);
    }
  }, [isAuthenticated, token, pendingSave]);

  const handleShuffle = async () => {
    setIsShuffling(true);
    setSelectedCard(null);
    setMessage('');

    setTimeout(async () => {
      try {
        const response = await fetch('/api/cards/random');
        if (!response.ok) throw new Error('Failed to fetch card');
        const card = await response.json();
        setSelectedCard(card);
      } catch (error) {
        console.error(error);
        setMessage('ERROR PICKING CARD');
      } finally {
        setIsShuffling(false);
      }
    }, 2000);
  };

  const handleSave = async () => {
    if (!selectedCard || !journalContent.trim()) return;

    if (!isAuthenticated) {
      setPendingSave(true);
      openLogin();
      return;
    }

    setIsSaving(true);
    try {
      const response = await fetch('/api/entries', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: `Reading: ${selectedCard.name}`,
          content: journalContent,
          card_id: selectedCard.id,
        }),
      });

      if (!response.ok) throw new Error('Failed to save');

      setMessage('ENTRY RECORDED');
      setJournalContent('');
    } catch (error) {
      setMessage('ERROR SAVING ENTRY');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      {/* Left Column: Interactive Arena */}
      <div className="arena-column">
        <div className="brutal-card arena-container">
          {!selectedCard && !isShuffling && (
            <div className="deck-base">
              <button className="brutal-btn shuffle-trigger" onClick={handleShuffle}>
                SHUFFLE DECK
              </button>
            </div>
          )}

          <div className={`deck-arena ${isShuffling ? 'is-shuffling' : ''}`}>
            {!selectedCard && (
              <>
                <div className="hand-svg hand-left" style={{ width: '150px', height: '150px' }}>
                  <svg
                    viewBox="0 0 120 120"
                    fill="#F9FBFD"
                    stroke="#111111"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    style={{ filter: 'drop-shadow(2px 4px 6px rgba(0,0,0,0.15))' }}
                  >
                    <path d="
                      M 95,95 
                      C 95,110 75,115 55,105 
                      C 35,95 20,70 15,55 
                      C 10,45 15,35 25,38 
                      C 32,40 42,48 48,55 
                      C 43,38 30,18 42,12 
                      C 47,9 53,18 55,32 
                      C 56,16 62,5 69,10 
                      C 74,14 74,28 73,42 
                      C 76,26 84,14 91,20 
                      C 96,25 91,42 88,54 
                      C 93,44 104,38 108,45 
                      C 112,52 108,68 102,78 
                      Z"
                    />
                  </svg>
                </div>
                <div className="hand-svg hand-right" style={{ width: '150px', height: '150px' }}>
                  <svg
                    viewBox="0 0 120 120"
                    fill="#F9FBFD"
                    stroke="#111111"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    transform="scale(-1, 1)"
                    style={{ filter: 'drop-shadow(-2px 4px 6px rgba(0,0,0,0.15))' }}
                  >
                    <path d="
                      M 95,95 
                      C 95,110 75,115 55,105 
                      C 35,95 20,70 15,55 
                      C 10,45 15,35 25,38 
                      C 32,40 42,48 48,55 
                      C 43,38 30,18 42,12 
                      C 47,9 53,18 55,32 
                      C 56,16 62,5 69,10 
                      C 74,14 74,28 73,42 
                      C 76,26 84,14 91,20 
                      C 96,25 91,42 88,54 
                      C 93,44 104,38 108,45 
                      C 112,52 108,68 102,78 
                      Z"
                    />
                  </svg>
                </div>
              </>
            )}

            {isShuffling && (
              <div className="packets-container">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className={`brutal-card packet packet-${i}`} />
                ))}
              </div>
            )}

            {selectedCard && !isShuffling && (
              <div className="reveal-area animate-entry">
                <div className="brutal-card revealed-card-container">
                  <img
                    src={`/static/tarot_cards/${selectedCard.image_file}`}
                    alt={selectedCard.name}
                    className="revealed-card-img"
                  />
                </div>
                <div className="ai-insight-block">
                  <p className="insight-title">COSMIC INSIGHT: {selectedCard.name}</p>
                  <p className="insight-text">{selectedCard.meaning_upright}</p>
                </div>
                <button className="brutal-btn draw-again-btn" onClick={() => setSelectedCard(null)}>
                  DRAW AGAIN
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Right Column: Slate */}
      <div className="slate-column">
        <div className="brutal-card slate-container">
          <div className="ai-prompt-bubble">
            <span>AI: WHAT DOES THIS CARD REVEAL ABOUT YOUR JOURNEY?</span>
          </div>
          <textarea
            className="journal-textarea"
            value={journalContent}
            onChange={(e) => setJournalContent(e.target.value)}
            placeholder="RECORD YOUR REFLECTIONS..."
            disabled={!selectedCard || isShuffling}
          />
          <div className="slate-footer">
            <button
              className="brutal-btn save-btn"
              onClick={handleSave}
              disabled={isSaving || !journalContent.trim()}
            >
              {isSaving ? 'SAVING...' : 'SAVE ENTRY'}
            </button>
          </div>
        </div>
      </div>

      {message && <div className="brutal-status-toast">{message}</div>}
    </>
  );
};

export default TarotShuffle;
