# Telegram Bots: Joke Generator and Question Generator

This repository contains two Telegram bots deployed on Hugging Face Spaces:

- **Joke Generator Bot**: A simple bot that delivers random jokes to entertain users.
- **Question Generator Bot**: An advanced bot that generates customized quiz questions based on user-specified subjects, topics, and preferences, with weighted question formats and logging.

Last one is accessible at: [telegram](t.me/QuestionGenAIbot)

## Overview

The **Joke Generator Bot** is a lightweight Telegram bot designed to provide quick laughs with random jokes. The **Question Generator Bot** is an educational tool that creates tailored quiz questions for subjects like Computer Science, Math, or Physics, using prompt engineering with the Mistral AI model. It supports customizable parameters (e.g., language, difficulty, question types) and logs user interactions for analytics.


### Joke Generator Bot

- Generates random jokes on demand.
- created using golang.

### Question Generator Bot

- **Custom Question Generation**:
  - Generates 1-20 questions based on user inputs: subject, topic, language, number of questions, comment, and weights for question types.
  - Supports four question categories: Problem-Solving, Analytical Reasoning, Conceptual Understanding, and Factual Recall.
  - Weights (0-10) control the distribution of question formats
- **Prompt Engineering**:
  - Uses `langchain-core` and `langchain-mistralai` with Mistral AI’s `mistral-large-latest` model for intelligent question generation.
  - Dynamic prompt templates ensure relevant and engaging questions.
- **Supported Languages**:
  - Questions can be generated in languages like English, Spanish, or Python (for code examples).

## Deployment:
- Question generator bot was deployed to huggingface space