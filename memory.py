import json
import os
from datetime import datetime

MEMORY_FILE = "jarvis_memory.json"

def load_memory():
    """Load all memories from file"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {
        "user_profile": {
            "name":       None,
            "age":        None,
            "location":   None,
            "occupation": None,
            "language":   "English"
        },
        "interests":     [],
        "dislikes":      [],
        "goals":         [],
        "habits":        [],
        "facts":         [],
        "conversations": [],
        "achievements":  [],
        "mood_history":  [],
        "daily_patterns": {
            "wake_time":  None,
            "sleep_time": None,
            "busy_hours": []
        }
    }


def save_memory(memory):
    """Save all memories to file"""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


# ── User Profile ─────────────────────────────────────────
def set_user_name(name):
    memory = load_memory()
    memory["user_profile"]["name"] = name
    save_memory(memory)
    print(f"💾 Name saved: {name}")

def get_user_name():
    memory = load_memory()
    return memory["user_profile"].get("name", None)

def set_user_profile(key, value):
    """Set any profile field: age, location, occupation"""
    memory = load_memory()
    if key in memory["user_profile"]:
        memory["user_profile"][key] = value
        save_memory(memory)
        print(f"💾 Profile updated: {key} = {value}")

def get_user_profile():
    memory = load_memory()
    return memory["user_profile"]


# ── Interests & Dislikes ─────────────────────────────────
def add_interest(interest):
    memory = load_memory()
    if interest not in memory["interests"]:
        memory["interests"].append(interest)
        memory["interests"] = memory["interests"][-30:]
        save_memory(memory)
        print(f"💾 Interest saved: {interest}")

def add_dislike(dislike):
    memory = load_memory()
    if dislike not in memory["dislikes"]:
        memory["dislikes"].append(dislike)
        memory["dislikes"] = memory["dislikes"][-20:]
        save_memory(memory)
        print(f"💾 Dislike saved: {dislike}")

def add_goal(goal):
    memory = load_memory()
    memory["goals"].append({
        "goal":      goal,
        "timestamp": datetime.now().strftime("%Y-%m-%d")
    })
    memory["goals"] = memory["goals"][-10:]
    save_memory(memory)
    print(f"💾 Goal saved: {goal}")

def add_achievement(achievement):
    memory = load_memory()
    memory["achievements"].append({
        "achievement": achievement,
        "timestamp":   datetime.now().strftime("%Y-%m-%d")
    })
    memory["achievements"] = memory["achievements"][-20:]
    save_memory(memory)
    print(f"💾 Achievement saved: {achievement}")


# ── Facts & Conversations ────────────────────────────────
def remember_fact(fact):
    """Store a new fact"""
    memory = load_memory()

    # Avoid duplicate facts
    existing = [f["fact"] for f in memory["facts"]]
    if fact not in existing:
        memory["facts"].append({
            "fact":      fact,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        memory["facts"] = memory["facts"][-100:]
        save_memory(memory)
        print(f"💾 Fact saved: {fact}")

def remember_conversation(user_msg, jarvis_reply):
    """Store conversation exchange"""
    memory = load_memory()
    memory["conversations"].append({
        "user":   user_msg,
        "jarvis": jarvis_reply,
        "time":   datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    memory["conversations"] = memory["conversations"][-50:]
    save_memory(memory)


# ── Mood Tracking ────────────────────────────────────────
def track_mood(mood):
    """Track user mood over time"""
    memory = load_memory()
    memory["mood_history"].append({
        "mood":      mood,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    memory["mood_history"] = memory["mood_history"][-50:]
    save_memory(memory)


# ── Memory Context Builder ───────────────────────────────
def get_memory_context():
    """
    Build rich memory summary to inject into JARVIS brain.
    """
    memory  = load_memory()
    profile = memory["user_profile"]
    context = ""

    # ── User profile ──────────────────────────────
    if profile["name"]:
        context += f"User's name: {profile['name']}.\n"
    if profile["age"]:
        context += f"Age: {profile['age']}.\n"
    if profile["location"]:
        context += f"Location: {profile['location']}.\n"
    if profile["occupation"]:
        context += f"Occupation: {profile['occupation']}.\n"

    # ── Interests ────────────────────────────────
    if memory["interests"]:
        context += f"\nInterests & likes: {', '.join(memory['interests'][-10:])}.\n"

    # ── Dislikes ─────────────────────────────────
    if memory["dislikes"]:
        context += f"Dislikes: {', '.join(memory['dislikes'][-5:])}.\n"

    # ── Goals ────────────────────────────────────
    if memory["goals"]:
        recent_goals = [g["goal"] for g in memory["goals"][-3:]]
        context += f"\nCurrent goals: {', '.join(recent_goals)}.\n"

    # ── Achievements ─────────────────────────────
    if memory["achievements"]:
        recent = [a["achievement"] for a in memory["achievements"][-3:]]
        context += f"Recent achievements: {', '.join(recent)}.\n"

    # ── Recent facts ──────────────────────────────
    if memory["facts"]:
        context += "\nKey facts about user:\n"
        for item in memory["facts"][-15:]:
            context += f"  - {item['fact']}\n"

    # ── Mood history ─────────────────────────────
    if memory["mood_history"]:
        recent_moods = [m["mood"] for m in memory["mood_history"][-5:]]
        context += f"\nRecent mood pattern: {', '.join(recent_moods)}.\n"

    # ── Recent conversations ──────────────────────
    if memory["conversations"]:
        context += "\nRecent conversations:\n"
        for conv in memory["conversations"][-8:]:
            context += f"  User: {conv['user']}\n"
            context += f"  JARVIS: {conv['jarvis']}\n"

    return context.strip()


# ── Smart Auto-Extract ───────────────────────────────────
def extract_and_save_facts(user_input, jarvis_reply):
    """
    Intelligently extract and categorize facts
    from conversation automatically.
    """
    user_lower = user_input.lower()

    # ── Name detection ────────────────────────────
    for trigger in ["my name is ", "i am ", "i'm ", "call me "]:
        if trigger in user_lower:
            name = user_input.lower().split(trigger)[-1].strip().split()[0].capitalize()
            if len(name) > 1 and name.isalpha():
                set_user_name(name)
                remember_fact(f"User's name is {name}")
                break

    # ── Age detection ────────────────────────────
    import re
    age_match = re.search(r"i(?:'m| am) (\d{1,2}) years old", user_lower)
    if age_match:
        age = age_match.group(1)
        set_user_profile("age", age)
        remember_fact(f"User is {age} years old")

    # ── Location detection ────────────────────────
    for trigger in ["i live in ", "i'm from ", "i am from "]:
        if trigger in user_lower:
            location = user_input[user_lower.index(trigger) + len(trigger):]
            location = location.strip().split(".")[0].split(",")[0].strip()
            if location:
                set_user_profile("location", location)
                remember_fact(f"User lives in {location}")
                break

    # ── Occupation detection ──────────────────────
    for trigger in ["i am a ", "i'm a ", "i work as "]:
        if trigger in user_lower:
            occupation = user_input[user_lower.index(trigger) + len(trigger):]
            occupation = occupation.strip().split(".")[0].strip()
            if occupation:
                set_user_profile("occupation", occupation)
                remember_fact(f"User works as {occupation}")
                break

    # ── Interests detection ───────────────────────
    for trigger in ["i love ", "i like ", "i enjoy ", "i'm into ", "i am into "]:
        if trigger in user_lower:
            interest = user_input[user_lower.index(trigger) + len(trigger):]
            interest = interest.strip().split(".")[0].split("and")[0].strip()
            if interest:
                add_interest(interest)
                remember_fact(f"User likes {interest}")
                break

    # ── Dislikes detection ────────────────────────
    for trigger in ["i hate ", "i dislike ", "i don't like ", "i do not like "]:
        if trigger in user_lower:
            dislike = user_input[user_lower.index(trigger) + len(trigger):]
            dislike = dislike.strip().split(".")[0].strip()
            if dislike:
                add_dislike(dislike)
                remember_fact(f"User dislikes {dislike}")
                break

    # ── Goals detection ───────────────────────────
    for trigger in ["my goal is ", "i want to ", "i am trying to ", "i'm trying to "]:
        if trigger in user_lower:
            goal = user_input[user_lower.index(trigger) + len(trigger):]
            goal = goal.strip().split(".")[0].strip()
            if len(goal) > 5:
                add_goal(goal)
                break

    # ── Achievement detection ─────────────────────
    for trigger in ["i achieved ", "i completed ", "i finished ", "i passed "]:
        if trigger in user_lower:
            achievement = user_input[user_lower.index(trigger) + len(trigger):]
            achievement = achievement.strip().split(".")[0].strip()
            if achievement:
                add_achievement(achievement)
                remember_fact(f"User achieved: {achievement}")
                break

    # ── Always save conversation ──────────────────
    remember_conversation(user_input, jarvis_reply)


# ── Memory Summary ───────────────────────────────────────
def get_memory_summary():
    """Get a readable summary of everything JARVIS knows"""
    memory  = load_memory()
    profile = memory["user_profile"]

    summary = "Here is everything I know about you, sir:\n\n"

    if profile["name"]:
        summary += f"Name: {profile['name']}\n"
    if profile["age"]:
        summary += f"Age: {profile['age']}\n"
    if profile["location"]:
        summary += f"Location: {profile['location']}\n"
    if profile["occupation"]:
        summary += f"Occupation: {profile['occupation']}\n"

    if memory["interests"]:
        summary += f"\nInterests: {', '.join(memory['interests'])}\n"
    if memory["dislikes"]:
        summary += f"Dislikes: {', '.join(memory['dislikes'])}\n"
    if memory["goals"]:
        goals = [g["goal"] for g in memory["goals"]]
        summary += f"\nGoals: {', '.join(goals)}\n"
    if memory["achievements"]:
        achievements = [a["achievement"] for a in memory["achievements"]]
        summary += f"Achievements: {', '.join(achievements)}\n"
    if memory["facts"]:
        summary += f"\nKey facts stored: {len(memory['facts'])}\n"
    if memory["conversations"]:
        summary += f"Conversations remembered: {len(memory['conversations'])}\n"

    return summary