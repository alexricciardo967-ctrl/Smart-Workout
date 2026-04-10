import streamlit as st
import random
from dataclasses import dataclass
from typing import List, Dict, Any

# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class UserProfile:
    name: str
    age: int
    gender: str
    height_ft: int
    height_in: int
    weight_lb: float
    fitness_level: str
    goal: str
    equipment: List[str]
    time_minutes: int
    intensity: str


@dataclass
class Exercise:
    name: str
    category: str
    equipment: List[str]
    difficulty: str
    muscles: List[str]
    description: str


@dataclass
class WorkoutBlock:
    title: str
    exercises: List[Dict[str, Any]]


@dataclass
class WorkoutPlan:
    title: str
    blocks: List[WorkoutBlock]


# ============================================================
# EXERCISE DATABASE
# ============================================================

EXERCISES: List[Exercise] = [
    # Upper Body
    Exercise("Push-up", "upper", [], "beginner",
             ["chest", "triceps", "shoulders"],
             "Lower chest to floor and press back up."),
    Exercise("Incline Dumbbell Press", "upper", ["dumbbells", "bench"], "intermediate",
             ["chest", "shoulders"],
             "Press dumbbells upward on an incline bench."),
    Exercise("Lat Pulldown", "upper", ["lat pulldown"], "beginner",
             ["back", "biceps"],
             "Pull bar to chest while keeping torso upright."),
    Exercise("Cable Row", "upper", ["cable machine"], "intermediate",
             ["back", "biceps"],
             "Pull cable handle toward torso, squeezing shoulder blades."),
    Exercise("Barbell Bench Press", "upper", ["barbell", "bench"], "advanced",
             ["chest", "triceps"],
             "Lower bar to chest and press upward."),

    # Lower Body
    Exercise("Bodyweight Squat", "lower", [], "beginner",
             ["quads", "glutes"],
             "Sit hips back and down, then stand tall."),
    Exercise("Goblet Squat", "lower", ["dumbbells"], "beginner",
             ["quads", "glutes"],
             "Hold dumbbell at chest and squat down."),
    Exercise("Barbell Back Squat", "lower", ["squat rack", "barbell"], "advanced",
             ["quads", "glutes", "core"],
             "Squat with barbell on upper back."),
    Exercise("Leg Press", "lower", ["leg press"], "beginner",
             ["quads", "glutes"],
             "Press platform away with feet."),
    Exercise("Romanian Deadlift", "lower", ["barbell"], "intermediate",
             ["hamstrings", "glutes"],
             "Hinge at hips while lowering barbell along legs."),

    # Speed / Plyo
    Exercise("Sprint Intervals", "speed", [], "advanced",
             ["legs", "lungs"],
             "Short sprints with walking recovery."),
    Exercise("Bounding", "speed", [], "intermediate",
             ["legs", "glutes"],
             "Explosive long strides focusing on power."),
    Exercise("Box Jumps", "speed", ["box"], "intermediate",
             ["legs", "glutes"],
             "Jump explosively onto a box and step down."),

    # Conditioning
    Exercise("Burpees", "conditioning", [], "advanced",
             ["full body"],
             "Squat, kick back to plank, return, jump upward."),
    Exercise("Jump Rope", "conditioning", ["jump rope"], "beginner",
             ["full body"],
             "Continuous rope jumping at steady pace."),
    Exercise("Treadmill Intervals", "conditioning", ["treadmill"], "intermediate",
             ["legs", "lungs"],
             "Alternate fast and slow treadmill speeds."),

    # Full Body
    Exercise("Kettlebell Swing", "full", ["kettlebell"], "intermediate",
             ["glutes", "hamstrings", "core"],
             "Hinge and swing kettlebell to shoulder height."),
    Exercise("Dumbbell Thruster", "full", ["dumbbells"], "intermediate",
             ["legs", "shoulders"],
             "Squat and press dumbbells overhead explosively."),

    # Core / Mobility
    Exercise("Plank", "core", [], "beginner",
             ["core"],
             "Hold body straight on forearms."),
    Exercise("Dead Bug", "core", [], "beginner",
             ["core"],
             "Extend opposite arm and leg while bracing core."),
    Exercise("Russian Twist", "core", [], "intermediate",
             ["obliques"],
             "Rotate torso side to side while seated."),
    Exercise("Hamstring Stretch", "mobility", [], "beginner",
             ["hamstrings"],
             "Reach toward toes with long spine."),
    Exercise("Hip Flexor Stretch", "mobility", [], "beginner",
             ["hip flexors"],
             "Shift hips forward in half-kneeling position."),
]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def height_to_inches(ft: int, inch: int) -> int:
    return ft * 12 + inch


def calculate_bmi(user: UserProfile) -> float:
    h = height_to_inches(user.height_ft, user.height_in)
    return 703 * (user.weight_lb / (h * h))


def allowed_difficulties(level: str) -> List[str]:
    if level == "beginner":
        return ["beginner"]
    if level == "intermediate":
        return ["beginner", "intermediate"]
    return ["beginner", "intermediate", "advanced"]


def filter_exercises(category: str, user: UserProfile) -> List[Exercise]:
    allowed = allowed_difficulties(user.fitness_level)
    result = []
    for ex in EXERCISES:
        if ex.category == category and ex.difficulty in allowed:
            if all(eq in user.equipment for eq in ex.equipment):
                result.append(ex)
    return result


def choose(ex_list: List[Exercise], n: int) -> List[Exercise]:
    if len(ex_list) <= n:
        return ex_list
    return random.sample(ex_list, n)


def sets_reps(user: UserProfile, category: str) -> Dict[str, Any]:
    base_sets = 3
    base_reps = 10
    factor = 1.0 if user.intensity == "moderate" else (0.8 if user.intensity == "low" else 1.2)

    if category in ["conditioning", "speed"]:
        return {"sets": int(base_sets * factor), "reps_or_time": f"{int(30 * factor)} sec"}

    if category in ["core"]:
        return {"sets": 3, "reps_or_time": f"{int(20 * factor)} sec"}

    if category in ["mobility"]:
        return {"sets": 1, "reps_or_time": "30–45 sec hold"}

    return {"sets": int(base_sets * factor), "reps_or_time": f"{int(base_reps * factor)} reps"}


# ============================================================
# DAY-SPECIFIC WORKOUT GENERATORS
# ============================================================

DAY_CATEGORIES = {
    "Upper Body": ["upper"],
    "Lower Body": ["lower"],
    "Speed / Plyometrics": ["speed"],
    "Conditioning / HIIT": ["conditioning"],
    "Full Body": ["full"],
    "Core + Mobility": ["core", "mobility"]
}


def generate_day(user: UserProfile, day_type: str) -> WorkoutPlan:
    categories = DAY_CATEGORIES[day_type]
    exercises = []

    for cat in categories:
        exercises.extend(filter_exercises(cat, user))

    chosen = choose(exercises, max(3, min(8, user.time_minutes // 5)))

    block_items = []
    for ex in chosen:
        sr = sets_reps(user, ex.category)
        block_items.append({"exercise": ex, "sets": sr["sets"], "reps_or_time": sr["reps_or_time"]})

    block = WorkoutBlock(title=f"{day_type}", exercises=block_items)
    return WorkoutPlan(title=f"{day_type} Workout", blocks=[block])


# ============================================================
# WEEKLY PLAN GENERATOR
# ============================================================

WEEKLY_TEMPLATE = [
    "Upper Body",
    "Lower Body",
    "Speed / Plyometrics",
    "Conditioning / HIIT",
    "Full Body",
    "Core + Mobility"
]


def generate_weekly_plan(user: UserProfile) -> List[WorkoutPlan]:
    return [generate_day(user, day) for day in WEEKLY_TEMPLATE]


# ============================================================
# STREAMLIT UI
# ============================================================

st.title("Workout Generator")

st.subheader("Enter Your Information")

name = st.text_input("Name", "First, Last")
age = st.slider("Age", 12, 90, 18)
gender = st.selectbox("Gender", ["Male", "Female", "Other"])

col1, col2 = st.columns(2)
with col1:
    height_ft = st.number_input("Height (feet)", 4, 7, 5)
with col2:
    height_in = st.number_input("Height (inches)", 0, 11, 8)

weight_lb = st.number_input("Weight (lb)", 70, 400, 150)

fitness_level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
goal = st.selectbox("Primary Goal", ["Strength", "Endurance", "Fat Loss", "Speed", "General"])
intensity = st.selectbox("Intensity", ["Low", "Moderate", "High"])
time_minutes = st.slider("Workout Duration (minutes)", 15, 90, 30)

st.subheader("Equipment Available")

EQUIPMENT_OPTIONS = [
    "dumbbells", "barbell", "kettlebell",
    "squat rack", "power rack",
    "leg press", "lat pulldown", "cable machine",
    "chest press machine", "leg extension", "hamstring curl",
    "treadmill", "stationary bike", "rowing machine",
    "bench", "pull-up bar", "resistance bands", "medicine ball", "box", "jump rope"
]

equipment = st.multiselect("Select all equipment you have:", EQUIPMENT_OPTIONS)

user = UserProfile(
    name=name,
    age=age,
    gender=gender,
    height_ft=height_ft,
    height_in=height_in,
    weight_lb=weight_lb,
    fitness_level=fitness_level,
    goal=goal,
    equipment=equipment,
    time_minutes=time_minutes,
    intensity=intensity
)

st.subheader("Choose Workout Mode")
mode = st.radio("Select one:", ["Single Workout", "Full Weekly Plan"])

if mode == "Single Workout":
    day_type = st.selectbox("Choose Workout Type", list(DAY_CATEGORIES.keys()))

    if st.button("Generate Workout"):
        plan = generate_day(user, day_type)

        st.header(plan.title)
        for block in plan.blocks:
            st.subheader(block.title)
            for item in block.exercises:
                ex = item["exercise"]
                st.markdown(f"**{ex.name}**")
                st.write(f"Muscles: {', '.join(ex.muscles)}")
                st.write(f"Sets: {item['sets']} | Reps/Time: {item['reps_or_time']}")
                st.write(f"How to: {ex.description}")
                st.write("---")

else:
    if st.button("Generate Weekly Plan"):
        weekly = generate_weekly_plan(user)

        for day_plan in weekly:
            st.header(day_plan.title)
            for block in day_plan.blocks:
                st.subheader(block.title)
                for item in block.exercises:
                    ex = item["exercise"]
                    st.markdown(f"**{ex.name}**")
                    st.write(f"Muscles: {', '.join(ex.muscles)}")
                    st.write(f"Sets: {item['sets']} | Reps/Time: {item['reps_or_time']}")
                    st.write(f"How to: {ex.description}")
                    st.write("---")

        st.success("Rest Day automatically included on Day 7!")
