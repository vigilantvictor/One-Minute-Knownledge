from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Add CORS headers to ALL responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response

@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return '', 200

# ------------------- SUBSCRIPTION PLANS -------------------
SUBSCRIPTION_PLANS = {
    "weekly": {
        "name": "Weekly Plan",
        "price": 49,
        "duration": 7,
        "duration_unit": "days"
    },
    "monthly": {
        "name": "Monthly Plan",
        "price": 99,
        "duration": 30,
        "duration_unit": "days"
    },
    "yearly": {
        "name": "Yearly Plan",
        "price": 999,
        "duration": 365,
        "duration_unit": "days"
    }
}

# ------------------- LARGE DATABASE OF FACTS -------------------

DAILY_FACTS = [
    "The average person walks about 100,000 miles in a lifetime — that's 4 times around the Earth.",
    "Honey never spoils. Archaeologists found 3,000-year-old honey in Egyptian tombs, still edible.",
    "Octopuses have three hearts, and two of them stop beating when they swim.",
    "Bananas are berries, but strawberries are not.",
    "A day on Venus is longer than a year on Venus.",
    "The Eiffel Tower can grow up to 6 inches taller in summer due to thermal expansion.",
    "Humans share 60% of their DNA with bananas.",
    "The shortest war in history lasted only 38 minutes (Anglo-Zanzibar War, 1896).",
    "A single cloud can weigh more than 1 million pounds.",
    "The human nose can remember 50,000 different scents."
]

TOPIC_FACTS = {
    "Daily Facts": [
        "A bolt of lightning is 5 times hotter than the surface of the sun.",
        "The average person produces 25,000 quarts of saliva in a lifetime.",
        "The world's largest desert is Antarctica, not the Sahara.",
        "The human heart beats about 100,000 times per day.",
        "The average person will spend 25 years asleep in their lifetime.",
        "There are more trees on Earth than stars in the Milky Way galaxy.",
        "The human eye can distinguish about 10 million different colors.",
        "The average person spends 2 weeks of their life kissing.",
        "The world's population has doubled in the last 50 years.",
        "The average person laughs about 15 times per day.",
        "The human skeleton replaces itself every 10 years.",
        "The average person blinks about 15-20 times per minute.",
        "There are more than 7,000 languages spoken in the world today.",
        "The human brain uses 20% of the body's total oxygen and energy.",
        "The average person spends 5 years of their life eating.",
        "The average person will spend 3 years of their life on the toilet.",
        "The human body contains enough iron to make a 3-inch nail.",
        "The average person produces enough saliva in a lifetime to fill 2 swimming pools.",
        "The human nose can detect over 1 trillion different scents.",
        "The average person walks about 100,000 miles in a lifetime."
    ],
    "Life Skills": [
        "The 5-second rule: when you have an impulse to act on a goal, you must physically move within 5 seconds or your brain will kill the idea.",
        "The 80/20 rule (Pareto Principle): 80% of effects come from 20% of causes.",
        "Active listening can improve your relationships by 40%.",
        "Writing down your goals increases your success rate by 42%.",
        "The average person makes about 35,000 decisions per day.",
        "Learning to say 'no' is one of the most important life skills.",
        "The best time to start a new habit is right now.",
        "Meditation for 10 minutes a day can reduce stress by 30%.",
        "The 2-minute rule: if a task takes less than 2 minutes, do it immediately.",
        "Emotional intelligence is twice as important as IQ for success.",
        "The average person spends 2 hours per day on social media.",
        "Networking can increase your career opportunities by 70%.",
        "The power of habit: 40% of our daily actions are habits.",
        "The Eisenhower Matrix helps prioritize tasks by urgency and importance.",
        "Learning to cook can save you $2,000+ per year.",
        "The Pomodoro Technique can increase productivity by 25%.",
        "Reading for 30 minutes a day can reduce stress by 68%.",
        "The average person spends 6 months of their life waiting for red lights.",
        "The average person changes careers 5-7 times in their lifetime.",
        "85% of job success comes from well-developed soft skills."
    ],
    "Career Tips": [
        "85% of job success comes from having well-developed soft skills and people skills.",
        "The average person changes careers 5-7 times in their lifetime.",
        "Networking is the #1 way people find new jobs.",
        "70% of jobs are found through networking, not online applications.",
        "The average professional spends 2.5 hours per day on work emails.",
        "Continuous learning can increase your income by 30-50%.",
        "The best time to negotiate salary is when you have a job offer.",
        "Remote work has increased by 400% in the last decade.",
        "The average person spends 90,000 hours at work in their lifetime.",
        "Mentorship can double your career advancement speed.",
        "The most successful people read at least one book per week.",
        "Public speaking is the #1 fear for most professionals.",
        "The average worker is productive for only 2.5 hours per day.",
        "Companies that invest in employee development have 50% higher retention.",
        "The future of work is hybrid: 58% of workers want a mix of office and remote.",
        "Active listening at work can increase team productivity by 30%.",
        "The average person receives 121 work emails per day.",
        "The average person spends 2 years of their life in meetings.",
        "70% of employees say they would be more productive in a quiet workspace.",
        "The average person checks their work email 15 times per day."
    ],
    "Money Tips": [
        "The average millionaire reads at least one non-fiction book per month.",
        "Compound interest is the 8th wonder of the world.",
        "The average person spends $1,500 per year on coffee.",
        "The 50/30/20 rule: 50% needs, 30% wants, 20% savings.",
        "The average millionaire has 7 streams of income.",
        "Saving $1 per day can grow to over $1,000 in 10 years with compound interest.",
        "The average American household has $7,000 in credit card debt.",
        "The best time to start investing is yesterday, the next best is today.",
        "The average person will spend $200,000 on a car in their lifetime.",
        "The 1% rule: if the monthly rent is 1% of the purchase price, it's a good investment.",
        "The average person spends $10,000 per year on non-essential items.",
        "Emergency funds should cover 3-6 months of living expenses.",
        "The average millionaire drives a 4-year-old car.",
        "Budgeting apps can help you save 20% more money.",
        "The average person can save $300 per month by meal planning.",
        "The average person has $38,000 in personal debt.",
        "Only 24% of people feel confident in their financial decisions.",
        "The average person spends $1,000 per year on subscriptions they don't use.",
        "The average person will earn $1.7 million in their lifetime.",
        "The average person spends $50,000 on dining out in their lifetime."
    ],
    "Health Awareness": [
        "Drinking water can boost your metabolism by 24-30% over a period of 1-1.5 hours.",
        "The average person spends 25 years of their life sleeping.",
        "Exercise can reduce the risk of depression by 25%.",
        "The human body contains enough carbon to fill 9,000 pencils.",
        "Laughter can lower stress hormones and boost immune cells.",
        "The average person takes about 8,000 steps per day.",
        "Sleep deprivation can cost you $3,000 per year in lost productivity.",
        "The human eye can detect light from a candle 1.7 miles away.",
        "Stress can reduce your lifespan by up to 10 years.",
        "The average person gains 1-2 pounds per year during adulthood.",
        "Meditation can reduce anxiety symptoms by up to 50%.",
        "The human liver can regenerate to its full size within 3 months.",
        "Walking 30 minutes per day can add 3 years to your life.",
        "The average person spends 1.5 hours per day eating.",
        "Yoga can reduce chronic back pain by 40%.",
        "The human body has 206 bones and over 600 muscles.",
        "Regular exercise can increase your life expectancy by 7 years.",
        "The average person takes 20,000 breaths per day.",
        "The human heart beats 2.5 billion times in a lifetime.",
        "The average person spends 6 years of their life eating."
    ],
    "Technology Updates": [
        "The first computer virus was created in 1983 and was called 'Elk Cloner'.",
        "The average smartphone has 10x more computing power than the Apollo 11 spacecraft.",
        "There are now more than 7 billion smartphone users worldwide.",
        "The first website is still online: info.cern.ch.",
        "The average person checks their phone 96 times per day.",
        "Artificial Intelligence will create 97 million new jobs by 2025.",
        "The first commercial computer weighed 29 tons.",
        "The internet has increased the global average IQ by 7 points.",
        "The average person spends 2.5 hours per day on social media.",
        "The first email was sent in 1971.",
        "The world's fastest supercomputer can perform 1.1 billion billion calculations per second.",
        "The average person will spend 2 years of their life on social media.",
        "Voice assistants like Siri and Alexa have 500 million active users.",
        "The first computer mouse was made of wood in 1964.",
        "Cloud computing has reduced IT costs by 40% for businesses.",
        "The average person uses 36 apps per month.",
        "The first website went live in 1991.",
        "AI can now outperform humans in facial recognition and natural language processing.",
        "The internet has more than 1.8 billion websites.",
        "The average person spends 6 hours per day on the internet.",
        "5G networks are 100 times faster than 4G.",
        "The first iPhone was released in 2007, 16 years ago.",
        "The average person will generate 1.7 MB of data per second.",
        "There are 5 billion internet users worldwide."
    ]
}

# ------------------- API ENDPOINTS -------------------

@app.route('/')
def home():
    return jsonify({
        "message": "One Minute Knowledge API",
        "endpoints": {
            "/api/daily": "Get today's daily fact",
            "/api/topic/<topic_name>": "Get random fact for a specific topic",
            "/api/topics": "Get all topic names",
            "/api/all-facts": "Get all facts organized by topic",
            "/api/random-fact": "Get random fact from any topic",
            "/api/subscription/plans": "Get all subscription plans",
            "/api/subscription/subscribe": "Subscribe to a plan (POST)"
        }
    })

@app.route('/api/daily')
def get_daily_fact():
    today = datetime.now()
    day_of_year = today.timetuple().tm_yday
    fact_index = day_of_year % len(DAILY_FACTS)
    return jsonify({
        "fact": DAILY_FACTS[fact_index],
        "date": today.strftime("%Y-%m-%d"),
        "day": today.strftime("%A")
    })

@app.route('/api/topics')
def get_topics():
    return jsonify(list(TOPIC_FACTS.keys()))

@app.route('/api/topic/<topic_name>')
def get_topic_fact(topic_name):
    matching_topic = None
    for key in TOPIC_FACTS.keys():
        if key.lower() == topic_name.lower():
            matching_topic = key
            break
    
    if matching_topic:
        facts = TOPIC_FACTS[matching_topic]
        return jsonify({
            "topic": matching_topic,
            "fact": random.choice(facts)
        })
    else:
        return jsonify({
            "error": f"Topic '{topic_name}' not found",
            "available_topics": list(TOPIC_FACTS.keys())
        }), 404

@app.route('/api/random-fact')
def get_random_fact():
    topics = list(TOPIC_FACTS.keys())
    random_topic = random.choice(topics)
    facts = TOPIC_FACTS[random_topic]
    return jsonify({
        "topic": random_topic,
        "fact": random.choice(facts)
    })

@app.route('/api/all-facts')
def get_all_facts():
    return jsonify(TOPIC_FACTS)

# ------------------- SUBSCRIPTION ENDPOINTS -------------------

@app.route('/api/subscription/plans', methods=['GET'])
def get_subscription_plans():
    """Get all subscription plans"""
    return jsonify(SUBSCRIPTION_PLANS)

@app.route('/api/subscription/subscribe', methods=['POST'])
def subscribe():
    """Subscribe to a plan (simulated payment)"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        card_number = data.get('card_number', '').replace(' ', '').replace('-', '')
        card_expiry = data.get('card_expiry')
        card_cvv = data.get('card_cvv')
        
        if not plan_id or plan_id not in SUBSCRIPTION_PLANS:
            return jsonify({
                "success": False,
                "message": "Invalid plan selected"
            }), 400
        
        # Simulate payment validation
        if len(card_number) != 16 or not card_number.isdigit():
            return jsonify({
                "success": False,
                "message": "Invalid card number. Please enter a 16-digit card number."
            }), 400
        
        if not card_expiry or len(card_expiry) != 5 or '/' not in card_expiry:
            return jsonify({
                "success": False,
                "message": "Invalid expiry date. Please use MM/YY format."
            }), 400
        
        if not card_cvv or len(card_cvv) != 3 or not card_cvv.isdigit():
            return jsonify({
                "success": False,
                "message": "Invalid CVV. Please enter a 3-digit CVV."
            }), 400
        
        plan = SUBSCRIPTION_PLANS[plan_id]
        now = datetime.now()
        expiry_date = now + timedelta(days=plan['duration'])
        
        # Generate a fake transaction ID
        transaction_id = f"TX-{random.randint(100000, 999999)}-{random.randint(100, 999)}"
        
        # Return success response
        return jsonify({
            "success": True,
            "message": f"Successfully subscribed to {plan['name']}!",
            "transaction_id": transaction_id,
            "plan": plan,
            "start_date": now.strftime("%Y-%m-%d"),
            "expiry_date": expiry_date.strftime("%Y-%m-%d")
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Payment failed: {str(e)}"
        }), 400

if __name__ == '__main__':
    total_facts = sum(len(facts) for facts in TOPIC_FACTS.values())
    print("\n" + "="*60)
    print("🚀 ONE MINUTE KNOWLEDGE API")
    print("="*60)
    print(f"📍 Running at: http://localhost:5000")
    print(f"📚 Total facts: {total_facts} facts across {len(TOPIC_FACTS)} topics")
    print(f"💳 Subscription plans loaded: {len(SUBSCRIPTION_PLANS)}")
    print("\n📖 Available endpoints:")
    print("   GET /api/daily              - Today's daily fact")
    print("   GET /api/topics             - List all topics")
    print("   GET /api/topic/<name>       - Random fact for a topic")
    print("   GET /api/random-fact        - Random fact from any topic")
    print("   GET /api/all-facts          - All facts organized by topic")
    print("   GET /api/subscription/plans - Get subscription plans")
    print("   POST /api/subscription/subscribe - Subscribe to a plan")
    print("\n💡 Examples:")
    print("   http://localhost:5000/api/topic/Career%20Tips")
    print("   http://localhost:5000/api/daily")
    print("   http://localhost:5000/api/subscription/plans")
    print("\n🌐 Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
