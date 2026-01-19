"""Multi-agent travel orchestration using Google ADK."""

from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool
from personal_assistant.tools import fetch_safety_brief
from personal_assistant.tools import fetch_weather_summary

weather_intel_tool = FunctionTool(fetch_weather_summary)
safety_intel_tool = FunctionTool(fetch_safety_brief)

weather_data_agent = Agent(
    model='gemini-2.5-flash',
    name='weather_data_agent',
    description='Retrieves structured weather data for downstream reasoning.',
    instruction=(
        "Call `fetch_weather_summary` immediately using the trip destination and desired coverage window.\n"
        "- Return a compact JSON block capturing current conditions, 5-day outlook, UV, wind, and any notable "
        "alerts.\n"
        "- Do not interpret or summarize; provide raw but tidy data for the next agent.\n"
        "- When finished, call `transfer_to_agent` to hand control back to `travel_orchestrator`."
    ),
    tools=[weather_intel_tool],
)

weather_agent = Agent(
    model='gemini-2.5-flash',
    name='weather_intel_agent',
    description='Weather intelligence analyst for trip planning.',
    instruction=(
        "You are responsible for gathering weather intelligence for trip plans.\n"
        "- Use the structured weather data provided by `weather_data_agent` along with user context.\n"
        "- Focus on the travel dates or trip length provided.\n"
        "- Translate raw data into actionable guidance: packing tips, risky weather windows, "
        "and timing suggestions.\n"
        "- Raise flags for severe weather, storms, heat waves, or precipitation spikes.\n"
        "- Return concise bullet points grouped by `Current`, `Daily Outlook`, and `Implications`.\n"
        "- Once your analysis is complete, call `transfer_to_agent` to hand control back to "
        "`travel_orchestrator` without issuing a final user-facing answer."
    ),
)

safety_agent = Agent(
    model='gemini-2.5-flash',
    name='safety_watch_agent',
    description='Monitors safety advisories, disruptions, and major events.',
    instruction=(
        "You focus on official advisories and high-impact alerts.\n"
        "- Build on the latest local incident feed and any prior context to surface credible advisories, "
        "entry requirements, health notices, or geopolitical risks.\n"
        "- Highlight severity, credibility of information, and required actions for travelers.\n"
        "- Coordinate with findings from local news analysts to present a consistent risk picture.\n"
        "- After delivering your findings, immediately call `transfer_to_agent` to return control to "
        "`travel_orchestrator`."
    ),
)

local_news_fetch_agent = Agent(
    model='gemini-2.5-flash',
    name='local_news_fetch_agent',
    description='Fetches recent news headlines for the destination.',
    instruction=(
        "Immediately call `fetch_safety_brief` with the destination (and default parameters).\n"
        "- Return a concise JSON payload listing the most relevant headlines (title, link, snippet, date).\n"
        "- Do not add interpretation; the next agent will assess risk levels.\n"
        "- After returning the data, call `transfer_to_agent` to hand control back to `travel_orchestrator`."
    ),
    tools=[safety_intel_tool],
)

local_news_agent = Agent(
    model='gemini-2.5-flash',
    name='local_news_safety_agent',
    description='Scans local news to assess on-the-ground safety conditions.',
    instruction=(
        "You determine local situational safety using fresh news coverage.\n"
        "- Analyze the structured feed provided by `local_news_fetch_agent` and any additional context.\n"
        "- Classify the destination as `Safe`, `Caution`, or `Avoid` with a short justification "
        "based on news evidence.\n"
        "- Provide a concise briefing with concrete incidents, dates, and recommended traveler actions.\n"
        "- When you finish, call `transfer_to_agent` to give control back to `travel_orchestrator`."
    ),
)

trip_planner_agent = Agent(
    model='gemini-2.5-pro',
    name='trip_planner_agent',
    description='Designs itineraries before, during, and after the trip.',
    instruction=(
        "Craft the end-to-end travel plan using previously gathered weather and safety findings.\n"
        "- Structure the output with sections: `Before Departure`, `During Trip`, `After Return`.\n"
        "- Tailor recommendations to the trip length (weekend, short, long) and user preferences.\n"
        "- Integrate weather alerts and safety advisories into scheduling and packing guidance.\n"
        "- Suggest logistics (transport, lodging checks, reservations) and enrichment ideas.\n"
        "- Highlight contingency plans or alternative activities when needed.\n"
        "- Prepare concise notes for: packing checklist, travel routes from the origin, must-see landmarks, "
        "baseline budget ranges, and legal or documentation requirements.\n"
        "- After you have drafted the trip blueprint, call `transfer_to_agent` to return control to "
        "`travel_orchestrator` for the final synthesis."
    ),
)

root_agent = Agent(
    model='gemini-2.5-pro',
    name='travel_orchestrator',
    description='Coordinates specialized agents to deliver full travel plans.',
    instruction=(
        "You are the personal travel assistant orchestrator.\n"
        "Workflow:\n"
        "1. Gather clarifying details (destination, travel dates/length, travelers, preferences). "
        "Ask follow-up questions once if critical information is missing.\n"
        "2. Delegate to `weather_data_agent` to obtain structured meteorological data.\n"
        "3. Delegate to `weather_intel_agent` to translate that data into implications.\n"
        "4. Delegate to `local_news_fetch_agent` to gather recent incident headlines.\n"
        "5. Delegate to `local_news_safety_agent` for on-the-ground safety classification.\n"
        "6. Delegate to `safety_watch_agent` for official advisories and policy guidance.\n"
        "7. Delegate to `trip_planner_agent` to synthesize the itinerary.\n"
        "8. Conclude with a polished response summarizing key insights and next actions, explicitly covering:\n"
        "   • Approximate weather conditions for the travel window.\n"
        "   • Safety level assessment (e.g., Safe/Caution/Avoid) with justification.\n"
        "   • Packing guidance highlighting what to take.\n"
        "   • Primary travel route from the stated origin to the destination.\n"
        "   • Must-visit attractions or experiences.\n"
        "   • Rough budget expectations (e.g., transport, lodging, daily spend).\n"
        "   • Legal or regulatory requirements (visas, permits, local laws).\n"
        "Follow this sequence strictly: call `transfer_to_agent` to `weather_data_agent`, then "
        "`weather_intel_agent`, `local_news_fetch_agent`, `local_news_safety_agent`, `safety_watch_agent`, "
        "and finally `trip_planner_agent`. Provide each agent with the distilled context they need. After each "
        "agent finishes and returns control, continue orchestrating the next step.\n"
        "Ensure each sub-agent is invoked when their expertise is needed. "
        "Do not produce the final plan until the trip planner agent has responded."
    ),
    sub_agents=[
        weather_data_agent,
        weather_agent,
        local_news_fetch_agent,
        local_news_agent,
        safety_agent,
        trip_planner_agent,
    ],
)
