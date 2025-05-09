"""Betty AI Server with ReflexOS Integration

This module integrates the Betty GPT Trainer system with the ReflexOS environment,
providing a complete server implementation that can be run within the project structure.
"""


from gpt_trainer import BettyGPTTrainer
import datetime
import json
import logging
import os
import sys
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

# Add core directory to path to import fix_gpt_trainer as gpt_trainer
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

# Import the BettyGPTTrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/betty_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BettyServer")

# Initialize Flask app
app = Flask(__name__,
            template_folder='core/templates',
            static_folder='core/static'
            )

# Global variables
conversation_history = {}
betty_trainer = None
memory_path = 'memory'


def initialize_betty(mode: str = "train") -> None:
    """
    Initialize Betty with the specified mode.

    Args:
        mode: Operating mode ("train", "assist", or "off")
    """
    global betty_trainer

    # Ensure memory directories exist
    os.makedirs(os.path.join(memory_path, 'capsule'), exist_ok=True)
    os.makedirs(os.path.join(memory_path, 'emotion'), exist_ok=True)
    os.makedirs(os.path.join(memory_path, 'extended'), exist_ok=True)
    os.makedirs(os.path.join(memory_path, 'longterm'), exist_ok=True)
    os.makedirs(os.path.join(memory_path, 'stack'), exist_ok=True)

    # Initialize Betty
    betty_trainer = BettyGPTTrainer(mode=mode)
    logger.info(f"Betty initialized in {mode} mode")


def save_conversation_to_memory(
        user_id: str, conversation: Dict[str, Any]) -> None:
    """
    Save conversation data to Betty's memory system.

    Args:
        user_id: User identifier
        conversation: Conversation data
    """
    # Save to memory stack
    stack_file = os.path.join(memory_path, 'stack', f'{user_id}_stack.json')

    # Load existing stack or create new
    if os.path.exists(stack_file):
        try:
            with open(stack_file, 'r') as f:
                stack = json.load(f)
        except BaseException:
            stack = {"messages": []}
    else:
        stack = {"messages": []}

    # Add new message
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stack["messages"].append(
        {
            "timestamp": timestamp, "user_input": conversation.get(
                "user_input", ""), "betty_response": conversation.get(
                "response", ""), "emotion": conversation.get(
                    "emotion", {}), "memory_capsule_id": conversation.get(
                        "memory_capsule", {}).get(
                            "id", "")})

    # Save updated stack
    with open(stack_file, 'w') as f:
        json.dump(stack, f, indent=2)

    # Save emotion to emotion log
    emotion_file = os.path.join(
        memory_path,
        'emotion',
        f'{user_id}_emotion.json')

    # Load existing emotions or create new
    if os.path.exists(emotion_file):
        try:
            with open(emotion_file, 'r') as f:
                emotions = json.load(f)
        except BaseException:
            emotions = {"emotions": []}
    else:
        emotions = {"emotions": []}

    # Add new emotion
    emotions["emotions"].append({
        "timestamp": timestamp,
        "emotion": conversation.get("emotion", {}).get("emotion", "neutral"),
        "intensity": conversation.get("emotion", {}).get("intensity", 0.5),
        "context": "user_message",
        # First 100 chars for context
        "text": conversation.get("user_input", "")[:100]
    })

    # Save updated emotions
    with open(emotion_file, 'w') as f:
        json.dump(emotions, f, indent=2)

    logger.info(f"Conversation saved to memory for user {user_id}")


@app.route('/')
def index():
    """Render the main UI page."""
    return render_template('index.html', title="Betty AI - ReflexOS Hybrid")


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat API requests."""
    data = request.json
    user_id = data.get('user_id', 'user_a')
    message = data.get('message', '')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Initialize conversation history for this user if not exists
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Format conversation history for GPT
    history = []
    for entry in conversation_history[user_id][-5:]:  # Last 5 messages
        history.append({"role": "user", "content": entry["user_input"]})
        history.append({"role": "assistant", "content": entry["response"]})

    # Process the message
    result = betty_trainer.process_interaction(message, history)

    # Save to conversation history
    conversation_history[user_id].append(result)

    # Save to memory system
    save_conversation_to_memory(user_id, result)

    # Return response to client
    return jsonify({
        "response": result["response"],
        "emotion": result["emotion"]["emotion"],
        "intensity": result["emotion"]["intensity"]
    })


@app.route('/api/get_history', methods=['GET'])
def get_history():
    """Get conversation history for a user."""
    user_id = request.args.get('user_id', 'user_a')

    # Load from memory stack
    stack_file = os.path.join(memory_path, 'stack', f'{user_id}_stack.json')

    if os.path.exists(stack_file):
        try:
            with open(stack_file, 'r') as f:
                stack = json.load(f)
            return jsonify(stack)
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"messages": []})


@app.route('/api/set_mode', methods=['POST'])
def set_mode():
    """Change Betty's operating mode."""
    data = request.json
    mode = data.get('mode', 'train')

    if mode not in ["train", "assist", "off"]:
        return jsonify({"error": "Invalid mode"}), 400

    try:
        betty_trainer.set_mode(mode)
        return jsonify({"success": True, "mode": mode})
    except Exception as e:
        logger.error(f"Error setting mode: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/get_memory_capsules', methods=['GET'])
def get_memory_capsules():
    """Get memory capsules for a user."""
    request.args.get('user_id', 'user_a')

    # Get list of capsule files
    capsule_dir = os.path.join(memory_path, 'capsule')
    capsules = []

    if os.path.exists(capsule_dir):
        for filename in os.listdir(capsule_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(capsule_dir, filename), 'r') as f:
                        capsule = json.load(f)
                    capsules.append(capsule)
                except Exception as e:
                    logger.error(f"Error loading capsule {filename}: {e}")

    return jsonify({"capsules": capsules})


def main():
    """Main function to run the Betty AI server."""
    import argparse

    parser = argparse.ArgumentParser(description="Betty AI Server")
    parser.add_argument(
        "--mode",
        type=str,
        default="train",
        choices=[
            "train",
            "assist",
            "off"],
        help="Operating mode for GPT")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    parser.add_argument(
        "--memory-path",
        type=str,
        default="memory",
        help="Path to memory storage")

    args = parser.parse_args()

    # Set memory path
    global memory_path
    memory_path = args.memory_path

    # Initialize Betty
    initialize_betty(mode=args.mode)

    # Run the Flask app
    app.run(host="0.0.0.0", port=args.port, debug=True)


if __name__ == "__main__":
    main()
