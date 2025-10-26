import warnings

warnings.filterwarnings("ignore")
from flask import Flask, render_template, request, jsonify
import joblib
import json
from slot_extraction import extract_order_id, conversation_state
from simulated_backend import simulated_backend_action

# Load Trained Model and Vectorizer
data = joblib.load("intent_model.pkl")
vectorizer_intent = data["vectorizer"]
model = data["model"]


# Load Intent → Response Mapping
with open("intents_responses.json", "r") as f:
    intent_responses = json.load(f)

app = Flask(__name__)


# Helper Functions
def get_response(intent):
    return intent_responses.get(intent, intent_responses["default"])


def handle_conversation(user_id, user_input, predicted_intent):
    """Handles conversation flow for order-related or other intents."""
    state = conversation_state.get(user_id, {"intent": None, "order_id": None})

    # Step 1: Detect intent if not set yet
    if state["intent"] is None:
        state["intent"] = predicted_intent
        conversation_state[user_id] = state
        return get_response(predicted_intent)

    # Step 2: Check for order ID (for order-related intents)
    if state["order_id"] is None:
        order_id = extract_order_id(user_input)
        if order_id:
            state["order_id"] = order_id
            conversation_state[user_id] = state
            return f"Order ID {order_id} received. Do you want to proceed with {state['intent'].replace('_', ' ')}? (yes/no)"
        else:
            return "Please provide your 5-10 digit order ID."

    # Step 3: Confirmation step
    if user_input.lower() in ["yes", "y"]:
        response = simulated_backend_action(state["intent"], state["order_id"])
        conversation_state[user_id] = {
            "intent": None,
            "order_id": None,
        }  # reset after operation
        return response
    elif user_input.lower() in ["no", "n"]:
        conversation_state[user_id] = {"intent": None, "order_id": None}
        return "Operation cancelled."

    # Default fallback
    return get_response(predicted_intent)


# Routes
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    user_id = "demo_user"  # single-user session for demo

    # Greeting detection
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(greet in user_input.lower() for greet in greetings):
        return jsonify({"response": intent_responses["greeting"], "intent": "greeting"})

    # Farewell / Thank You detection
    farewells = ["bye", "goodbye", "see you", "thank you", "thanks", "thanku", "thank"]
    if any(word in user_input.lower() for word in farewells):
        return jsonify({"response": intent_responses["farewell"], "intent": "farewell"})

    # Transform input with TF-IDF
    user_input_tfidf = vectorizer_intent.transform([user_input])

    # Predict intent
    predicted_intent = model.predict(user_input_tfidf)[0]

    # Handle conversation & response
    response = handle_conversation(user_id, user_input, predicted_intent)

    return jsonify({"response": response, "intent": predicted_intent})


# Run app
if __name__ == "__main__":
    app.run(debug=True)
