"""Deterministic, hand-written themed content ("golden content").

This module serves three purposes:
1. Fallback generator so the full learning loop works with no API key.
2. Quality bar + few-shot reference for the LLM generator (same schemas).
3. Deterministic fixture for tests.

Content currently covers the vertical slice (variables, conditionals, loops)
in four themes. The LLM generator covers arbitrary themes and modules.
"""
from __future__ import annotations

import re

from ..schemas import (
    Feedback,
    FinalChallenge,
    HiddenTest,
    MentorCharacter,
    Mission,
    MissionArcEntry,
    MissionWithSolution,
    NextMissionRules,
    Remediation,
    StoryArc,
    StoryContext,
    StudentProfileIn,
)

_DIFFICULTY_SHIFT = {"gentle": -1, "standard": 0, "challenging": 1}


def _clamp(d: int) -> int:
    return max(1, min(5, d))


# ---------------------------------------------------------------------------
# Theme packs
# ---------------------------------------------------------------------------
# Each mission entry holds the story + exercise material for one concept.
# `previous_state` for mission N+1 is wired to mission N's success story
# feedback at build time, so the narrative is a chain, not isolated wrappers.

THEMES: dict[str, dict] = {
    "space": {
        "keywords": ["space", "rocket", "astronaut", "planet", "star", "sci-fi", "scifi", "nasa", "galaxy"],
        "arc": {
            "story_title": "The Wanderer: Signal in the Dark",
            "protagonist_role": "Junior flight engineer of the deep-space ship Wanderer",
            "world_description": (
                "The Wanderer is a long-haul research ship three months from the nearest "
                "station, crewed by four people and one ship AI. Out here, every system "
                "that works was made to work by an engineer — and right now, that engineer is {name}."
            ),
            "central_conflict": (
                "An asteroid storm has knocked out the Wanderer's core systems. Life support, "
                "power routing and navigation are all dark, and Kepler Station is too far away to help."
            ),
            "main_goal": "Bring the ship's systems back online, one by one, and reach Kepler Station safely.",
            "mentor": {
                "name": "ARIA",
                "role": "The ship's AI — part co-pilot, part patient teacher",
                "personality": "Calm, dry-humoured, endlessly encouraging; explains everything twice without ever sounding bored.",
            },
            "opening_state": "Alarms have just gone quiet. The Wanderer drifts in the dark after the asteroid storm, every console blank.",
            "final_challenge": "Dock with Kepler Station: combine stored readings, docking decisions and automated thruster sequences in one final program.",
        },
        "missions": {
            "variables": {
                "title": "Restore the Life-Support Readouts",
                "story_purpose": "Re-awaken the ship's memory: stored values are how the Wanderer knows itself.",
                "current_problem": "The life-support console is blank. The ship has forgotten its own oxygen level, its name, even how many crew it carries.",
                "why_this_matters": "Every system on the ship reads these stored values. Until they exist, nothing else can be repaired.",
                "narrative_stakes": "Without a trusted oxygen readout, the crew must stay in emergency suits — and the suits have six hours left.",
                "themed_tie_in": "On the Wanderer, variables are the ship's memory banks: each named value is a readout another system depends on.",
                "student_task": (
                    "ARIA needs you to restore three memory banks. Create a variable `oxygen_level` "
                    "with the value 100, a variable `ship_name` with the value \"Wanderer\", and a "
                    "variable `crew_count` with the value 4."
                ),
                "starter_code": (
                    "# Life-support memory banks — restore each one.\n"
                    "# ARIA: \"A variable is just a name pointing at a value: name = value\"\n\n"
                    "# 1. oxygen_level should be 100\n\n# 2. ship_name should be \"Wanderer\"\n\n# 3. crew_count should be 4\n"
                ),
                "expected_solution_description": "Three assignment statements creating oxygen_level, ship_name and crew_count with the exact required values.",
                "reference_solution": 'oxygen_level = 100\nship_name = "Wanderer"\ncrew_count = 4\n',
                "hidden_tests": [
                    ("oxygen_level == 100", "oxygen_level holds 100"),
                    ('ship_name == "Wanderer"', 'ship_name holds the text "Wanderer"'),
                    ("crew_count == 4", "crew_count holds 4"),
                ],
                "hints": [
                    "An assignment puts the name on the left and the value on the right: score = 10.",
                    "Numbers are written plain (100), text needs quotes (\"Wanderer\").",
                    "You need exactly three lines: oxygen_level = 100, ship_name = \"Wanderer\", crew_count = 4.",
                ],
                "success_story": "The life-support console flickers green. ARIA: \"Memory banks restored. The ship knows itself again — and the crew can take their helmets off.\"",
                "failure_story": "The console stays dark. ARIA: \"One of the memory banks still reads empty or wrong. Check each stored value against what I asked for.\"",
                "success_tech": "All three variables exist with the correct values. Assignment with = is the foundation of everything that follows.",
                "failure_tech": "At least one variable is missing or holds the wrong value. Remember: name = value, numbers without quotes, text with quotes.",
                "remediation": {
                    "simpler_explanation": "Think of a variable as a labelled box. `oxygen_level = 100` writes 'oxygen_level' on a box and puts 100 inside. Reading the name later gives you what's in the box.",
                    "smaller_subtask": "Start with just one box: write the single line `oxygen_level = 100` and run the tests. Then add the other two.",
                },
            },
            "conditionals": {
                "title": "Route the Emergency Power",
                "story_purpose": "Give the ship judgement: decisions are how the Wanderer reacts to a changing situation.",
                "current_problem": "Three reactors report power readings, but the routing computer can't decide which are safe to use.",
                "why_this_matters": "Routing power from an unstable reactor could blow the grid; ignoring a stable one wastes power the ship needs to move.",
                "narrative_stakes": "If power isn't routed before the next debris wave, the shields stay down.",
                "themed_tie_in": "On the Wanderer, conditionals are the routing computer's judgement: compare a reading against a threshold and choose a path.",
                "student_task": (
                    "The readings are already stored: reactor_a = 85, reactor_b = 40, reactor_c = 12. "
                    "For EACH reactor, write an if/elif/else that stores its status: \"stable\" when the "
                    "reading is 70 or more, \"low\" when it is 30 or more, otherwise \"critical\". "
                    "Store the answers in status_a, status_b and status_c."
                ),
                "starter_code": (
                    "# Reactor readings from the sensors — do not change these.\n"
                    "reactor_a = 85\nreactor_b = 40\nreactor_c = 12\n\n"
                    "# ARIA: \"70 or more is stable, 30 or more is low, anything else is critical.\"\n"
                    "# Decide status_a from reactor_a:\n\n# Decide status_b from reactor_b:\n\n# Decide status_c from reactor_c:\n"
                ),
                "expected_solution_description": "Three if/elif/else blocks (one per reactor) assigning \"stable\", \"low\" or \"critical\" to status_a, status_b, status_c based on the thresholds.",
                "reference_solution": (
                    "reactor_a = 85\nreactor_b = 40\nreactor_c = 12\n"
                    'if reactor_a >= 70:\n    status_a = "stable"\nelif reactor_a >= 30:\n    status_a = "low"\nelse:\n    status_a = "critical"\n'
                    'if reactor_b >= 70:\n    status_b = "stable"\nelif reactor_b >= 30:\n    status_b = "low"\nelse:\n    status_b = "critical"\n'
                    'if reactor_c >= 70:\n    status_c = "stable"\nelif reactor_c >= 30:\n    status_c = "low"\nelse:\n    status_c = "critical"\n'
                ),
                "hidden_tests": [
                    ('status_a == "stable"', "reactor A (85) is classified as stable"),
                    ('status_b == "low"', "reactor B (40) is classified as low"),
                    ('status_c == "critical"', "reactor C (12) is classified as critical"),
                ],
                "hints": [
                    "An if statement looks like: if reading >= 70: (note the colon), with the assignment indented underneath.",
                    "Use elif for the middle case (>= 30) and else for everything below it — order matters.",
                    "Repeat the same if/elif/else three times, once per reactor: check reactor_a to set status_a, and so on. (Tedious, right? ARIA says the next system fixes that.)",
                ],
                "success_story": "Power hums through the ship as the grid lights up deck by deck. ARIA: \"Routing logic accepted. The Wanderer can make decisions again — shields are back.\"",
                "failure_story": "The routing computer rejects the plan and the lights stutter. ARIA: \"One of the reactors is mis-classified. Walk through my thresholds again, top to bottom.\"",
                "success_tech": "Your if/elif/else branches classify all three readings correctly. Threshold order (highest first) is what makes this work.",
                "failure_tech": "At least one status is wrong or missing. Check: == vs =, the colon at the end of each condition, the indentation of each assignment, and that thresholds go highest first.",
                "remediation": {
                    "simpler_explanation": "A conditional reads top to bottom and takes the FIRST branch whose condition is True. `if x >= 70` catches big values, `elif x >= 30` catches middle ones, `else` catches the rest.",
                    "smaller_subtask": "Forget B and C for a moment. Write only the if/elif/else for reactor_a so that status_a becomes \"stable\", and run the tests — one will pass.",
                },
            },
            "loops": {
                "title": "Scan the Asteroid Field",
                "story_purpose": "Teach the ship to repeat itself: automation is how one engineer handles a thousand rocks.",
                "current_problem": "Navigation needs the total mass of the debris field ahead, but the scanner only reports one asteroid at a time.",
                "why_this_matters": "Plotting a course through the field requires the total mass — and nobody is adding hundreds of readings by hand.",
                "narrative_stakes": "Until the course is plotted, the Wanderer drifts — and Kepler Station's docking window is closing.",
                "themed_tie_in": "On the Wanderer, a loop is the scanner sweep: the same step repeated for every object the sensors find.",
                "student_task": (
                    "The scanner readings are in the list asteroid_sizes. Use a for loop to add every "
                    "size into a variable `total_mass` (start it at 0), and count the readings in a "
                    "variable `scanned` (also starting at 0)."
                ),
                "starter_code": (
                    "# Scanner readings — do not change this list.\n"
                    "asteroid_sizes = [4, 8, 15, 16, 23]\n\n"
                    "# ARIA: \"Start your totals at zero, then let the loop do the adding.\"\n"
                    "total_mass = 0\nscanned = 0\n\n# your for loop here:\n"
                ),
                "expected_solution_description": "A for loop over asteroid_sizes that accumulates the sum into total_mass and increments scanned once per item.",
                "reference_solution": (
                    "asteroid_sizes = [4, 8, 15, 16, 23]\n"
                    "total_mass = 0\nscanned = 0\n"
                    "for size in asteroid_sizes:\n    total_mass = total_mass + size\n    scanned = scanned + 1\n"
                ),
                "hidden_tests": [
                    ("total_mass == 66", "total_mass is the sum of all readings (66)"),
                    ("scanned == 5", "scanned counts all five readings"),
                ],
                "hints": [
                    "A for loop visits each item: for size in asteroid_sizes: — everything indented under it runs once per asteroid.",
                    "Inside the loop, grow the total with total_mass = total_mass + size.",
                    "Add a second indented line, scanned = scanned + 1, so the counter goes up once per reading.",
                ],
                "success_story": "The scanner sweeps the whole field in seconds and a safe course draws itself across the star chart. ARIA: \"Course plotted. Kepler Station, here we come — you just automated your first system, engineer.\"",
                "failure_story": "The course plotter spits out an error: the totals don't match the field. ARIA: \"Either the sweep missed rocks or it counted wrong. Check what happens inside your loop.\"",
                "success_tech": "Your accumulator pattern is correct: initialize before the loop, update inside it. This pattern powers almost every data-processing program you'll ever write.",
                "failure_tech": "total_mass or scanned is wrong. Make sure both start at 0 BEFORE the loop, and both updates are INDENTED so they run inside it.",
                "remediation": {
                    "simpler_explanation": "A for loop is 'do this once per item'. With [4, 8] the body runs twice: first size is 4, then size is 8. If total starts at 0 and you add size each time, it ends at 12.",
                    "smaller_subtask": "Ignore the counter. Write just the loop that builds total_mass, run the tests, and watch the first one pass. Then add scanned.",
                },
            },
        },
    },
    "football": {
        "keywords": ["football", "soccer", "futebol", "fifa", "league", "striker", "goal", "club"],
        "arc": {
            "story_title": "Vale FC: The Last Season",
            "protagonist_role": "Newly appointed head coach of Vale FC",
            "world_description": (
                "Vale FC is a small club with a loud crowd and an empty trophy cabinet, sitting "
                "bottom of the league in {name}'s first season as head coach. The board has made "
                "it simple: turn the season around, or the club goes down."
            ),
            "central_conflict": "The club's old planning systems are chaos — no team sheet, no tactics, no training plan. Relegation is twelve matches away.",
            "main_goal": "Rebuild the club's match-day systems step by step and survive the season.",
            "mentor": {
                "name": "Marta",
                "role": "Club captain and veteran of 400 matches",
                "personality": "Blunt, loyal, allergic to excuses; explains football — and everything else — with total clarity.",
            },
            "opening_state": "It's {name}'s first morning at Vale FC. The whiteboard in the coach's office is blank and the season starts Saturday.",
            "final_challenge": "Match day against the league leaders: combine the team sheet, live tactical decisions and automated training stats in one final program.",
        },
        "missions": {
            "variables": {
                "title": "Set Up the Team Sheet",
                "story_purpose": "Give the club a memory: the team sheet is the single source of truth everything else reads.",
                "current_problem": "The league portal rejected Vale FC's registration — the club never stored its basic details.",
                "why_this_matters": "Tactics, substitutions and training plans all read from the team sheet. No stored values, no season.",
                "narrative_stakes": "If the sheet isn't filed by Saturday, Vale FC forfeits the opening match.",
                "themed_tie_in": "At a football club, variables are the team sheet: each named value is a fact the whole club relies on.",
                "student_task": (
                    "Marta slides the registration form across the desk. Create a variable `team_name` "
                    "with the value \"Vale FC\", a variable `points` with the value 0, and a variable "
                    "`players_available` with the value 11."
                ),
                "starter_code": (
                    "# Vale FC registration — fill in the team sheet.\n"
                    "# Marta: \"Name on the left, value on the right. Like a team sheet.\"\n\n"
                    "# 1. team_name should be \"Vale FC\"\n\n# 2. points should be 0\n\n# 3. players_available should be 11\n"
                ),
                "expected_solution_description": "Three assignments creating team_name, points and players_available with the exact required values.",
                "reference_solution": 'team_name = "Vale FC"\npoints = 0\nplayers_available = 11\n',
                "hidden_tests": [
                    ('team_name == "Vale FC"', 'team_name holds "Vale FC"'),
                    ("points == 0", "points starts at 0"),
                    ("players_available == 11", "players_available holds 11"),
                ],
                "hints": [
                    "Assignment is name = value — the name goes on the left.",
                    "Text values like \"Vale FC\" need quotes; numbers like 0 and 11 don't.",
                    "Three lines: team_name = \"Vale FC\", then points = 0, then players_available = 11.",
                ],
                "success_story": "The league portal turns green: REGISTRATION ACCEPTED. Marta nods once — from her, that's a standing ovation. Vale FC plays Saturday.",
                "failure_story": "The portal flags the form in red. Marta squints at the screen: \"One of these entries is empty or wrong, coach. Check them against what I gave you.\"",
                "success_tech": "All three variables exist with the right values. Assignment is the foundation — every system you build this season reads these names.",
                "failure_tech": "At least one variable is missing or wrong. Remember: name = value, quotes around text, none around numbers.",
                "remediation": {
                    "simpler_explanation": "A variable is a labelled slot on the team sheet. `points = 0` writes 'points' on a slot and puts 0 in it. Whenever the club needs the points total, it reads that slot.",
                    "smaller_subtask": "Fill in one slot first: write only `points = 0`, run the tests, and watch one turn green. Then do the other two.",
                },
            },
            "conditionals": {
                "title": "Half-Time Tactics",
                "story_purpose": "Give the bench judgement: tactics are decisions made from the scoreline.",
                "current_problem": "Three match reports are on the desk, and the tactics board needs a call for each: protect the lead, stay balanced, or chase the game.",
                "why_this_matters": "The right tactic comes from reading the scoreline the same way every time — a rule, not a mood.",
                "narrative_stakes": "Get the calls wrong and Vale FC throws away points it cannot afford to lose.",
                "themed_tie_in": "On the touchline, conditionals are tactical rules: compare the score difference against a rule and pick the plan.",
                "student_task": (
                    "The score differences are stored: diff_a = 2 (winning by two), diff_b = 0 (level), "
                    "diff_c = -1 (losing by one). For EACH match, write an if/elif/else that stores the "
                    "tactic: \"defend\" when the difference is 1 or more, \"balance\" when it is exactly 0, "
                    "otherwise \"attack\". Store the calls in tactic_a, tactic_b and tactic_c."
                ),
                "starter_code": (
                    "# Half-time score differences — do not change these.\n"
                    "diff_a = 2\ndiff_b = 0\ndiff_c = -1\n\n"
                    "# Marta: \"Ahead? Defend. Level? Stay balanced. Behind? Attack. Every time.\"\n"
                    "# Decide tactic_a from diff_a:\n\n# Decide tactic_b from diff_b:\n\n# Decide tactic_c from diff_c:\n"
                ),
                "expected_solution_description": "Three if/elif/else blocks assigning \"defend\", \"balance\" or \"attack\" to tactic_a, tactic_b, tactic_c based on each score difference.",
                "reference_solution": (
                    "diff_a = 2\ndiff_b = 0\ndiff_c = -1\n"
                    'if diff_a >= 1:\n    tactic_a = "defend"\nelif diff_a == 0:\n    tactic_a = "balance"\nelse:\n    tactic_a = "attack"\n'
                    'if diff_b >= 1:\n    tactic_b = "defend"\nelif diff_b == 0:\n    tactic_b = "balance"\nelse:\n    tactic_b = "attack"\n'
                    'if diff_c >= 1:\n    tactic_c = "defend"\nelif diff_c == 0:\n    tactic_c = "balance"\nelse:\n    tactic_c = "attack"\n'
                ),
                "hidden_tests": [
                    ('tactic_a == "defend"', "winning by two means defend"),
                    ('tactic_b == "balance"', "a level game means balance"),
                    ('tactic_c == "attack"', "losing by one means attack"),
                ],
                "hints": [
                    "The shape is: if diff_a >= 1: then an indented assignment — don't forget the colon.",
                    "Use elif diff_a == 0: for the level case (== compares, = assigns) and else: for behind.",
                    "Repeat the same three-branch rule for each match: diff_a sets tactic_a, diff_b sets tactic_b, diff_c sets tactic_c.",
                ],
                "success_story": "The bench executes all three calls perfectly — a win held, a draw secured, a late equalizer chased down and scored. Marta, almost smiling: \"Good calls, coach.\"",
                "failure_story": "The wrong tactic goes out and the crowd groans. Marta: \"One of those calls doesn't follow my rule. Ahead-defend, level-balance, behind-attack — walk it through again.\"",
                "success_tech": "Your if/elif/else branches classify all three scorelines correctly — same rule, applied consistently, every match.",
                "failure_tech": "At least one tactic is wrong or missing. Check == vs =, the colons, the indentation, and that the 'ahead' case comes first.",
                "remediation": {
                    "simpler_explanation": "A conditional checks rules top to bottom and uses the FIRST one that's True. `if diff >= 1` catches winning, `elif diff == 0` catches level, `else` catches everything left — losing.",
                    "smaller_subtask": "Just match A: write the if/elif/else so tactic_a becomes \"defend\", run the tests, see one pass. Then copy the pattern for B and C.",
                },
            },
            "loops": {
                "title": "The Training Week",
                "story_purpose": "Automate the grind: a season is the same work repeated until it compounds.",
                "current_problem": "Five training sessions are logged, but the fitness report needs total minutes and a session count — and the old coach added it up by hand.",
                "why_this_matters": "Fitness decisions come from totals across the whole week, not single sessions. Hand-adding doesn't scale to a season.",
                "narrative_stakes": "Without the report, the physio benches half the squad for Saturday as a precaution.",
                "themed_tie_in": "At a club, a loop is the training drill: the same step repeated for every session on the schedule.",
                "student_task": (
                    "The week's sessions are in the list training_minutes. Use a for loop to add every "
                    "session into `total_minutes` (start at 0) and count the sessions in `sessions` "
                    "(also starting at 0)."
                ),
                "starter_code": (
                    "# This week's training log — do not change this list.\n"
                    "training_minutes = [45, 60, 30, 75, 50]\n\n"
                    "# Marta: \"Start the totals at zero. Let the loop run the laps.\"\n"
                    "total_minutes = 0\nsessions = 0\n\n# your for loop here:\n"
                ),
                "expected_solution_description": "A for loop over training_minutes accumulating the sum into total_minutes and incrementing sessions once per item.",
                "reference_solution": (
                    "training_minutes = [45, 60, 30, 75, 50]\n"
                    "total_minutes = 0\nsessions = 0\n"
                    "for minutes in training_minutes:\n    total_minutes = total_minutes + minutes\n    sessions = sessions + 1\n"
                ),
                "hidden_tests": [
                    ("total_minutes == 260", "total_minutes sums the whole week (260)"),
                    ("sessions == 5", "sessions counts all five sessions"),
                ],
                "hints": [
                    "for minutes in training_minutes: visits each session — the indented lines under it run once per session.",
                    "Grow the total inside the loop: total_minutes = total_minutes + minutes.",
                    "Add sessions = sessions + 1 inside the loop too, so the counter rises once per session.",
                ],
                "success_story": "The fitness report prints itself: 260 minutes, 5 sessions, squad cleared to play. Marta pins it to the board: \"Whole season's admin, done in a blink. We might actually survive this league, coach.\"",
                "failure_story": "The physio frowns at the report — the numbers don't match the log. Marta: \"Either the loop skipped sessions or counted wrong. Look at what happens inside it.\"",
                "success_tech": "Accumulator pattern, executed cleanly: initialize before the loop, update inside it. The same pattern handles a week or a whole season.",
                "failure_tech": "total_minutes or sessions is off. Both must start at 0 BEFORE the loop, and both updates must be INDENTED inside it.",
                "remediation": {
                    "simpler_explanation": "A for loop means 'do this once per item'. With [45, 60] the body runs twice: minutes is 45, then 60. Adding it to a total that starts at 0 ends at 105.",
                    "smaller_subtask": "Skip the counter. Write only the loop that builds total_minutes and run the tests — the first one will pass. Then add sessions.",
                },
            },
        },
    },
    "music": {
        "keywords": ["music", "band", "guitar", "piano", "drums", "dj", "song", "concert", "festival", "singing"],
        "arc": {
            "story_title": "Lumen Festival: Show Must Go On",
            "protagonist_role": "Sound engineer of the Lumen Festival main stage",
            "world_description": (
                "Lumen Festival happens one night a year, on a clifftop stage above the sea. "
                "Tonight ten thousand people are walking through the gates — and {name} is the "
                "engineer with the only working console key."
            ),
            "central_conflict": "A storm surge fried the main stage rig an hour before doors. The mixing desk, the soundcheck system and the setlist clock are all dead.",
            "main_goal": "Rebuild the stage systems one by one and get the headliner on stage before the crowd gives up.",
            "mentor": {
                "name": "Rui",
                "role": "Stage manager who has run two hundred shows",
                "personality": "Unshakeably calm, speaks in checklists, believes every problem is just a step that hasn't been done yet.",
            },
            "opening_state": "The storm has passed but the main stage is silent — every rack light dark, one hour to doors.",
            "final_challenge": "Showtime: combine the desk settings, live level decisions and automated setlist timing in one final program that opens the show.",
        },
        "missions": {
            "variables": {
                "title": "Reboot the Mixing Desk",
                "story_purpose": "Give the desk its memory back: stored settings are what 'configured' means.",
                "current_problem": "The desk boots to factory zero — it has forgotten the master volume, the stage name, even how many channels are live.",
                "why_this_matters": "Every fader and screen on stage reads these stored settings. Until they exist, the desk is an expensive brick.",
                "narrative_stakes": "No desk, no soundcheck — and the headliner won't walk on stage without one.",
                "themed_tie_in": "On a mixing desk, variables are the saved settings: each named value is a knob position the whole rig depends on.",
                "student_task": (
                    "Rui reads from his checklist. Create a variable `master_volume` with the value 70, "
                    "a variable `stage_name` with the value \"Lumen Main Stage\", and a variable "
                    "`channels_live` with the value 8."
                ),
                "starter_code": (
                    "# Desk reboot checklist — restore each setting.\n"
                    "# Rui: \"Name equals value. That's all a setting is.\"\n\n"
                    "# 1. master_volume should be 70\n\n# 2. stage_name should be \"Lumen Main Stage\"\n\n# 3. channels_live should be 8\n"
                ),
                "expected_solution_description": "Three assignments creating master_volume, stage_name and channels_live with the exact required values.",
                "reference_solution": 'master_volume = 70\nstage_name = "Lumen Main Stage"\nchannels_live = 8\n',
                "hidden_tests": [
                    ("master_volume == 70", "master_volume holds 70"),
                    ('stage_name == "Lumen Main Stage"', 'stage_name holds "Lumen Main Stage"'),
                    ("channels_live == 8", "channels_live holds 8"),
                ],
                "hints": [
                    "Assignment is name = value, with the name on the left.",
                    "70 and 8 are numbers (no quotes); \"Lumen Main Stage\" is text (quotes required).",
                    "Three lines: master_volume = 70, stage_name = \"Lumen Main Stage\", channels_live = 8.",
                ],
                "success_story": "The desk hums awake, faders gliding to position on their own. Rui ticks his list: \"Desk: alive. Two systems to go before doors.\"",
                "failure_story": "The desk reboots back to zero. Rui doesn't look up: \"A setting's empty or wrong. Read the checklist again — exact names, exact values.\"",
                "success_tech": "All three variables exist with the right values. Stored settings — assignment — are the base layer of every system tonight.",
                "failure_tech": "At least one variable is missing or wrong. Check: name = value, quotes around text, exact spelling of each name.",
                "remediation": {
                    "simpler_explanation": "A variable is a labelled preset. `master_volume = 70` stores 70 under the label 'master_volume'. Any part of the rig can read that label and get 70.",
                    "smaller_subtask": "Restore one preset: write only `master_volume = 70`, run the tests, watch one pass. Then do the other two.",
                },
            },
            "conditionals": {
                "title": "Soundcheck the Levels",
                "story_purpose": "Give the desk ears: judging a level against a rule is what mixing is.",
                "current_problem": "Three input meters show readings, but the auto-mixer can't label them: too hot, good, or too quiet.",
                "why_this_matters": "A hot channel distorts through the cliff speakers; a quiet one vanishes under the crowd. The labels drive every fader move.",
                "narrative_stakes": "Doors open in twenty minutes — an unlabelled mix means feedback in front of ten thousand people.",
                "themed_tie_in": "At the desk, conditionals are level checks: compare a meter against thresholds and label the channel.",
                "student_task": (
                    "The meter readings are stored: vocals = 95, guitar = 60, drums = 20. For EACH channel, "
                    "write an if/elif/else that stores its label: \"too hot\" when the reading is 90 or more, "
                    "\"good\" when it is 40 or more, otherwise \"too quiet\". Store the labels in "
                    "check_vocals, check_guitar and check_drums."
                ),
                "starter_code": (
                    "# Soundcheck meter readings — do not change these.\n"
                    "vocals = 95\nguitar = 60\ndrums = 20\n\n"
                    "# Rui: \"90 or more is too hot. 40 or more is good. Under that, too quiet.\"\n"
                    "# Label check_vocals from vocals:\n\n# Label check_guitar from guitar:\n\n# Label check_drums from drums:\n"
                ),
                "expected_solution_description": "Three if/elif/else blocks assigning \"too hot\", \"good\" or \"too quiet\" to check_vocals, check_guitar, check_drums based on the thresholds.",
                "reference_solution": (
                    "vocals = 95\nguitar = 60\ndrums = 20\n"
                    'if vocals >= 90:\n    check_vocals = "too hot"\nelif vocals >= 40:\n    check_vocals = "good"\nelse:\n    check_vocals = "too quiet"\n'
                    'if guitar >= 90:\n    check_guitar = "too hot"\nelif guitar >= 40:\n    check_guitar = "good"\nelse:\n    check_guitar = "too quiet"\n'
                    'if drums >= 90:\n    check_drums = "too hot"\nelif drums >= 40:\n    check_drums = "good"\nelse:\n    check_drums = "too quiet"\n'
                ),
                "hidden_tests": [
                    ('check_vocals == "too hot"', "vocals at 95 are labelled too hot"),
                    ('check_guitar == "good"', "guitar at 60 is labelled good"),
                    ('check_drums == "too quiet"', "drums at 20 are labelled too quiet"),
                ],
                "hints": [
                    "Shape: if vocals >= 90: with an indented assignment under it — colon required.",
                    "elif vocals >= 40: handles the middle band, else: catches everything quieter.",
                    "Apply the same rule to each channel: vocals sets check_vocals, guitar sets check_guitar, drums sets check_drums.",
                ],
                "success_story": "The auto-mixer pulls the vocals down, leaves the guitar, lifts the drums — and the test tone rolls clean across the clifftop. Rui: \"That's a mix. One system left.\"",
                "failure_story": "A squeal of feedback cuts across the empty field. Rui winces: \"One label's wrong. Ninety-plus is hot, forty-plus is good — run the readings through the rule again.\"",
                "success_tech": "Your branches label all three channels correctly. Thresholds checked highest-first is exactly how real auto-mixers are written.",
                "failure_tech": "At least one label is wrong or missing. Check == vs =, colons, indentation, and that >= 90 is tested before >= 40.",
                "remediation": {
                    "simpler_explanation": "Conditions run top to bottom; the FIRST true one wins. 95 hits `if vocals >= 90` immediately. 60 misses it, then hits `elif >= 40`. 20 misses both and lands in `else`.",
                    "smaller_subtask": "Label one channel: write the if/elif/else for vocals only, so check_vocals becomes \"too hot\". Run the tests, then copy the pattern twice.",
                },
            },
            "loops": {
                "title": "Time the Setlist",
                "story_purpose": "Automate the clock: a show is songs repeated until the night adds up.",
                "current_problem": "The headliner's setlist is loaded, but the show clock needs the total minutes and song count — and the storm wiped the timing computer.",
                "why_this_matters": "The curfew is fixed by the council. If the set runs long, the power gets cut mid-encore; too short and the crowd riots politely.",
                "narrative_stakes": "The headliner walks on in ten minutes and the clock is still dark.",
                "themed_tie_in": "Backstage, a loop is the setlist itself: the same timing step repeated for every song on the page.",
                "student_task": (
                    "The song lengths are in the list song_lengths. Use a for loop to add every length "
                    "into `total_minutes` (start at 0) and count the songs in `song_count` (also starting at 0)."
                ),
                "starter_code": (
                    "# Tonight's setlist, in minutes — do not change this list.\n"
                    "song_lengths = [3, 4, 5, 3, 6]\n\n"
                    "# Rui: \"Zero the clock, then let the loop play through the list.\"\n"
                    "total_minutes = 0\nsong_count = 0\n\n# your for loop here:\n"
                ),
                "expected_solution_description": "A for loop over song_lengths accumulating the sum into total_minutes and incrementing song_count once per song.",
                "reference_solution": (
                    "song_lengths = [3, 4, 5, 3, 6]\n"
                    "total_minutes = 0\nsong_count = 0\n"
                    "for length in song_lengths:\n    total_minutes = total_minutes + length\n    song_count = song_count + 1\n"
                ),
                "hidden_tests": [
                    ("total_minutes == 21", "total_minutes adds the whole set (21)"),
                    ("song_count == 5", "song_count counts all five songs"),
                ],
                "hints": [
                    "for length in song_lengths: visits each song — indented lines run once per song.",
                    "Inside the loop: total_minutes = total_minutes + length grows the clock.",
                    "Also inside the loop: song_count = song_count + 1 ticks the counter once per song.",
                ],
                "success_story": "The show clock blazes to life: 21 MINUTES — 5 SONGS — CURFEW SAFE. The house lights drop, ten thousand voices rise, and Rui hands you the headliner's pick: \"Your stage, engineer.\"",
                "failure_story": "The clock flashes a timing error. Rui checks his watch: \"The totals don't match the setlist. Whatever happens inside that loop, it's missing songs or miscounting.\"",
                "success_tech": "Clean accumulator pattern: totals initialized before the loop, updated inside it. The same code times a five-song set or a five-day festival.",
                "failure_tech": "total_minutes or song_count is wrong. Both must start at 0 BEFORE the loop and both updates must be INDENTED inside it.",
                "remediation": {
                    "simpler_explanation": "A for loop plays the list one item at a time. With [3, 4] the body runs twice: length is 3, then 4. A total starting at 0 ends at 7.",
                    "smaller_subtask": "Time the set only: write the loop that builds total_minutes, run the tests, watch one pass. Then add song_count.",
                },
            },
        },
    },
    "explorer": {
        "keywords": ["explorer", "adventure", "island", "jungle", "map", "treasure", "expedition", "nature", "animals"],
        "arc": {
            "story_title": "The Cartographer's Island",
            "protagonist_role": "Expedition cartographer on an uncharted island",
            "world_description": (
                "A storm drove the survey ship onto the reef of an island that appears on no map. "
                "The crew made it ashore with crates, instruments and one waterlogged logbook — "
                "and elected {name} expedition cartographer."
            ),
            "central_conflict": "The expedition's instruments were scrambled by the wreck. Without working records, weather calls and supply counts, the crew can't survive the island, let alone chart it.",
            "main_goal": "Rebuild the expedition's systems one by one, chart the island, and signal the rescue ship.",
            "mentor": {
                "name": "Captain Quill",
                "role": "Retired navigator who has been shipwrecked four times and enjoyed it",
                "personality": "Wry, unhurried, full of stories; convinced that every disaster is just a map nobody has drawn yet.",
            },
            "opening_state": "The tide has gone out, the crates are stacked on the sand, and the expedition's logbook is open to a blank first page.",
            "final_challenge": "Signal fire night: combine the camp records, weather decisions and automated supply tallies into one final program that times the rescue signal.",
        },
        "missions": {
            "variables": {
                "title": "Set Up Base Camp",
                "story_purpose": "Start the logbook: an expedition exists once its facts are written down.",
                "current_problem": "The logbook's first page is blank — no camp name, no water count, no crew tally. Officially, the expedition doesn't exist.",
                "why_this_matters": "Every decision on the island — rations, watches, routes — reads from the logbook. Blank pages mean guesses, and guesses kill expeditions.",
                "narrative_stakes": "Quill won't ration the water until the ledger says how much there is.",
                "themed_tie_in": "On an expedition, variables are logbook entries: each named value is a fact the whole crew relies on.",
                "student_task": (
                    "Quill dictates the first page. Create a variable `camp_name` with the value "
                    "\"Driftwood Camp\", a variable `water_liters` with the value 20, and a variable "
                    "`crew_count` with the value 3."
                ),
                "starter_code": (
                    "# Expedition logbook, page one — record each fact.\n"
                    "# Quill: \"A fact is a name and a value. Write both.\"\n\n"
                    "# 1. camp_name should be \"Driftwood Camp\"\n\n# 2. water_liters should be 20\n\n# 3. crew_count should be 3\n"
                ),
                "expected_solution_description": "Three assignments creating camp_name, water_liters and crew_count with the exact required values.",
                "reference_solution": 'camp_name = "Driftwood Camp"\nwater_liters = 20\ncrew_count = 3\n',
                "hidden_tests": [
                    ('camp_name == "Driftwood Camp"', 'camp_name holds "Driftwood Camp"'),
                    ("water_liters == 20", "water_liters holds 20"),
                    ("crew_count == 3", "crew_count holds 3"),
                ],
                "hints": [
                    "Assignment is name = value — the label first, then what it holds.",
                    "Text like \"Driftwood Camp\" needs quotes; 20 and 3 are plain numbers.",
                    "Three lines: camp_name = \"Driftwood Camp\", water_liters = 20, crew_count = 3.",
                ],
                "success_story": "Quill reads the page and stamps it with a thumbprint of charcoal: \"Driftwood Camp, twenty liters, three souls. Now it's an expedition.\"",
                "failure_story": "Quill taps the page: \"An entry's missing or wrong, cartographer. The ledger has to match what I dictated — exactly.\"",
                "success_tech": "All three variables exist with the right values. Recorded facts — assignments — are the base of every program, and every expedition.",
                "failure_tech": "At least one variable is missing or wrong. Check: name = value, quotes around the camp name, exact spellings.",
                "remediation": {
                    "simpler_explanation": "A variable is a logbook line. `water_liters = 20` writes 'water_liters: 20' in the book. Reading the name later gives back the value.",
                    "smaller_subtask": "Record one fact: write only `water_liters = 20` and run the tests — one passes. Then add the other two lines.",
                },
            },
            "conditionals": {
                "title": "Read the Weather Signs",
                "story_purpose": "Give the camp judgement: survival is reading a sign and choosing a plan.",
                "current_problem": "The barometer logged three pressure readings, but nobody has turned them into weather calls: storm, cloudy, or clear.",
                "why_this_matters": "Tomorrow's route depends on the calls. The cliff path in a storm is a one-way trip.",
                "narrative_stakes": "Quill delays the inland trek until the weather page is filled in.",
                "themed_tie_in": "On the island, conditionals are weather rules: compare a reading against a threshold and choose the day's plan.",
                "student_task": (
                    "The pressure readings are stored: morning = 985, midday = 1005, evening = 1025. "
                    "For EACH reading, write an if/elif/else that stores the call: \"storm\" when the "
                    "pressure is below 1000, \"cloudy\" when it is below 1020, otherwise \"clear\". "
                    "Store the calls in call_morning, call_midday and call_evening."
                ),
                "starter_code": (
                    "# Barometer readings — do not change these.\n"
                    "morning = 985\nmidday = 1005\nevening = 1025\n\n"
                    "# Quill: \"Under 1000, storm. Under 1020, cloudy. Otherwise clear skies.\"\n"
                    "# Decide call_morning from morning:\n\n# Decide call_midday from midday:\n\n# Decide call_evening from evening:\n"
                ),
                "expected_solution_description": "Three if/elif/else blocks assigning \"storm\", \"cloudy\" or \"clear\" to call_morning, call_midday, call_evening based on the pressure thresholds.",
                "reference_solution": (
                    "morning = 985\nmidday = 1005\nevening = 1025\n"
                    'if morning < 1000:\n    call_morning = "storm"\nelif morning < 1020:\n    call_morning = "cloudy"\nelse:\n    call_morning = "clear"\n'
                    'if midday < 1000:\n    call_midday = "storm"\nelif midday < 1020:\n    call_midday = "cloudy"\nelse:\n    call_midday = "clear"\n'
                    'if evening < 1000:\n    call_evening = "storm"\nelif evening < 1020:\n    call_evening = "cloudy"\nelse:\n    call_evening = "clear"\n'
                ),
                "hidden_tests": [
                    ('call_morning == "storm"', "985 reads as storm"),
                    ('call_midday == "cloudy"', "1005 reads as cloudy"),
                    ('call_evening == "clear"', "1025 reads as clear"),
                ],
                "hints": [
                    "Shape: if morning < 1000: with an indented assignment beneath — and a colon at the end.",
                    "elif morning < 1020: catches the cloudy band; else: is everything higher — clear.",
                    "Apply the same rule three times: morning sets call_morning, midday sets call_midday, evening sets call_evening.",
                ],
                "success_story": "Quill pins the weather page to the mast: storm at dawn, clearing by dark. \"We move at midday, cartographer. The island just got smaller.\"",
                "failure_story": "Quill frowns at the page: \"One call doesn't follow my rule. Under a thousand is storm, under ten-twenty is cloudy. Read them again.\"",
                "success_tech": "Your branches classify all three readings correctly. Checking the lowest threshold first is what makes the chain airtight.",
                "failure_tech": "At least one call is wrong or missing. Check < vs <=, == vs =, colons, indentation, and the order of the branches.",
                "remediation": {
                    "simpler_explanation": "Rules check top to bottom; the FIRST true one wins. 985 trips `if < 1000` at once. 1005 passes it, trips `elif < 1020`. 1025 passes both and falls to `else`.",
                    "smaller_subtask": "Make one call: write the if/elif/else for morning only, so call_morning is \"storm\". Run the tests, then repeat the pattern twice.",
                },
            },
            "loops": {
                "title": "Count the Supplies",
                "story_purpose": "Automate the tally: a crate line is the same count repeated until it's done.",
                "current_problem": "Five crates came off the wreck, each with a stenciled weight — and the supply page needs the total weight and crate count before dark.",
                "why_this_matters": "The raft to the signal point can carry a fixed load. Overload it and the supplies sink; undercount and food gets left behind.",
                "narrative_stakes": "The tide turns at dusk. No tally, no raft, no signal fire tonight.",
                "themed_tie_in": "On the beach, a loop is the crate line: the same tally step repeated for every crate the crew hauls past.",
                "student_task": (
                    "The crate weights are in the list crate_weights. Use a for loop to add every weight "
                    "into `total_weight` (start at 0) and count the crates in `crate_count` (also starting at 0)."
                ),
                "starter_code": (
                    "# Stenciled crate weights — do not change this list.\n"
                    "crate_weights = [12, 7, 20, 5, 16]\n\n"
                    "# Quill: \"Zero the tally, then let the line walk past you.\"\n"
                    "total_weight = 0\ncrate_count = 0\n\n# your for loop here:\n"
                ),
                "expected_solution_description": "A for loop over crate_weights accumulating the sum into total_weight and incrementing crate_count once per crate.",
                "reference_solution": (
                    "crate_weights = [12, 7, 20, 5, 16]\n"
                    "total_weight = 0\ncrate_count = 0\n"
                    "for weight in crate_weights:\n    total_weight = total_weight + weight\n    crate_count = crate_count + 1\n"
                ),
                "hidden_tests": [
                    ("total_weight == 60", "total_weight sums every crate (60)"),
                    ("crate_count == 5", "crate_count counts all five crates"),
                ],
                "hints": [
                    "for weight in crate_weights: visits each crate — indented lines run once per crate.",
                    "Inside the loop, grow the tally: total_weight = total_weight + weight.",
                    "Add crate_count = crate_count + 1 inside the loop so the count rises with each crate.",
                ],
                "success_story": "The tally closes at sixty kilos across five crates — exactly a raft-load. By moonrise the signal fire is burning on the point, and far out at sea, a light answers. Quill grins: \"Best shipwreck I've ever had.\"",
                "failure_story": "Quill weighs a crate by hand and shakes his head: \"Your tally and my arms disagree. Whatever your loop does per crate, it's skipping or double-counting.\"",
                "success_tech": "Accumulator pattern done right: totals start at zero before the loop, grow inside it. The same loop tallies five crates or five thousand.",
                "failure_tech": "total_weight or crate_count is wrong. Both must start at 0 BEFORE the loop, and both updates must be INDENTED inside it.",
                "remediation": {
                    "simpler_explanation": "A for loop handles one item per pass. With [12, 7] the body runs twice: weight is 12, then 7. A total starting at 0 ends at 19.",
                    "smaller_subtask": "Tally weight only: write the loop that builds total_weight, run the tests, watch one pass. Then add crate_count.",
                },
            },
        },
    },
}

DEFAULT_THEME = "explorer"


def _keyword_in(keyword: str, text: str) -> bool:
    # Whole-word match: 'star' must not match inside 'starting'.
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def pick_theme(profile: StudentProfileIn) -> str:
    """Explicit preference wins; otherwise match interests against theme
    keywords; otherwise the generic explorer theme."""
    if profile.preferred_theme:
        wanted = profile.preferred_theme.strip().lower()
        if wanted in THEMES:
            return wanted
    for interest in profile.interests:
        text = interest.lower()
        for theme, pack in THEMES.items():
            if any(_keyword_in(kw, text) for kw in pack["keywords"]):
                return theme
    return DEFAULT_THEME


def generate_template_adventure(
    profile: StudentProfileIn, modules: list[dict]
) -> tuple[StoryArc, list[MissionWithSolution]]:
    theme = pick_theme(profile)
    pack = THEMES[theme]
    arc_data = pack["arc"]
    shift = _DIFFICULTY_SHIFT[profile.difficulty_preference]

    entries: list[MissionArcEntry] = []
    missions: list[MissionWithSolution] = []
    previous_state = arc_data["opening_state"].format(name=profile.name)

    for idx, module in enumerate(modules):
        module_id = module["module_id"]
        content = pack["missions"].get(module_id) or THEMES[DEFAULT_THEME]["missions"].get(module_id)
        if content is None:
            raise ValueError(
                f"No template content for module '{module_id}'. "
                "Template themes cover the vertical slice; use the LLM generator for other modules."
            )
        mission_id = f"m{idx + 1}-{module_id}"
        difficulty = _clamp(module["difficulty"] + shift)

        entries.append(
            MissionArcEntry(
                mission_id=mission_id,
                python_concept=module_id,
                story_purpose=content["story_purpose"],
                learning_objective=module["learning_objectives"][0],
                difficulty=difficulty,
            )
        )
        missions.append(
            MissionWithSolution(
                mission_id=mission_id,
                module=module_id,
                difficulty=difficulty,
                theme=theme,
                title=content["title"],
                story_context=StoryContext(
                    previous_state=previous_state,
                    current_problem=content["current_problem"],
                    why_this_matters=content["why_this_matters"],
                    narrative_stakes=content["narrative_stakes"],
                ),
                learning_objective=module["learning_objectives"][0],
                concept_explanation=module["explanation"] + "\n\n" + content["themed_tie_in"],
                starter_code=content["starter_code"],
                student_task=content["student_task"],
                expected_solution_description=content["expected_solution_description"],
                hidden_tests=[
                    HiddenTest(assertion=a, description=d) for a, d in content["hidden_tests"]
                ],
                hints=content["hints"],
                success_feedback=Feedback(
                    technical_feedback=content["success_tech"],
                    story_feedback=content["success_story"],
                ),
                failure_feedback=Feedback(
                    technical_feedback=content["failure_tech"],
                    story_feedback=content["failure_story"],
                ),
                remediation=Remediation(**content["remediation"]),
                next_mission_rules=NextMissionRules(
                    on_success="finish" if idx == len(modules) - 1 else "next",
                    on_failure="remediate",
                ),
                reference_solution=content["reference_solution"],
            )
        )
        # Narrative chain: the next mission opens where this one's success ends.
        previous_state = content["success_story"]

    interests = ", ".join(profile.interests) or "general adventure"
    arc = StoryArc(
        student_profile_summary=(
            f"{profile.name}"
            + (f", age {profile.age}" if profile.age else "")
            + f" — interests: {interests}; prior knowledge: {profile.prior_knowledge}; "
            + f"difficulty preference: {profile.difficulty_preference}."
        ),
        theme=theme,
        story_title=arc_data["story_title"],
        protagonist_role=arc_data["protagonist_role"],
        world_description=arc_data["world_description"].format(name=profile.name),
        central_conflict=arc_data["central_conflict"],
        main_goal=arc_data["main_goal"],
        mentor_character=MentorCharacter(**arc_data["mentor"]),
        mission_arc=entries,
        final_challenge=FinalChallenge(
            description=arc_data["final_challenge"],
            concepts_combined=[m["module_id"] for m in modules],
        ),
    )
    return arc, missions
