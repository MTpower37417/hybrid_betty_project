import os
import re
from datetime import datetime


class ContextExtender:
    def __init__(self, memory_core, context_window=4096):
        self.memory_core = memory_core
        self.context_window = context_window  # Simulated token limit
        self.context_buffer = []
        self.char_to_token_ratio = 4  # Approximate ratio of characters to tokens

    def extend_context(self, current_input):
        """Extend the current context with relevant memories"""
        # Get relevant memories
        relevant_memories = self.memory_core.get_relevant_memories(
            current_input)

        # Create extended context
        extended_context = {
            "current_input": current_input,
            "relevant_memories": relevant_memories,
            "timestamp": datetime.now().isoformat()
        }

        # Add to buffer
        self.context_buffer.append(extended_context)
        if len(self.context_buffer) > 10:  # Keep last 10 extended contexts
            self.context_buffer.pop(0)

        # Build optimized context string
        return self.build_optimized_context(current_input, relevant_memories)

    def build_optimized_context(self, current_input, relevant_memories):
        """Build optimized context string based on token limits"""
        # Start with current input
        context_parts = [current_input]

        # Calculate approximate token count for current input
        approx_tokens_used = len(current_input) / self.char_to_token_ratio

        # Add relevant memories as long as we stay under the token limit
        for memory in relevant_memories:
            memory_text = memory.get("message", "")
            memory_tokens = len(memory_text) / self.char_to_token_ratio

            if approx_tokens_used + memory_tokens < self.context_window * 0.8:  # Keep 20% buffer
                context_parts.append(
                    f"Previous relevant memory: {memory_text}")
                approx_tokens_used += memory_tokens
            else:
                break

        # Combine all parts
        return "\n\n".join(context_parts)

    def save_extended_context(self, user_id, context_text):
        """Save extended context to file for later analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extended_context_{user_id}_{timestamp}.txt"

        # Ensure directory exists
        os.makedirs("./memory/extended", exist_ok=True)

        # Save context
        with open(f"./memory/extended/{filename}", "w", encoding="utf-8") as f:
            f.write(context_text)

        return filename

    def get_conversation_topics(self):
        """Extract main topics from the conversation context"""
        if not self.context_buffer:
            return []

        # Combine all inputs from buffer
        all_text = " ".join([ctx["current_input"]
                            for ctx in self.context_buffer])

        # Simple keyword extraction (can be improved with NLP)
        # Remove common words and extract potential topics
        common_words = {
            "a",
            "an",
            "the",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "and",
            "or",
            "but",
            "if",
            "then",
            "so",
            "that",
            "this",
            "these",
            "those",
            "it",
            "they",
            "them",
            "their",
            "ฉัน",
            "คุณ",
            "เรา",
            "มัน",
            "เขา",
            "เธอ",
            "พวกเขา",
            "ที่",
            "ซึ่ง",
            "อัน",
            "มี",
            "เป็น",
            "คือ",
            "อยู่"}

        words = re.findall(r'\b\w+\b', all_text.lower())
        word_counts = {}

        for word in words:
            if word not in common_words and len(word) > 3:
                word_counts[word] = word_counts.get(word, 0) + 1

        # Sort by frequency
        sorted_topics = sorted(
            word_counts.items(),
            key=lambda x: x[1],
            reverse=True)

        # Return top 5 topics
        return [topic for topic, count in sorted_topics[:5]]

    def generate_response_with_context(
            self,
            user_input,
            base_response,
            extended_context):
        """Generate a response that considers the extended context"""
        # Check if we have relevant memories
        if "Previous relevant memory:" in extended_context:
            # Extract only the first relevant memory for simplicity
            memory_parts = extended_context.split(
                "Previous relevant memory:", 1)
            if len(memory_parts) > 1:
                memory_parts[1].strip()

                # Add a reference to the memory in the response
                response_with_context = f"{base_response} (ฉันจำได้ว่าเราเคยคุยเกี่ยวกับเรื่องนี้ด้วย)"
                return response_with_context

        return base_response
