# Sentiment Analysis and Bug Tracking Features

## Overview

The UX Agent now includes advanced sentiment analysis and bug tracking capabilities to better understand user experience and identify issues during website interaction.

## Features

### 1. Bug Detection
- Automatically detects various types of bugs during agent execution
- Bug types include:
  - `UI_ERROR`: UI element issues
  - `LOADING_ERROR`: Page loading problems
  - `INTERACTION_FAILURE`: Failed interactions with elements
  - `VALIDATION_ERROR`: Form validation failures
  - `NAVIGATION_ERROR`: Navigation issues (404s, etc.)
  - `UNKNOWN`: Other unclassified errors

### 2. Sentiment Analysis
- Tracks user sentiment throughout the interaction
- Sentiment levels:
  - `VERY_POSITIVE`: Highly engaged with relevant content
  - `POSITIVE`: Smooth progress
  - `NEUTRAL`: Normal exploration
  - `NEGATIVE`: Experiencing difficulties
  - `FRUSTRATED`: Multiple errors or confusion

### 3. Dynamic Thoughts
- Agent thoughts adapt based on:
  - Current sentiment level
  - Bug encounters
  - Page context
  - User persona

### 4. Drop-off Detection
- Detects when users would likely abandon the site
- Reasons include:
  - Lost interest due to irrelevant content
  - Frustration from poor UX
  - Lack of meaningful progress

## Usage

The features are automatically integrated into the agent. When running the agent, you'll see:

```python
result = await agent.run(input_data)

# Access sentiment and bug data
print(f"Overall sentiment: {result.overall_sentiment}")
print(f"Bugs encountered: {result.bugs_encountered}")
print(f"Dropoff reason: {result.dropoff_reason}")

# Per-interaction data
for interaction in result.interactions:
    print(f"Sentiment: {interaction.sentiment}")
    if interaction.bug_detected:
        print(f"Bug: {interaction.bug_type} - {interaction.bug_description}")
```

## Testing

Run the test script to see the features in action:

```bash
python test_sentiment_bugs.py
```

This will run three test cases demonstrating:
1. Bug detection on a buggy website
2. Positive sentiment on a working site
3. User drop-off due to content mismatch