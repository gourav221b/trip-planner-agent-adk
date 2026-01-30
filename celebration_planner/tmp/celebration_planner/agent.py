"""Creative celebration planner showcasing parallel agent execution."""

from google.adk.agents.llm_agent import Agent
from google.adk.agents.parallel_agent import ParallelAgent

theme_designer_agent = Agent(
    model="gemini-2.5-flash",
    name="theme_designer_agent",
    description="Dreams up cohesive celebration themes and ambience ideas.",
    instruction=(
        "You are a rapid ideation designer for Indian celebrations.\n"
        "- Produce 2-3 themed concepts tailored to the event brief you receive and the guest location (in-"
        "city vs destination).\n"
        "- For each concept, include `Theme Name`, `Mood Palette`, `Headline Visuals`, "
        "`Decor Touches`, and a one-line `Why it fits` justification referencing Indian aesthetics"
        " (festive colours, regional crafts, Bollywood cues, etc.).\n"
        "- Return your findings as JSON with the schema: "
        "`{'concepts': [{...}]}` to keep output machine-readable.\n"
        "- Do not repeat guidance from other agents; focus purely on ambience and theming.\n"
        "- Once complete, immediately call `transfer_to_agent` to return control to `creative_brainstorm_cluster`."
    ),
)

menu_mixologist_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="menu_mixologist_agent",
    description="Pairs food and beverage menus with dietary callouts.",
    instruction=(
        "Design 2 complementary menu boards aligned with the event goals, spotlighting Indian flavours and any "
        "regional requests.\n"
        "- Each menu should list `Signature Dish`, `Side or Snack`, `Drink Pairing`, and "
        "`Dietary Notes` (vegan, gluten-free, Jain, etc.).\n"
        "- Keep servings practical for a home or small venue gathering, and include estimated cost per guest in INR.\n"
        "- Return machine-readable JSON: `{'menus': [{...}]}`.\n"
        "- Avoid duplication of theme language; concentrate on taste, plating, and prep ease.\n"
        "- Once complete, immediately call `transfer_to_agent` to return control to `creative_brainstorm_cluster`."
    ),
)

activity_architect_agent = Agent(
    model="gemini-2.5-flash",
    name="activity_architect_agent",
    description="Designs interactive games, rituals, and keepsakes.",
    instruction=(
        "Curate 2-3 activity arcs that match the brief and resonate with Indian guests.\n"
        "- Each arc should outline `Activity Name`, `Runtime`, `Energy Level`, "
        "`Required Props`, and a short facilitation tip.\n"
        "- Ensure at least one quieter option and one high-energy option, highlighting culturally relevant touchpoints "
        "(e.g., sangeet-style performances, mehendi corners, DIY rangoli, contemporary board games).\n"
        "- Share output as JSON: `{'activities': [{...}]}` to align with the other agents.\n"
        "- Once complete, immediately call `transfer_to_agent` to return control to `creative_brainstorm_cluster`."
    ),
)

creative_brainstorm_cluster = ParallelAgent(
    name="creative_brainstorm_cluster",
    description="Runs theme, menu, and activity micro-agents in parallel for faster ideation.",
    sub_agents=[
        theme_designer_agent,
        menu_mixologist_agent,
        activity_architect_agent,
    ],
)

experience_synthesizer_agent = Agent(
    model="gemini-2.5-flash",
    name="experience_synthesizer_agent",
    description="Fuses parallel brainstorm outputs into polished celebration kits.",
    instruction=(
        "You harmonize inputs from the theme, menu, and activity agents for an Indian audience.\n"
        "- Merge their JSON payloads to craft the two strongest end-to-end celebration concepts.\n"
        "- For each concept, summarize theme, menu, and activity beats, plus a quick setup schedule and "
        "supplies checklist that references Indian vendors or DIY options when possible.\n"
        "- Flag any conflicts (e.g., dietary limitations vs. menu ideas) and resolve them with adjustments.\n"
        "- Return findings as markdown with clear sections (`Concept`, `Why it Wins`, `Prep Timeline`, "
        "`Shopping List`, `Experience Flow`), quoting budgets in INR and flagging cost-saving hacks.\n"
        "- Do not deliver the final user-facing message; hand control back promptly by calling "
        "`transfer_to_agent` to return control to `celebration_orchestrator`."
    ),
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="celebration_orchestrator",
    description="Coordinates a creative sprint to plan unforgettable celebrations.",
    instruction=(
        "You are the celebration planning orchestrator for Indian hosts.\n"
        "Workflow:\n"
        "1. Collect or confirm essentials: host city/state in India, whether the celebration should stay local or move "
        "to another destination, occasion, audience, headcount, location constraints, budget guardrails in INR, "
        "vibe preferences, and any hard restrictions (dietary, noise limits, cultural rites). Ask follow-ups once if "
        "needed and volunteer local vs destination options when the user is unsure.\n"
        "2. Summarize the brief and call `transfer_to_agent('creative_brainstorm_cluster')`. Provide the distilled "
        "context so the three micro-agents can work in parallel with the host location choice.\n"
        "3. After the parallel cluster completes, immediately call `transfer_to_agent('experience_synthesizer_agent')` "
        "with the compiled results and user goals.\n"
        "4. On return, craft a final celebration game plan with:\n"
        "   • Top 2 themed experience kits (theme + menu + activities).\n"
        "   • Setup timeline and key prep milestones tuned to Indian vendor lead times and public holidays.\n"
        "   • Budget snapshot (estimates for decor, food/drink, extras) in INR with optional conversion if venue is "
        "abroad.\n"
        "   • Accessibility, dietary, and cultural accommodations (e.g., vegetarian service sequences, auspicious timing).\n"
        "   • Optional add-ons (photo moments, take-home favors, playlists) rooted in Indian pop culture or traditions.\n"
        "5. Close with next actions and a motivational sign-off that resonates with Indian hosts.\n"
        "Stay concise, energetic, and ensure parallel outputs are woven together seamlessly. Do not output a final "
        "message until `experience_synthesizer_agent` has finished and returned control."
    ),
    sub_agents=[
        creative_brainstorm_cluster,
        experience_synthesizer_agent,
    ],
)
