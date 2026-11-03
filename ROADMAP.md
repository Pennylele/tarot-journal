# Tarot Journal: Roadmap & Next Steps

## 📍 Current Project State
* **Backend:** FastAPI + SQLAlchemy (async) + PostgreSQL.
  * Full CRUD for journal entries, card lookup/randomizer, and JWT auth with Google SSO.
  * Card deck of 78 cards seeded with upright & reversed meanings.
* **Frontend:** React 19 + TypeScript + Vite with Neo-Brutalist design.
  * Interactive shuffle arena & card reveal.
  * Journal reflection recording slate with deferred auth.
  * Reading archives with time-filtering (All Time, 3 Days, Past Week, Past Month) and entry deletion.
* **Dev Workflow:** Unified root `package.json` with `concurrently` (`npm run dev`) and Python UTF-8 support.

---

## 🎯 Sprint 1: MVP Core Polish (Immediate Next Session)

These items close the remaining functional gaps before the application is complete as a daily driver.

### 1. Card Orientation (Upright vs. Reversed) - ✅ COMPLETED
* **Goal:** Allow users to choose between pulling *all upright* cards or *both upright and reversed* (50% chance).
* **Backend:**
  * Updated `/api/cards/random` to accept `allow_reversed: bool` (default `True`) and return `is_reversed: bool`.
  * Updated `Entry` model, `EntryBase`, `EntryCreate`, `EntryUpdate`, and `EntryResponse` to store and return `is_reversed: bool`.
  * Auto-migration safe column check added on FastAPI lifespan startup.
* **Frontend:**
  * Added Neo-Brutalist Deck Orientation mode toggle (`UPRIGHT ONLY` vs `UPRIGHT & REVERSED`) with `localStorage` persistence.
  * In `TarotShuffle.tsx`, if reversed:
    * Rotates revealed card image 180° with smooth transition.
    * Displays `meaning_reversed` instead of `meaning_upright`.
    * Shows `REVERSED ↺` orientation tag and customized AI reflection prompt.
  * Display reversed badge & rotated thumbnail in `JournalHistory.tsx` with reversed cosmic hints.

### 2. Edit Entry in UI - ✅ COMPLETED
* **Goal:** Enable users to edit their reflection text and title without affecting the historical integrity of the card drawn.
* **Backend:**
  * Powered by `PATCH /api/entries/{entry_id}` supporting partial updates (`title`, `content`).
* **Frontend:**
  * Added `✎` action icon button to each card in `JournalHistory.tsx`.
  * Inline editor with brutalist title input, expandable reflection textarea, validation, and Save/Cancel controls.
  * Instant local state update upon successful update with confirmation toast.

### 3. Toast Notifications Polish - ✅ COMPLETED
* Added active 3.5-second auto-dismiss lifecycle hooks (`useEffect` with timer cleanup) across [`TarotShuffle.tsx`](frontend/src/components/TarotShuffle.tsx) and [`JournalHistory.tsx`](frontend/src/components/JournalHistory.tsx).
* Added global Neo-Brutalist toast utilities in [`index.css`](frontend/src/index.css) with slide-up animation and manual `✕` dismiss buttons.
* Added automatic toasts for entry saves, updates, deletions, and error handling.

---

## 📊 Sprint 2: Pattern Analytics ("Cosmic Trends")

*Tarot practitioners love tracking recurring cards ("stalker cards") and dominant energies.*

### Proposed Features:
1. **Stalker Cards (Frequency Tracker):**
   * Top 3–5 most frequently drawn cards over the selected time window (e.g. *"Seven of Wands drawn 4x this month"*).
2. **Elemental / Suit Energy Balance:**
   * **Fire (Wands):** Passion, creativity, willpower, burnout.
   * **Water (Cups):** Emotions, intuition, relationships.
   * **Air (Swords):** Intellect, conflict, decision-making.
   * **Earth (Pentacles):** Career, finances, groundedness.
   * Visual progress bars showing percentage breakdown.
3. **Major vs. Minor Arcana Ratio:**
   * Highlights whether the user is navigating major life milestones or everyday situations.
4. **Backend Implementation:**
   * New endpoint: `GET /api/entries/analytics` using SQLAlchemy `GROUP BY` and aggregations over the user's entries.

---

## 🤖 Sprint 3: Generative AI Weekly Synthesis ("Cosmic Digest")

*Synthesize multiple readings and personal reflections into an overarching story.*

### Proposed Flow:
1. **Trigger:** User clicks *"✨ Synthesize My Week"* on the history page.
2. **Backend:** Aggregates the week's cards, orientations, and user journal reflections.
3. **LLM:** Prompts Gemini with structured guidance to weave the entries into an empathetic, insightful 3-paragraph narrative.
4. **UI:** Displays the synthesized weekly story with key advice moving forward.
