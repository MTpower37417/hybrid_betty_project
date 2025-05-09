# Betty AI GPT Trainer System

## Overview

The Betty AI GPT Trainer System is designed to train an AI assistant named Betty, enabling her to learn from GPT initially and then operate independently. This system follows a "teach to fish" approach rather than an "eat forever" approach to AI development.

## System Architecture

The system consists of several key components:

### 1. GPTController

Controls the usage of GPT throughout the system with three operating modes:
- `train`: Betty actively learns from GPT
- `assist`: GPT helps Betty when needed
- `off`: Betty operates independently using learned knowledge

### 2. EmotionAnalyzer

Analyzes emotions in user text:
- Uses GPT when available
- Falls back to keyword-based analysis when GPT is disabled
- Returns emotion type and intensity

### 3. ResponsePatternAnalyzer

Detects conversation patterns and suggests appropriate response styles:
- Identifies patterns like self-doubt, advice-seeking, anger, etc.
- Recommends response styles (encouraging, thoughtful, calming, etc.)
- Works with or without GPT

### 4. MemoryCapsuleManager

Creates memory capsules to store essential information:
- Extracts key insights from conversations
- Organizes information in structured capsules with topics, emotions, lessons
- Stores capsules for future training

### 5. BettyTrainer

Trains Betty using memory capsules:
- Extracts patterns and knowledge from capsules
- Builds a local knowledge base Betty can use independently
- Provides fallback responses when GPT is unavailable

### 6. BettyGPTTrainer

Main class that integrates all components:
- Coordinates the training process
- Manages switching between GPT and local knowledge
- Provides the main interface for interacting with Betty

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a configuration file `config.env` with your settings

## Usage

### Basic usage

```python
from gpt_trainer import BettyGPTTrainer

# Initialize Betty in training mode
trainer = BettyGPTTrainer(mode="train")

# Process a user interaction
result = trainer.process_interaction("I'm feeling really happy today!")

# Get Betty's response
print(result["response"])
```

### Command-line interface

```
# Start in training mode
python gpt_trainer.py --mode train --interactive

# Batch training on example data
python gpt_trainer.py --batch-train examples.json

# Run Betty in independent mode (no GPT)
python gpt_trainer.py --mode off --interactive
```

## Training Methodology

Betty learns through these stages:

1. **GPT Analysis**: GPT analyzes emotions, patterns, and generates responses
2. **Memory Capsule Creation**: Key information is extracted and stored
3. **Pattern Learning**: Betty learns response patterns from GPT
4. **Independent Operation**: Betty can eventually operate without GPT
5. **Continuous Learning**: New conversations improve Betty's knowledge

## Directory Structure

```
.
├── gpt_trainer.py        # Main implementation
├── requirements.txt      # Dependencies
├── config.env            # Configuration file
├── logs/                 # Log files
└── memory/               # Betty's memory storage
    ├── capsule/          # Memory capsules
    └── lessons/          # Learned patterns
```

## Configuration

Configure the system by editing `config.env`:

```
USE_GPT=True             # Enable or disable GPT
MODE=train               # Operating mode
LOG_LEVEL=INFO           # Logging verbosity
MEMORY_PATH=memory/      # Path to memory storage
```

## Notes

- This system is designed to gradually reduce dependency on GPT
- Betty's knowledge accumulates over time through conversations
- The system can operate in a fully offline mode once sufficient training has occurred