from datetime import datetime

from flask import Flask, jsonify, render_template, request


class WebContextUI:
    def __init__(self, memory_core, context_extender, emotion_layer):
        self.app = Flask(__name__)
        self.memory_core = memory_core
        self.context_extender = context_extender
        self.emotion_layer = emotion_layer

        # Set up routes
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html', dark_mode=True)

        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            data = request.json
            user_input = data.get('message', '')
            data.get('user_id', 'user_a')

            # Extend context
            self.context_extender.extend_context(user_input)

            # TODO: Here you would pass the extended context to your AI model
            # For this example, we'll just echo back a placeholder response
            response = f"Betty AI received: {user_input}"

            # Process emotion
            emotion = self.emotion_layer.process_user_input(
                user_input, response)

            # Create response data
            response_data = {
                'response': response,
                'emotion': emotion,
                'timestamp': datetime.now().isoformat()
            }

            return jsonify(response_data)

        @self.app.route('/api/memory', methods=['GET'])
        def get_memory():
            memory_summary = self.memory_core.get_memory_summary()
            emotional_trends = self.emotion_layer.get_emotional_trends()

            response_data = {
                'memory': memory_summary,
                'emotions': emotional_trends,
                'topics': self.context_extender.get_conversation_topics()
            }

            return jsonify(response_data)

    def run(self, host='0.0.0.0', port=5000, debug=True):
        self.app.run(host=host, port=port, debug=debug)
