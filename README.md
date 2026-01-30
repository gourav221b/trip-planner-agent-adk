# AI Trip Planner – Google ADK

This project implements two demo assistants using the Google Agent Development Kit (ADK).

- `personal_assistant/travel_orchestrator` (multi-stage travel planner) coordinates weather, safety, and itinerary specialists before producing a structured trip brief.
- `celebration_planner/celebration_orchestrator` (parallel celebration planner) showcases how ADK's `ParallelAgent` can fan out to multiple creative micro-agents at once before synthesising the results.

## Features
- **Agent orchestration**: A root assistant delegates to weather, local news, official advisory, and itinerary planning agents.
- **Data fetchers**: Lightweight Gemini 1.5 agents call custom tools to gather fresh weather forecasts (Open‑Meteo) and safety headlines (Google News RSS).
- **Risk awareness**: Local news and policy agents classify destinations (Safe/Caution/Avoid) and flag advisories, health notices, or disruptions.
- **Comprehensive output**: Final responses cover weather outlook, safety verdicts, packing guidance, travel routes, must‑see attractions, budget estimates, and legal requirements.
- **Extensible tools**: `personal_assistant/tools.py` includes reusable helpers for geocoding, weather summaries, and safety briefs.

## Project Structure
```
celebration_planner/
├── agent.py        # Celebration planner showcasing parallel agents
└── __init__.py

personal_assistant/
├── agent.py        # Defines travel orchestrator and specialised agents
├── tools.py        # Domain-specific tools for weather and safety data
└── __init__.py
```

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt  # (ensure google-adk and dependencies are available)
   ```
2. Export your Google Gemini credentials:
   ```bash
   export GOOGLE_API_KEY="YOUR_KEY"
   ```
3. Launch the ADK Dev UI (from the repo root so both agents are detected):
   ```bash
   adk web .
   ```
4. Interact with the **Personal Assistant** application, e.g.:
   ```
   "Plan a 5-day weekend trip to Sri Lanka starting from Kolkata next Friday."
   ```

### Parallel celebration planner quickstart

Try the new celebration agent to see parallel orchestration in action:
```
"I want to throw a cozy-but-fun engagement celebration for 20 guests in a New York loft. Budget $1500, need vegan-friendly bites, and quiet hours start at 11pm."
```

## Customisation Ideas
- Swap in additional fetcher agents (e.g., currency exchange, event calendars).
- Extend `tools.py` with region-specific APIs.
- Add persistence by saving agent artefacts or state between sessions.

## License
Licensed under the Apache License 2.0. See the LICENSE file for details.
