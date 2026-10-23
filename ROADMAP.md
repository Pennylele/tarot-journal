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

### 1. Card Orientation (Upright vs. Reversed)
* **Goal:** Reversals provide critical contrast in tarot readings (50% of practical tarot).
* **Backend:**
  * Update `/api/cards/random` to return an `is_reversed: bool` flag (50% probability).
  * Update `Entry` model and `EntryResponse` to store and return `is_reversed: bool`.
* **Frontend:**
  * In `TarotShuffle.tsx`, if reversed:
    * Apply CSS `transform: rotate(180deg)` to the revealed card image.
    * Display `selectedCard.meaning_reversed` instead of `meaning_upright`.
    * Tag the insight as `COSMIC INSIGHT (REVERSED)`.
  * Display reversed badge & rotated thumbnail in `JournalHistory.tsx`.

### 2. Edit Entry in UI
* **Goal:** Enable users to edit their reflection text or title.
* **Backend:**
  * Already built at `update_entry_partial` (`PATCH /api/entries/{entry_id}`).
* **Frontend:**
  * Add an `Edit` action icon button to each card in `JournalHistory.tsx`.
  * Inline editing mode or modal popup to update reflection notes without re-drawing.

### 3. Toast Notifications Polish
* Add a 3.5-second automatic dismiss timer for toast notifications across the UI.

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
