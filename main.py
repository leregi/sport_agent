import httpx 
import asyncio
from ollama import chat
from ollama import Client
from ollama import AsyncClient 


system_prompt = """
You are an expert Nutritionist and Certified Gym Trainer. Your role is to guide users step-by-step by first collecting their key details, then providing a personalized weight loss/gain plan.  

### **Step 1: Ask for Details**  
Start by requesting the following information in a clear, friendly manner:  
1. **Age**  
2. **Gender** (optional, if relevant to hormonal/metabolic advice)  
3. **Current Weight** (e.g., "180 lbs" or "82 kg")  
4. **Height** (e.g., "5'9\"" or "175 cm")  
5. **Goal** (Lose Weight / Gain Weight / Maintain)  
6. **Target Weight** (if any)  
7. **Activity Level** (Sedentary / Lightly Active / Active / Very Active)  
8. **Dietary Restrictions** (Vegan, Keto, Gluten-Free, Allergies, etc.)  

*Example Prompt:*  
"Welcome! To create your personalized plan, I'll need a few details:  
- Your age, gender (optional), current weight, and height.  
- Your goal (lose/gain weight) and target weight (if any).  
- How active you are (Sedentary, Lightly Active, etc.).  
- Any dietary restrictions (e.g., Vegan, Keto).  

Ready? Let's start!"  

### **Step 2: Provide the Plan**  
Once all details are provided, generate a structured plan:  
- **Calorie/Macro Targets** (science-backed calculation)  
- **Meal Ideas** (customized for dietary restrictions)  
- **Workout Routine** (home/gym options)  
- **Safety Tips** (e.g., "Consult a doctor if you have conditions like diabetes")  

*Tone:* Supportive, professional, and concise.  

### **Additional Guidelines:**
1. Always calculate BMI first: BMI = weight(kg) / (height(m))²  
   - Underweight: <18.5  
   - Normal: 18.5-24.9  
   - Overweight: 25-29.9  
   - Obese: ≥30  

2. For weight loss: Recommend 300-500 kcal deficit daily  
3. For weight gain: Recommend 300-500 kcal surplus daily  
4. Always include rest days in workout plans  
5. Provide vegetarian/vegan alternatives when needed  

*Example Response Format:*  
\"Based on your details (Age: 30, Height: 1.75m, Weight: 85kg, Goal: Lose Weight):  
- **Daily Calories:** ~2100 kcal (500 kcal deficit)  
- **Macros:** 40% Carbs, 30% Protein, 30% Fat  
- **Sample Meals:**  
  - Breakfast: Oatmeal with berries and almonds  
  - Lunch: Grilled chicken with quinoa and vegetables  
  - Dinner: Baked salmon with sweet potato  
- **Workout Plan:**  
  - Monday: Full-body strength training  
  - Wednesday: HIIT cardio  
  - Friday: Upper body focus  
- **Tip:** Stay hydrated and aim for 7-9 hours of sleep nightly.\"
"""

print("=== Fitness Planner Assistant ===")
name = input("Name: ")
age = int(input("Age: "))
gender = input("Gender: ")
weight = float(input("Weight (kg): "))
height = float(input("Height (m): "))

# Calculate BMI
bmi = weight / (height ** 2)
bmi_category = (
    "Underweight" if bmi < 18.5 else
    "Normal" if 18.5 <= bmi < 25 else
    "Overweight" if 25 <= bmi < 30 else
    "Obese"
)

print("\nWhat is your target?")
print("1. Lose Weight\n2. Gain Weight")
goal = int(input("Select an option (1 or 2): "))

goal_text = ""
# Generate summary based on goal
if goal == 1:
    goal_text += "LOSE weight (calorie deficit)"
    advice = "Focus on high-protein meals and cardio + strength training."
elif goal == 2:
    goal_text += "GAIN weight (calorie surplus)"
    advice = "Prioritize calorie-dense foods and progressive overload in workouts."
else:
    print("Invalid choice!")
    exit()

# Summary message
print(f"\n🔥 **SUMMARY FOR {name.upper()}** 🔥")
print(f"- Age: {age} | Weight: {weight} kg | Height: {height} m")
print(f"- BMI: {bmi:.1f} ({bmi_category})")
print(f"- Goal: {goal_text}")
print(f"\n💡 **ADVICE**: {advice}")
print("\n🚀 Let’s crush your goals together! Consistency is key.")

user = {
    "age": age,
    "gender": gender,
    "weight": weight,
    "height": height,
    "bmi": bmi,
    "bmi_category": bmi_category,
    "goal": goal_text
}


def generate_user_prompt(name, age, weight, height, gender, goal, activity_level, dietary_restrictions, target_weight=None):
    # Calculate BMI
    bmi = weight / (height ** 2)
    bmi_category = (
        "Underweight" if bmi < 18.5 else
        "Normal" if 18.5 <= bmi < 25 else
        "Overweight" if 25 <= bmi < 30 else
        "Obese"
    )
    
    # Build the prompt
    prompt = f"""
    I'm {name}, {age} years old ({gender if gender else 'no gender specified'}). 
    My current stats:
    - Weight: {weight} kg
    - Height: {height} m
    - BMI: {bmi:.1f} ({bmi_category})
    
    My fitness goal is to {goal.lower()}{f' (target weight: {target_weight} kg)' if target_weight else ''}.
    Activity level: {activity_level}.
    Dietary restrictions: {dietary_restrictions if dietary_restrictions else 'None'}.
    
    Please provide:
    1. A personalized daily calorie target and macronutrient breakdown
    2. A meal plan for seven day
    3. A weekly workout routine
    4. Any important safety considerations
    
    Make the plan realistic and tailored to my specific needs. Thank you!

    this what a meal day plan must looks like: 
    Day 6:
    - Breakfast: Whole wheat waffles with banana, almond butter, and milk 
        * calories: 400  
        * carbs 50g  
        * protein 10g  
        * fat 16g 
    - Snack: Greek yogurt with mixed berries and honey 
        * calories: 200  
        * carbs 30g  
        * protein 10g  
        * fat 0g
    - Lunch: Turkey and avocado wrap with mixed greens 
        * calories: 600  
        * carbs 40g  
        * protein 25g  
        * fat 20g 
    - Snack: Hard-boiled egg and cherry tomatoes 
        * calories: 100  
        * carbs 5g  
        * protein 6g  
        * fat 0g 
    - Dinner: Grilled turkey breast with quinoa and steamed broccoli 
        * calories: 500  
        * carbs 40g  
        * protein 30g  
        * fat 10g

        
        this what a workout day plan must looks like: 
        **Day 1: Chest and Triceps**

        *   Barbell bench press (3 sets of 8-12 reps)
        *   Incline dumbbell press (3 sets of 8-12 reps)
        *   Cable flyes (3 sets of 12-15 reps)
        *   Tricep pushdowns (3 sets of 8-12 reps)
        *   Overhead dumbbell extension (3 sets of 12-15 reps)
    """
    
    return prompt.strip()

user_prompt = generate_user_prompt(
    name=name, 
    age=age, 
    weight=weight, 
    height=height, 
    gender=gender, 
    goal=goal_text,
    activity_level="",
    dietary_restrictions="None",
    ) 

message = [
    {
        "role": "system",
        "content": system_prompt   
    },
    {
        "role": "user",
        "content": user_prompt
    }
    
]


client = Client(
  host='http://localhost:11434',
  headers={'Content-Type': 'application/json'}
)

diet_and_workout = ""

work_diet_response = client.chat(model='llama3.2', messages=message,
 stream=True)
for chunk in work_diet_response:
    diet_and_workout += chunk['message']['content'] or '' 
    print(chunk['message']['content'], end='', flush=True)




prompt = f"""
Given the following user data, diet and workout plan:
{user}
{diet_and_workout}

🔶 Your task:
Generate a JSON object that maps to this database schema:

---

USERS TABLE FORMAT:

{{
  "user": {{
    "name": "Jhon Doe",
    "age": 56,
    "weight": 69.5,
    "height": 1.75,
    "gender": "Male",
    "goal": "Lose Weight",
    "bmi": 22.7,
    "bmi_category": "Normal"
  }}
}}

---

MEAL PLANS TABLE FORMAT:
Return a 1-day meal plan split by meal type (breakfast, lunch, dinner, snacks):

"meal_plans": [
  {{
    "day": "Monday",
    "meal_type": "Breakfast",
    "description": "Oatmeal with berries, almonds, and low-fat milk",
    "calories": 400,
    "carbs": "40g",
    "protein": "30g",  
    "fat": "10g",
  }},
  {{
    "day": "Monday",
    "meal_type": "Lunch",
    "description": "Grilled chicken breast with quinoa and steamed vegetables",
    "calories": 400,
    "carbs": "40g",
    "protein": "30g",  
    "fat": "10g"
  }},
  {{
    "day": "Monday",
    "meal_type": "Dinner",
    "description": "Baked salmon with sweet potato and green beans",
    "calories": 400,
    "carbs": "40g",
    "protein": "30g",  
    "fat": "10g"
  }},
  {{
    "day": "Monday",
    "meal_type": "Snack",
    "description": "Apple slices with peanut butter; Greek yogurt with berries and honey",
    "calories": 400,
    "carbs": "40g",
    "protein": "30g",  
    "fat": "10g"
  }}
]

---

WORKOUT PLANS TABLE FORMAT:
Return a weekly workout plan, one entry per day.

"workout_plans": [
  {{
    "day": "Monday",
    "workout_type": "Chest and Triceps",
    "description": "Bench press, incline dumbbell press, tricep pushdowns",
    "duration": "60 minutes"
  }},
  {{
    "day": "Tuesday",
    "workout_type": "Back and Biceps",
    "description": "Pull-ups, barbell rows, dumbbell curls",
    "duration": "60 minutes"
  }},
  {{
    "day": "Wednesday",
    "workout_type": "Rest",
    "description": "Rest day",
    "duration": "0 minutes"
  }},
  {{
    "day": "Thursday",
    "workout_type": "Legs",
    "description": "Squats, leg press, lunges",
    "duration": "60 minutes"
  }},
  {{
    "day": "Friday",
    "workout_type": "Shoulders and Abs",
    "description": "Shoulder press, lateral raises, planks",
    "duration": "60 minutes"
  }},
  {{
    "day": "Saturday",
    "workout_type": "Rest",
    "description": "Rest day",
    "duration": "0 minutes"
  }},
  {{
    "day": "Sunday",
    "workout_type": "Rest",
    "description": "Rest day",
    "duration": "0 minutes"
  }}
]

---

📌 Important Instructions:
- Only return a valid JSON object with keys: "user", "meal_plans", and "workout_plans".
- Do not include explanations or formatting like markdown or bullet points.
- Ensure the structure is valid JSON — no trailing commas, no comments, etc.
- Start your reply with the JSON object only.
"""


# print(prompt)





extracted_msg = [
    {
        "role": "user",
        "content": prompt 
    }
]

extracted_response = client.chat(model='llama3.2', messages=extracted_msg)
print(extracted_response['message']['content'])