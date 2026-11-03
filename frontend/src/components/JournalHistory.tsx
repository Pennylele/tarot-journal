import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import './JournalHistory.css';

export interface TarotCard {
  id: number;
  name: string;
  slug: string;
  arcana: string;
  suit: string | null;
  meaning_upright: string;
  meaning_reversed: string;
  image_file: string | null;
}

export interface JournalEntry {
  id: string;
  title: string;
  content: string;
  card_id: number;
  is_reversed?: boolean;
  date_posted: string;
  card?: TarotCard | null;
}

type TimeFilter = 'all' | '3days' | 'week' | 'month';

interface JournalHistoryProps {
  onDrawNew: () => void;
}

const JournalHistory: React.FC<JournalHistoryProps> = ({ onDrawNew }) => {
  const { token, isAuthenticated, openLogin, logout } = useAuth();
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>('all');
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  // Inline editing state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const fetchEntries = async () => {
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await fetch('/api/entries', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        if (res.status === 401) {
          logout();
          openLogin();
          throw new Error('Your session expired. Please sign in again.');
        }
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `Failed to fetch journal entries (${res.status})`);
      }

      const data: JournalEntry[] = await res.json();
      setEntries(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error loading entries');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchEntries();
    } else {
      setEntries([]);
      setLoading(false);
    }
  }, [isAuthenticated, token]);

  // 3.5-second automatic dismiss timer for toast notifications
  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => {
        setToastMessage(null);
      }, 3500);
      return () => clearTimeout(timer);
    }
  }, [toastMessage]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError(null);
      }, 3500);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleDelete = async (entryId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Delete this journal reading permanently?')) return;

    try {
      setDeletingId(entryId);
      const res = await fetch(`/api/entries/${entryId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        if (res.status === 401) {
          logout();
          openLogin();
          throw new Error('Your session expired. Please sign in again.');
        }
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `Failed to delete entry (${res.status})`);
      }

      setEntries((prev) => prev.filter((item) => item.id !== entryId));
      if (editingId === entryId) {
        cancelEditing();
      }
      setToastMessage('READING DELETED');
    } catch (err: any) {
      alert(err.message || 'Error deleting entry');
    } finally {
      setDeletingId(null);
    }
  };

  const startEditing = (entry: JournalEntry, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(entry.id);
    setEditTitle(entry.title);
    setEditContent(entry.content);
  };

  const cancelEditing = () => {
    setEditingId(null);
    setEditTitle('');
    setEditContent('');
  };

  const handleUpdate = async (entryId: string) => {
    if (!editTitle.trim() || !editContent.trim()) {
      alert('Title and reflection cannot be empty.');
      return;
    }

    try {
      setIsUpdating(true);
      const res = await fetch(`/api/entries/${entryId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: editTitle.trim(),
          content: editContent.trim(),
        }),
      });

      if (!res.ok) {
        if (res.status === 401) {
          logout();
          openLogin();
          throw new Error('Your session expired. Please sign in again.');
        }
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `Failed to update entry (${res.status})`);
      }

      const updated: JournalEntry = await res.json();
      setEntries((prev) =>
        prev.map((item) => (item.id === entryId ? { ...item, ...updated } : item))
      );
      setEditingId(null);
      setToastMessage('READING UPDATED');
    } catch (err: any) {
      alert(err.message || 'Error updating entry');
    } finally {
      setIsUpdating(false);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  // Filter computations
  const now = Date.now();
  const countInWindow = (days: number | null) => {
    if (days === null) return entries.length;
    const cutoff = now - days * 24 * 60 * 60 * 1000;
    return entries.filter((e) => new Date(e.date_posted).getTime() >= cutoff).length;
  };

  const filterCounts = {
    all: entries.length,
    '3days': countInWindow(3),
    week: countInWindow(7),
    month: countInWindow(30),
  };

  const filteredEntries = entries.filter((entry) => {
    if (timeFilter === 'all') return true;
    const entryTime = new Date(entry.date_posted).getTime();
    const diffMs = now - entryTime;
    if (timeFilter === '3days') return diffMs <= 3 * 24 * 60 * 60 * 1000;
    if (timeFilter === 'week') return diffMs <= 7 * 24 * 60 * 60 * 1000;
    if (timeFilter === 'month') return diffMs <= 30 * 24 * 60 * 60 * 1000;
    return true;
  });

  if (!isAuthenticated) {
    return (
      <div className="journal-history-container">
        <div className="brutal-card unauth-card">
          <h2>YOUR JOURNAL AWAITS</h2>
          <p>Sign in to view your past tarot readings, reflection notes, and card history.</p>
          <button className="brutal-btn" onClick={openLogin}>
            SIGN IN / REGISTER
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="journal-history-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>CONSULTING THE ARCHIVES...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="journal-history-container">
      {/* Top Bar Controls */}
      <div className="journal-topbar">
        <div className="journal-heading">
          <h2>READING ARCHIVES</h2>
          <span className="entry-total-badge">{entries.length} READINGS RECORDED</span>
        </div>

        {/* Time Range Filter Pills */}
        <div className="filter-pills">
          <button
            className={`filter-pill ${timeFilter === 'all' ? 'active' : ''}`}
            onClick={() => setTimeFilter('all')}
          >
            ALL TIME ({filterCounts.all})
          </button>
          <button
            className={`filter-pill ${timeFilter === '3days' ? 'active' : ''}`}
            onClick={() => setTimeFilter('3days')}
          >
            PAST 3 DAYS ({filterCounts['3days']})
          </button>
          <button
            className={`filter-pill ${timeFilter === 'week' ? 'active' : ''}`}
            onClick={() => setTimeFilter('week')}
          >
            PAST WEEK ({filterCounts.week})
          </button>
          <button
            className={`filter-pill ${timeFilter === 'month' ? 'active' : ''}`}
            onClick={() => setTimeFilter('month')}
          >
            PAST MONTH ({filterCounts.month})
          </button>
        </div>
      </div>

      {error && (
        <div className="brutal-status-toast">
          <span>{error}</span>
          <button
            onClick={fetchEntries}
            style={{
              marginLeft: '0.5rem',
              background: 'white',
              color: 'black',
              border: 'none',
              padding: '0.35rem 0.75rem',
              fontWeight: 900,
              cursor: 'pointer',
              borderRadius: '4px',
            }}
          >
            RETRY
          </button>
          <button
            className="toast-close-btn"
            onClick={() => setError(null)}
            title="Dismiss notification"
          >
            ✕
          </button>
        </div>
      )}

      {toastMessage && (
        <div className="brutal-status-toast">
          <span>{toastMessage}</span>
          <button
            className="toast-close-btn"
            onClick={() => setToastMessage(null)}
            title="Dismiss notification"
          >
            ✕
          </button>
        </div>
      )}

      {/* Empty State */}
      {filteredEntries.length === 0 ? (
        <div className="brutal-card empty-card">
          <h3>NO READINGS FOUND</h3>
          <p>
            {entries.length === 0
              ? 'You have not recorded any readings yet. Draw your first card to begin your journal!'
              : `No entries logged in this time range.`}
          </p>
          <button className="brutal-btn" onClick={onDrawNew}>
            DRAW A CARD NOW
          </button>
        </div>
      ) : (
        /* Card Grid Layout */
        <div className="entries-grid">
          {filteredEntries.map((entry) => {
            const isEditing = editingId === entry.id;
            const isExpanded = expandedIds.has(entry.id);
            const isLong = entry.content.length > 220;

            return (
              <div key={entry.id} className={`brutal-card entry-card ${isEditing ? 'is-editing' : ''}`}>
                {/* Header: Date, Orientation + Actions */}
                <div className="entry-card-header">
                  <div className="entry-card-badges">
                    <span className="date-badge">{formatDate(entry.date_posted)}</span>
                    <span className={`history-orientation-badge ${entry.is_reversed ? 'reversed' : 'upright'}`}>
                      {entry.is_reversed ? 'REVERSED ↺' : 'UPRIGHT ⇡'}
                    </span>
                  </div>

                  <div className="entry-card-actions">
                    {!isEditing && (
                      <button
                        className="edit-entry-btn"
                        title="Edit title & reflection"
                        disabled={deletingId === entry.id || isUpdating}
                        onClick={(e) => startEditing(entry, e)}
                      >
                        ✎
                      </button>
                    )}
                    <button
                      className="delete-entry-btn"
                      title="Delete reading"
                      disabled={deletingId === entry.id || isUpdating}
                      onClick={(e) => handleDelete(entry.id, e)}
                    >
                      {deletingId === entry.id ? '...' : '✕'}
                    </button>
                  </div>
                </div>

                {/* Card Info & Thumbnail */}
                <div className="entry-card-body">
                  {entry.card?.image_file && (
                    <div className="entry-thumbnail-wrapper">
                      <img
                        src={`/static/tarot_cards/${entry.card.image_file}`}
                        alt={entry.card.name}
                        className={`entry-thumbnail ${entry.is_reversed ? 'is-reversed' : ''}`}
                      />
                    </div>
                  )}

                  <div className="entry-details">
                    <div className="card-arcana-tag">
                      {entry.card?.arcana ? `${entry.card.arcana} ARCANA` : 'TAROT'}
                      {entry.card?.suit ? ` • ${entry.card.suit}` : ''}
                    </div>

                    {isEditing ? (
                      <div className="edit-field-group">
                        <label className="edit-field-label">TITLE</label>
                        <input
                          type="text"
                          className="edit-title-input"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          maxLength={100}
                          disabled={isUpdating}
                          placeholder="Reading title..."
                        />
                      </div>
                    ) : (
                      <h3 className="entry-card-title">{entry.title || entry.card?.name}</h3>
                    )}

                    {(entry.is_reversed ? entry.card?.meaning_reversed : entry.card?.meaning_upright) && (
                      <p className="entry-cosmic-hint">
                        "{entry.is_reversed ? entry.card?.meaning_reversed : entry.card?.meaning_upright}"
                      </p>
                    )}
                  </div>
                </div>

                {/* Reflection Notes or Inline Editor */}
                {isEditing ? (
                  <div className="entry-edit-box">
                    <label className="edit-field-label">YOUR REFLECTION</label>
                    <textarea
                      className="edit-reflection-textarea"
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      disabled={isUpdating}
                      placeholder="Update your reflections..."
                      rows={6}
                    />
                    <div className="edit-actions-bar">
                      <button
                        type="button"
                        className="brutal-btn cancel-edit-btn"
                        onClick={cancelEditing}
                        disabled={isUpdating}
                      >
                        CANCEL
                      </button>
                      <button
                        type="button"
                        className="brutal-btn save-edit-btn"
                        onClick={() => handleUpdate(entry.id)}
                        disabled={isUpdating || !editTitle.trim() || !editContent.trim()}
                      >
                        {isUpdating ? 'SAVING...' : 'SAVE CHANGES'}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="entry-reflection-box">
                    <div className="reflection-label">YOUR REFLECTION</div>
                    <p className="reflection-text">
                      {isLong && !isExpanded ? `${entry.content.slice(0, 220)}...` : entry.content}
                    </p>
                    {isLong && (
                      <button
                        className="expand-text-btn"
                        onClick={() => toggleExpand(entry.id)}
                      >
                        {isExpanded ? 'Show Less ↑' : 'Read Full Note ↓'}
                      </button>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default JournalHistory;
