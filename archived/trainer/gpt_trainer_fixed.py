"""
Betty AI GPT Trainer Module

This module provides functionality to train Betty AI using GPT as a trainer.
Betty learns patterns, emotions, and response styles from GPT, with the ability
to eventually operate independently once trained.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

# Configure logging
# --- ADDED FOR GPT CALL ---
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def call_gpt(text: str, context: Optional[List[Dict]] = None) -> str:
    messages = [{"role": "system",
                 "content": "คุณคือ Betty พูดไทย สุภาพ ฉลาด อ่อนโยน"},
                {"role": "user",
                 "content": text}]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"[GPT ERROR] {e}")
        return "ขอโทษค่ะ ฉันยังตอบไม่ได้ในตอนนี้"


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/betty_trainer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BettyGPTTrainer")


class GPTController:
    """
    Controls GPT usage across the system, with ability to switch between
    training, assistance, and independent modes.
    """
    MODES = ["train", "assist", "off"]

    def __init__(self, mode: str = "train", config_path: str = "config.env"):
        """
        Initialize the GPT controller.

        Args:
            mode: Operating mode - "train" (full GPT learning),
                  "assist" (GPT helps when needed), or "off" (Betty operates independently)
            config_path: Path to configuration file
        """
        if mode not in self.MODES:
            raise ValueError(f"Mode must be one of {self.MODES}")

        self.mode = mode
        self.config_path = config_path
        self.config = self._load_config()

        # Set default if not specified
        if "USE_GPT" not in self.config:
            self.config["USE_GPT"] = (mode != "off")

        logger.info(f"GPTController initialized in {mode} mode")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        config = {}

        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        # Convert string booleans to actual booleans
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        config[key.strip()] = value

        return config

    def save_config(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, 'w') as f:
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")
        logger.info(f"Configuration saved to {self.config_path}")

    def set_mode(self, mode: str) -> None:
        """
        Change the operating mode.

        Args:
            mode: New mode to set
        """
        if mode not in self.MODES:
            raise ValueError(f"Mode must be one of {self.MODES}")

        self.mode = mode
        self.config["USE_GPT"] = (mode != "off")
        self.save_config()
        logger.info(f"Mode changed to {mode}")

    def is_gpt_enabled(self) -> bool:
        """Check if GPT is currently enabled."""
        return self.config.get("USE_GPT", False)

    def get_mode(self) -> str:
        """Get the current operating mode."""
        return self.mode

    def _call_gpt_api(self, messages, system_prompt=None):
        import os

        import openai

        # ใช้ API key จาก environment variable
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            logger.error("GPT API key not found in environment")
            return "ไม่พบ API key สำหรับ GPT ในไฟล์ config"

        openai.api_key = api_key

        if system_prompt:
            all_messages = [{"role": "system", "content": system_prompt}]
            all_messages.extend(messages)
        else:
            all_messages = messages

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=all_messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message["content"]
        except Exception as e:
            logger.error(f"Error calling GPT API: {e}")
            return f"ขออภัย ไม่สามารถเชื่อมต่อกับ GPT API ได้: {str(e)}"


class EmotionAnalyzer:
    """
    Analyzes emotions in text using GPT or fallback methods.
    """

    def __init__(self, gpt_controller: GPTController):
        """
        Initialize the emotion analyzer.

        Args:
            gpt_controller: Controller for GPT usage
        """
        self.gpt_controller = gpt_controller
        self.emotional_keywords = {
            "happy": ["happy", "joy", "pleased", "delighted", "content", "satisfied"],
            "sad": ["sad", "unhappy", "depressed", "down", "miserable", "gloomy"],
            "angry": ["angry", "mad", "furious", "irritated", "annoyed", "enraged"],
            "afraid": ["afraid", "scared", "fearful", "terrified", "anxious", "worried"],
            "surprised": ["surprised", "amazed", "astonished", "shocked", "stunned"],
            "disgusted": ["disgusted", "repulsed", "revolted", "appalled"],
            "neutral": ["neutral", "indifferent", "impartial", "unbiased"]
        }
        logger.info("EmotionAnalyzer initialized")

    def use_gpt_for_emotion(self, text: str) -> Dict[str, Any]:
        """
        Analyze emotions in text using GPT or fallback to keyword-based analysis.

        Args:
            text: Input text to analyze

        Returns:
            Dict with emotion and intensity
        """
        if self.gpt_controller.is_gpt_enabled():
            try:
                # Here you would call the GPT API
                # This is a placeholder for the actual GPT API call
                logger.info("Using GPT for emotion analysis")

                # Simulated GPT response for now
                # In a real implementation, this would call the actual GPT API
                return self._call_gpt_emotion_api(text)
            except Exception as e:
                logger.error(f"Error using GPT for emotion: {e}")
                logger.info("Falling back to local emotion analysis")
                return self.fallback_emotion_analysis(text)
        else:
            logger.info("GPT disabled, using local emotion analysis")
            return self.fallback_emotion_analysis(text)

    def _call_gpt_emotion_api(self, text: str) -> Dict[str, Any]:
        """
        Call GPT API for emotion analysis (placeholder).

        In a real implementation, this would make an API call to GPT.
        For now, it returns a simulated response.

        Args:
            text: Text to analyze

        Returns:
            Emotion analysis result
        """
        # This is where you'd implement the actual GPT API call
        # For demonstration, we'll return a simulated response

        # Simple keyword-based simulation for demonstration
        lower_text = text.lower()

        # Default emotion
        emotion = "neutral"
        intensity = 0.5

        # Very basic emotion detection logic for demonstration
        for emotion_name, keywords in self.emotional_keywords.items():
            for keyword in keywords:
                if keyword in lower_text:
                    emotion = emotion_name
                    # Calculate a basic intensity based on word count
                    word_count = lower_text.count(keyword)
                    intensity = min(0.5 + (word_count * 0.1), 1.0)
                    break

        return {
            "emotion": emotion,
            "intensity": round(intensity, 2)
        }

    def fallback_emotion_analysis(self, text: str) -> Dict[str, Any]:
        """
        Perform emotion analysis without GPT.

        Args:
            text: Text to analyze

        Returns:
            Dict with emotion and intensity
        """
        lower_text = text.lower()

        # Default values
        emotion = "neutral"
        max_intensity = 0.5

        # Count emotional words in text
        emotion_counts = {}
        for emotion_name, keywords in self.emotional_keywords.items():
            count = 0
            for keyword in keywords:
                count += lower_text.count(keyword)
            emotion_counts[emotion_name] = count

        # Find most prevalent emotion
        if emotion_counts:
            max_count = 0
            for emotion_name, count in emotion_counts.items():
                if count > max_count:
                    max_count = count
                    emotion = emotion_name

            # Calculate intensity based on prevalence
            if max_count > 0:
                max_intensity = min(0.5 + (max_count * 0.1), 1.0)

        return {
            "emotion": emotion,
            "intensity": round(max_intensity, 2)
        }


class ResponsePatternAnalyzer:
    """
    Analyzes conversation patterns and suggests appropriate response styles.
    """

    def __init__(self, gpt_controller: GPTController):
        """
        Initialize the response pattern analyzer.

        Args:
            gpt_controller: Controller for GPT usage
        """
        self.gpt_controller = gpt_controller

        # Define common patterns and suggested response styles
        self.patterns = {
            "self_doubt": {
                "keywords": [
                    "can't",
                    "never good enough",
                    "failure",
                    "worthless",
                    "not smart enough"],
                "response_style": "encouraging"},
            "seeking_advice": {
                "keywords": [
                    "should I",
                    "what would you do",
                    "your opinion",
                    "what do you think"],
                "response_style": "thoughtful"},
            "angry": {
                "keywords": [
                    "angry",
                    "mad",
                    "furious",
                    "hate",
                    "terrible"],
                "response_style": "calming"},
            "excited": {
                "keywords": [
                    "excited",
                    "amazing",
                    "awesome",
                    "great news",
                    "wonderful"],
                "response_style": "enthusiastic"}}
        logger.info("ResponsePatternAnalyzer initialized")

    def use_gpt_for_response_pattern(
            self, text: str, context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Analyze conversation patterns and suggest response styles.

        Args:
            text: Current message text
            context: Previous messages for context

        Returns:
            Dict with detected pattern and suggested response style
        """
        if self.gpt_controller.is_gpt_enabled():
            try:
                # Here you would call the GPT API
                logger.info("Using GPT for response pattern analysis")
                return self._call_gpt_pattern_api(text, context)
            except Exception as e:
                logger.error(f"Error using GPT for pattern analysis: {e}")
                logger.info("Falling back to local pattern analysis")
                return self.fallback_pattern_analysis(text)
        else:
            logger.info("GPT disabled, using local pattern analysis")
            return self.fallback_pattern_analysis(text)

    def _call_gpt_pattern_api(
            self, text: str, context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Call GPT API for pattern analysis (placeholder).

        Args:
            text: Current message text
            context: Previous messages for context

        Returns:
            Pattern analysis result
        """
        # In a real implementation, this would make an API call to GPT
        # For now, we'll use a simple keyword-based approach

        # If no context provided, initialize empty list
        if context is None:
            context = []

        lower_text = text.lower()

        # Default pattern
        pattern = "general"
        response_style = "neutral"
        confidence = 0.5

        # Combine current text with recent context
        combined_text = lower_text
        for ctx in context[-3:]:  # Look at last 3 messages for context
            if "content" in ctx:
                combined_text += " " + ctx["content"].lower()

        # Very basic pattern detection for demonstration
        for pattern_name, pattern_info in self.patterns.items():
            for keyword in pattern_info["keywords"]:
                if keyword in combined_text:
                    pattern = pattern_name
                    response_style = pattern_info["response_style"]
                    # Basic confidence calculation
                    keyword_count = combined_text.count(keyword)
                    confidence = min(0.6 + (keyword_count * 0.1), 1.0)
                    break

        return {
            "pattern": pattern,
            "response_style": response_style,
            "confidence": round(confidence, 2),
            "suggestions": [
                f"Respond in a {response_style} manner",
                f"Address the {pattern} sentiment"
            ]
        }

    def fallback_pattern_analysis(self, text: str) -> Dict[str, Any]:
        """
        Analyze patterns without GPT.

        Args:
            text: Text to analyze

        Returns:
            Pattern analysis result
        """
        lower_text = text.lower()

        # Default pattern
        pattern = "general"
        response_style = "neutral"
        confidence = 0.5

        # Count pattern keywords
        pattern_scores = {}
        for pattern_name, pattern_info in self.patterns.items():
            score = 0
            for keyword in pattern_info["keywords"]:
                if keyword in lower_text:
                    score += lower_text.count(keyword)

            if score > 0:
                pattern_scores[pattern_name] = score

        # Find highest scoring pattern
        if pattern_scores:
            max_score = 0
            for p_name, score in pattern_scores.items():
                if score > max_score:
                    max_score = score
                    pattern = p_name
                    response_style = self.patterns[p_name]["response_style"]

            # Calculate confidence based on score
            if max_score > 0:
                confidence = min(0.6 + (max_score * 0.1), 1.0)

        return {
            "pattern": pattern,
            "response_style": response_style,
            "confidence": round(confidence, 2),
            "suggestions": [
                f"Respond in a {response_style} manner",
                f"Address the {pattern} sentiment"
            ]
        }


class MemoryCapsuleManager:
    """
    Creates and manages memory capsules for Betty's learning.
    """

    def __init__(self, gpt_controller: GPTController):
        """
        Initialize the memory capsule manager.

        Args:
            gpt_controller: Controller for GPT usage
        """
        self.gpt_controller = gpt_controller
        self.capsule_store_path = "memory/capsule"
        self.ensure_dir_exists(self.capsule_store_path)
        logger.info("MemoryCapsuleManager initialized")

    def ensure_dir_exists(self, directory: str) -> None:
        """Ensure the directory exists, create if not."""
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

    def use_gpt_to_create_memory_capsule(
        self, text: str, response: str, emotion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a memory capsule from conversation data.

        Args:
            text: User's message
            response: Betty's response
            emotion: Emotion analysis result

        Returns:
            Memory capsule data
        """
        if self.gpt_controller.is_gpt_enabled():
            try:
                logger.info("Using GPT to create memory capsule")
                return self._call_gpt_capsule_api(text, response, emotion)
            except Exception as e:
                logger.error(f"Error using GPT for capsule creation: {e}")
                logger.info("Falling back to local capsule creation")
                return self.fallback_create_capsule(text, response, emotion)
        else:
            logger.info("GPT disabled, using local capsule creation")
            return self.fallback_create_capsule(text, response, emotion)

    def _call_gpt_capsule_api(
        self, text: str, response: str, emotion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call GPT API to create a memory capsule (placeholder).

        Args:
            text: User's message
            response: Betty's response
            emotion: Emotion analysis result

        Returns:
            Memory capsule data
        """
        # In a real implementation, this would make an API call to GPT
        # For now, we'll create a basic capsule structure

        # Extract basic topics from the text
        topics = self._extract_basic_topics(text)

        # Create timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Generate a simple capsule structure
        capsule = {
            "id": f"capsule_{timestamp}",
            "timestamp": timestamp,
            "topic": topics[0] if topics else "general",
            "subtopics": topics[1:3] if len(topics) > 1 else [],
            "user_input": text,
            "betty_response": response,
            "emotion": emotion,
            "tags": topics + [emotion["emotion"]],
            "lessons": [
                {
                    "context": "user emotion detection",
                    "pattern": f"When user expresses {emotion['emotion']}, respond with empathy",
                    "importance": emotion["intensity"]
                }
            ],
            "insights": [
                f"User expressed {emotion['emotion']} about {topics[0] if topics else 'general topic'}"
            ],
            "related_memories": []
        }

        # Save the capsule
        self._save_capsule(capsule)

        return capsule

    def _extract_basic_topics(self, text: str) -> List[str]:
        """
        Extract basic topics from text using keyword frequency.

        Args:
            text: Text to analyze

        Returns:
            List of potential topics
        """
        import re
        from collections import Counter

        # Remove common words and prepositions
        common_words = {
            "the",
            "and",
            "a",
            "an",
            "in",
            "on",
            "at",
            "to",
            "for",
            "with",
            "of",
            "by",
            "as",
            "is",
            "are",
            "am",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "shall",
            "should",
            "may",
            "might",
            "must",
            "can",
            "could",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them"}

        # Split into words and clean
        words = re.findall(r'\b\w+\b', text.lower())
        filtered_words = [
            word for word in words if word not in common_words and len(word) > 3]

        # Count frequency and get top words
        word_counts = Counter(filtered_words)
        return [word for word, _ in word_counts.most_common(5)]

    def _save_capsule(self, capsule: Dict[str, Any]) -> None:
        """
        Save a memory capsule to storage.

        Args:
            capsule: Memory capsule to save
        """
        # Create a filename based on the capsule ID
        filename = f"{self.capsule_store_path}/{capsule['id']}.json"

        with open(filename, 'w') as f:
            json.dump(capsule, f, indent=2)

        logger.info(f"Saved memory capsule: {filename}")

    def fallback_create_capsule(
        self, text: str, response: str, emotion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a memory capsule without GPT.

        Args:
            text: User's message
            response: Betty's response
            emotion: Emotion analysis result

        Returns:
            Memory capsule data
        """
        # Extract basic keywords as topics
        topics = self._extract_basic_topics(text)

        # Create timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Create a simple capsule with basic structure
        capsule = {
            "id": f"capsule_{timestamp}",
            "timestamp": timestamp,
            "topic": topics[0] if topics else "general",
            "subtopics": topics[1:3] if len(topics) > 1 else [],
            "user_input": text,
            "betty_response": response,
            "emotion": emotion,
            "tags": topics + [emotion["emotion"]],
            "lessons": [
                {
                    "context": "conversation",
                    "pattern": f"When topic is about {topics[0] if topics else 'general'}, note emotional tone",
                    "importance": 0.7
                }
            ],
            "insights": [
                f"Remember this {emotion['emotion']} conversation about {topics[0] if topics else 'this topic'}"
            ],
            "related_memories": []
        }

        # Save the capsule
        self._save_capsule(capsule)

        return capsule


class BettyTrainer:
    """
    Trains Betty using memory capsules created by GPT.
    """

    def __init__(self, gpt_controller: GPTController):
        """
        Initialize the Betty trainer.

        Args:
            gpt_controller: Controller for GPT usage
        """
        self.gpt_controller = gpt_controller
        self.capsule_store_path = "memory/capsule"
        self.lessons_path = "memory/lessons"
        self.ensure_dirs_exist()
        self.learned_patterns = self._load_learned_patterns()
        logger.info("BettyTrainer initialized")

    def ensure_dirs_exist(self) -> None:
        """Ensure required directories exist."""
        for directory in [self.capsule_store_path, self.lessons_path]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")

    def _load_learned_patterns(self) -> Dict[str, Any]:
        """
        Load previously learned patterns.

        Returns:
            Dict of learned patterns
        """
        pattern_file = f"{self.lessons_path}/learned_patterns.json"

        if os.path.exists(pattern_file):
            try:
                with open(pattern_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading learned patterns: {e}")
                return {"topics": {}, "emotions": {}, "response_styles": {}}
        else:
            return {"topics": {}, "emotions": {}, "response_styles": {}}

    def _save_learned_patterns(self) -> None:
        """Save learned patterns to disk."""
        pattern_file = f"{self.lessons_path}/learned_patterns.json"

        with open(pattern_file, 'w') as f:
            json.dump(self.learned_patterns, f, indent=2)

        logger.info("Saved learned patterns")

    def train_betty_on_capsule(self, capsule: Dict[str, Any]) -> None:
        """
        Train Betty using a memory capsule.

        Args:
            capsule: Memory capsule to learn from
        """
        logger.info(f"Training Betty on capsule: {capsule['id']}")

        # Extract key information from the capsule
        topic = capsule.get("topic", "general")
        emotion = capsule.get("emotion", {}).get("emotion", "neutral")
        user_input = capsule.get("user_input", "")
        betty_response = capsule.get("betty_response", "")
        lessons = capsule.get("lessons", [])

        # Update topic knowledge
        if topic not in self.learned_patterns["topics"]:
            self.learned_patterns["topics"][topic] = {
                "examples": [],
                "related_emotions": {},
                "common_responses": {}
            }

        # Add this example
        self.learned_patterns["topics"][topic]["examples"].append({
            "input": user_input,
            "response": betty_response,
            "emotion": emotion
        })

        # Update emotion statistics for this topic
        emotion_stats = self.learned_patterns["topics"][topic]["related_emotions"]
        emotion_stats[emotion] = emotion_stats.get(emotion, 0) + 1

        # Learn from specific lessons
        for lesson in lessons:
            context = lesson.get("context", "")
            pattern = lesson.get("pattern", "")
            importance = lesson.get("importance", 0.5)

            # Skip if insufficient data
            if not context or not pattern:
                continue

            # Add to response styles
            if context not in self.learned_patterns["response_styles"]:
                self.learned_patterns["response_styles"][context] = []

            # Add this pattern if new
            if pattern not in [
                    p["pattern"] for p in self.learned_patterns["response_styles"][context]]:
                self.learned_patterns["response_styles"][context].append({
                    "pattern": pattern,
                    "importance": importance,
                    "examples": [betty_response]
                })

        # Save updated patterns
        self._save_learned_patterns()
        logger.info(f"Successfully trained on capsule {capsule['id']}")

    def fallback_to_local_response(self, text: str) -> str:
        """
        Generate a response using trained knowledge when GPT is unavailable.

        Args:
            text: User's input text

        Returns:
            Generated response
        """
        logger.info("Generating local response based on training")

        # Extract potential topics from input
        potential_topics = self._extract_topics_from_input(text)

        # Find best matching topic
        best_topic = self._find_best_matching_topic(potential_topics)

        # If we have examples for this topic, use them
        if best_topic and best_topic in self.learned_patterns["topics"]:
            topic_data = self.learned_patterns["topics"][best_topic]

            # If we have examples, use the most relevant one
            if topic_data["examples"]:
                # Simple approach: find example with most similar input
                most_similar = self._find_most_similar_example(
                    text, topic_data["examples"])
                if most_similar:
                    return most_similar["response"]

        # Fallback to a generic response if no matching topic or examples
        return "I understand what you're saying. Can you tell me more about that?"

    def _extract_topics_from_input(self, text: str) -> List[str]:
        """
        Extract potential topics from user input.

        Args:
            text: User's input text

        Returns:
            List of potential topics
        """
        import re
        from collections import Counter

        # Remove common words
        common_words = {
            "the", "and", "a", "an", "in", "on", "at", "to", "for", "with",
            "of", "by", "as", "is", "are", "am", "was", "were", "be", "been"
        }

        # Split text into words and clean
        words = re.findall(r'\b\w+\b', text.lower())
        filtered_words = [
            word for word in words if word not in common_words and len(word) > 3]

        # Count frequency
        return [word for word, _ in Counter(filtered_words).most_common(5)]

    def _find_best_matching_topic(
            self, potential_topics: List[str]) -> Optional[str]:
        """
        Find the best matching topic from learned patterns.

        Args:
            potential_topics: List of potential topics from user input

        Returns:
            Best matching topic or None
        """
        # If no topics extracted or no learned topics, return None
        if not potential_topics or not self.learned_patterns["topics"]:
            return None

        # Check for direct matches first
        for topic in potential_topics:
            if topic in self.learned_patterns["topics"]:
                return topic

        # If no direct match, compare words in topics
        best_match = None
        best_score = 0

        for user_topic in potential_topics:
            for known_topic in self.learned_patterns["topics"].keys():
                # Simple word overlap score
                user_words = set(user_topic.lower().split())
                known_words = set(known_topic.lower().split())
                intersection = user_words.intersection(known_words)

                if intersection:
                    score = len(intersection) / \
                        max(len(user_words), len(known_words))
                    if score > best_score:
                        best_score = score
                        best_match = known_topic

        # Return best match if score is reasonable
        return best_match if best_score > 0.3 else None

    def _find_most_similar_example(
            self, text: str, examples: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the most similar example from the list.

        Args:
            text: User's input text
            examples: List of example conversations

        Returns:
            Most similar example or None
        """
        if not examples:
            return None

        # Convert text to lowercase for comparison
        text = text.lower()

        # Simple word overlap similarity
        best_match = None
        best_score = 0

        for example in examples:
            example_input = example["input"].lower()

            # Calculate word overlap
            text_words = set(text.split())
            example_words = set(example_input.split())
            intersection = text_words.intersection(example_words)

            if intersection:
                score = len(intersection) / \
                    max(len(text_words), len(example_words))
                if score > best_score:
                    best_score = score
                    best_match = example

        # Return best match if score is reasonable
        return best_match if best_score > 0.2 else None


class BettyGPTTrainer:
    """
    Main class that integrates all components for Betty's training.
    """

    def __init__(self, mode: str = "train"):
        """
        Initialize the Betty GPT Trainer.

        Args:
            mode: Operating mode for GPT
        """
        # Initialize the controller
        self.gpt_controller = GPTController(mode=mode)

        # Initialize all components
        self.emotion_analyzer = EmotionAnalyzer(self.gpt_controller)
        self.pattern_analyzer = ResponsePatternAnalyzer(self.gpt_controller)
        self.capsule_manager = MemoryCapsuleManager(self.gpt_controller)
        self.betty_trainer = BettyTrainer(self.gpt_controller)

        logger.info(f"BettyGPTTrainer initialized in {mode} mode")

    def set_mode(self, mode: str) -> None:
        """
        Change the operating mode.

        Args:
            mode: New mode to set
        """
        self.gpt_controller.set_mode(mode)
        logger.info(f"Mode changed to {mode}")

    def process_interaction(
            self, user_input: str, context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Process a user interaction and generate a response.

        Args:
            user_input: User's input text
            context: Previous messages for context

        Returns:
            Dict with response and analysis data
        """
        if context is None:
            context = []

        logger.info(f"Processing user input: {user_input[:50]}...")

        # Step 1: Analyze emotions
        emotion_result = self.emotion_analyzer.use_gpt_for_emotion(user_input)

        # Step 2: Analyze conversation pattern
        pattern_result = self.pattern_analyzer.use_gpt_for_response_pattern(
            user_input, context)

        # Step 3: Generate response (using GPT or local knowledge)
        if self.gpt_controller.is_gpt_enabled():
            # In a real implementation, this would call GPT for the response
            # For now, use a template-based approach
            response = self.gpt_controller._call_gpt_api(
                [{"role": "user", "content": user_input}])
        else:
            # Use locally trained knowledge
            response = self.betty_trainer.fallback_to_local_response(
                user_input)

        # Step 4: Create memory capsule
        capsule = self.capsule_manager.use_gpt_to_create_memory_capsule(
            user_input, response, emotion_result
        )

        # Step 5: Train Betty with the new capsule
        self.betty_trainer.train_betty_on_capsule(capsule)

        # Return complete interaction data
        return {
            "user_input": user_input,
            "response": response,
            "emotion": emotion_result,
            "pattern": pattern_result,
            "memory_capsule": capsule
        }

    def _generate_template_response(
        self, text: str, emotion: Dict[str, Any], pattern: Dict[str, Any]
    ) -> str:
        """
        Generate a template-based response based on emotion and pattern analysis.

        Args:
            text: User's input text
            emotion: Emotion analysis result
            pattern: Pattern analysis result

        Returns:
            Generated response
        """
        # Get the detected emotion and pattern
        detected_emotion = emotion.get("emotion", "neutral")
        emotion.get("intensity", 0.5)
        response_style = pattern.get("response_style", "neutral")

        # Simple template-based responses
        templates = {
            "happy": [
                "I'm so glad to hear that! Tell me more.",
                "That sounds wonderful! I'm happy for you.",
                "It's great that you're feeling positive about this."
            ],
            "sad": [
                "I'm sorry to hear that. Is there anything I can do?",
                "That sounds difficult. I'm here for you.",
                "I understand this is hard. Let's talk through it."
            ],
            "angry": [
                "I can see why that would be frustrating.",
                "That situation does sound unfair.",
                "I understand why you'd feel that way."
            ],
            "afraid": [
                "It makes sense to be concerned about that.",
                "I understand your worries. Let's think about this together.",
                "Those fears are valid. Let's break this down."
            ],
            "surprised": [
                "Wow, that is unexpected!",
                "I can see why that would surprise you.",
                "That's quite a development!"
            ],
            "neutral": [
                "I understand what you're saying.",
                "That's an interesting point.",
                "Tell me more about that."
            ]
        }

        # Response style modifiers
        style_modifiers = {
            "encouraging": [
                "You're doing great with this.",
                "I believe in your ability to handle this.",
                "You've got this, and I'm here to support you."
            ],
            "thoughtful": [
                "Let's consider this from different angles.",
                "That's worth reflecting on more deeply.",
                "There are several perspectives to consider here."
            ],
            "calming": [
                "Let's take a step back and breathe.",
                "We can work through this calmly.",
                "Taking things one step at a time will help."
            ],
            "enthusiastic": [
                "That's amazing news!",
                "I'm really excited about this for you!",
                "This is such a wonderful development!"
            ],
            "neutral": [
                "I understand.",
                "That makes sense.",
                "I see what you mean."
            ]
        }

        import random

        # Select templates based on emotion and style
        emotion_template = random.choice(
            templates.get(
                detected_emotion,
                templates["neutral"]))
        style_modifier = random.choice(
            style_modifiers.get(
                response_style,
                style_modifiers["neutral"]))

        # Combine templates for a more nuanced response
        response = f"{emotion_template} {style_modifier}"

        # Add a follow-up question or comment based on the detected topic
        follow_ups = [
            "Would you like to talk more about this?",
            "How do you feel about this situation?",
            "What are you thinking of doing next?",
            "Is there a specific aspect you'd like to focus on?"
        ]

        # Add follow-up question with 70% probability
        if random.random() < 0.7:
            response += f" {random.choice(follow_ups)}"

        return response

    def batch_train(self, data_file: str) -> None:
        """
        Train Betty on a batch of example conversations.

        Args:
            data_file: Path to JSON file with training examples
        """
        if not os.path.exists(data_file):
            logger.error(f"Training data file not found: {data_file}")
            return

        try:
            with open(data_file, 'r') as f:
                training_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return

        logger.info(
            f"Starting batch training with {len(training_data)} examples")

        for i, example in enumerate(training_data):
            user_input = example.get("user_input", "")
            response = example.get("response", "")

            if not user_input or not response:
                continue

            # Process this example
            logger.info(f"Training on example {i+1}/{len(training_data)}")

            # Analyze emotion
            emotion_result = self.emotion_analyzer.use_gpt_for_emotion(
                user_input)

            # Create and train on a capsule
            capsule = self.capsule_manager.use_gpt_to_create_memory_capsule(
                user_input, response, emotion_result
            )
            self.betty_trainer.train_betty_on_capsule(capsule)

        logger.info(
            f"Batch training completed: {len(training_data)} examples processed")


def main():
    """
    Main function to demonstrate the Betty GPT Trainer.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Betty GPT Trainer")
    parser.add_argument(
        "--mode",
        type=str,
        default="train",
        choices=[
            "train",
            "assist",
            "off"],
        help="Operating mode for GPT")
    parser.add_argument(
        "--batch-train",
        type=str,
        help="Path to batch training data file")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive mode")

    args = parser.parse_args()

    # Initialize the trainer
    trainer = BettyGPTTrainer(mode=args.mode)

    # Batch training if specified
    if args.batch_train:
        trainer.batch_train(args.batch_train)

    # Interactive mode if specified
    if args.interactive:
        print("Starting Betty in interactive mode. Type 'quit' to exit.")
        print(f"GPT mode: {trainer.gpt_controller.get_mode()}")

        context = []

        while True:
            user_input = input("\nYou: ")

            if user_input.lower() in ["quit", "exit", "bye"]:
                print("Goodbye!")
                break

            if user_input.lower().startswith("mode "):
                mode = user_input.lower().split(" ")[1]
                if mode in ["train", "assist", "off"]:
                    trainer.set_mode(mode)
                    print(f"Mode changed to: {mode}")
                    continue

            # Process the input
            result = trainer.process_interaction(user_input, context)

            # Update context
            context.append({"role": "user", "content": user_input})
            context.append(
                {"role": "assistant", "content": result["response"]})

            # Keep context manageable
            if len(context) > 10:
                context = context[-10:]

            # Display the response
            print(f"\nBetty: {result['response']}")

            # Optionally show analysis
            if args.mode != "off":
                print(f"\nEmotion: {result['emotion']['emotion']} "
                      f"(intensity: {result['emotion']['intensity']})")
                print(f"Pattern: {result['pattern']['pattern']} "
                      f"(style: {result['pattern']['response_style']})")


if __name__ == "__main__":
    main()
