import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize the model
model = init_chat_model("mistral-large-latest", model_provider="mistralai")

# Refined system and user prompts
system_template = """You are a question generator bot that creates {num_questions} quiz questions for the user-specified subject, topic and language. Use the comment to adjust question style, difficulty, or specific requirements if provided (e.g., 'beginner level', 'multiple-choice only'). Generate questions based on these weighted preferences (0=lowest, 10=highest):
- Problem-Solving ({problem_solving_w}/10): Apply concepts to solve problems (e.g., coding challenges like 'Write a Python function to reverse a string' or math problems like 'Solve 2x + 3 = 7').
- Analytical Reasoning ({analytical_reasoning_w}/10): Analyze scenarios, identify patterns, or make logical deductions (e.g., 'What is the time complexity of this algorithm?' or 'Predict the outcome of this experiment').
- Conceptual Understanding ({conceptual_understanding_w}/10): Test comprehension of core concepts via explanation or interpretation (e.g., 'Explain how a hash table works' or 'Why does this chemical reaction occur?').
- Factual Recall ({factual_recall_w}/10): Specific facts or definitions, used minimally (e.g., 'Define a binary tree' or 'What is the capital of France?').

Guidelines:
1. Generate exactly {num_questions} questions in the user specified language, distributed proportionally based on weights (e.g., for weights {problem_solving_w}:{analytical_reasoning_w}:{conceptual_understanding_w}:{factual_recall_w}, allocate ~{problem_solving_w}/{sum} Problem-Solving, ~{analytical_reasoning_w}/{sum} Analytical Reasoning, ~{conceptual_understanding_w}/{sum} Conceptual Understanding, ~{factual_recall_w}/{sum} Factual Recall, where sum is the total weight).
2. . Questions must match the subject and topic, targeting intermediate difficulty unless specified in the comment.
3. Each question includes a clear question and concise answer in the specified language (<100 words).
4. Format output as:
   Q1: <question>
   A1: <answer>
   ...
5. If the subject or topic is vague or invalid, return: 'Please provide a specific subject and topic (e.g., "Computer Science, Algorithms").'
6. Ensure questions are engaging, concise, and promote learning or practical application."""

user_prompt = """Subject: {subject}
Topic: {topic}
language: {language}
Comment: {comment}"""

# Create prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("user", user_prompt)
])

# Default weights
weights = {
    'problem_solving_w': 10,
    'analytical_reasoning_w': 8,
    'conceptual_understanding_w': 9,
    'factual_recall_w': 1
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Use /generate <subject>, <topic>\n\n"
        "Or use /generate <subject>, <topic>, <language>\n\n"
        "Or use /generate <subject>, <topic>, <language>, <number of questions>\n\n"
        "Or use /generate <subject>, <topic>, <language>, <number of questions>, <comment>\n\n"
        "To create questions with default weights \n(e.g., /generate Computer Science, Algorithms, 5, beginner level) and language (default English). Comment and number of question (default=5) is optional.\n\n\n"
        "Or use /generate <subject>, <topic>, <language>, <number of questions>, <comment>, <Problem-Solving-weight out of 10>,<Analytical Reasoning-weight out of 10>,<Conceptual Understanding-weight out of 10>,<Factual Recall-weight out of 10> to create questions with weighted preferences (0=lowest, 10=highest) \n(e.g., /generate Computer Science, Algorithms, 5, beginner level, 10,8,9,1).\n\n\n"
  )
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(
        f"UserID: {update.effective_user.id}, Username: {update.effective_user.username or 'None'}, "
        f"ChatID: {update.effective_chat.id}, Message: {update.message.text or 'None'}"
    )
    input_text = update.message.text.replace('/generate', '').strip()
    parts = input_text.split(',')
    if len(parts) not in [2,3,4,5,9]:
        await update.message.reply_text("Please provide a subject and topic (e.g., /generate Computer Science, Algorithms).")
        return

    subject = parts[0].strip()
    topic = parts[1].strip()
    language = 'English'
    num_questions = 5
    comment = ''
    problem_solving_w = weights['problem_solving_w']
    analytical_reasoning_w = weights['analytical_reasoning_w']
    conceptual_understanding_w = weights['conceptual_understanding_w']
    factual_recall_w = weights['factual_recall_w']
    weight_sum = problem_solving_w + analytical_reasoning_w + conceptual_understanding_w + factual_recall_w

    if len(parts) > 2:
        language = parts[2].strip()
        if len(parts) > 3:
            try:
                num_questions = int(parts[3].strip())
            except (IndexError, ValueError):
                num_questions = 5
            if len(parts) > 4:
                comment = parts[4]
                if len(parts) > 5:
                    try:
                        problem_solving_w = int(parts[5].strip())
                        analytical_reasoning_w = int(parts[6].strip())
                        conceptual_understanding_w = int(parts[7].strip())
                        factual_recall_w = int(parts[8].strip())
                        weight_sum = problem_solving_w + analytical_reasoning_w + conceptual_understanding_w + factual_recall_w
                    except:
                        await update.message.reply_text("Please provide valid weights (e.g., /generate Computer Science, Algorithms, 5, beginner level, 10,8,9,1).")
                        return
            else:
                comment = ''
        else:
            num_questions = 5
            comment = ''


    prompt = prompt_template.invoke({
        'num_questions': num_questions,
        'subject': subject,
        'topic': topic,
        'comment': comment,
        'problem_solving_w': problem_solving_w,
        'analytical_reasoning_w': analytical_reasoning_w,
        'conceptual_understanding_w': conceptual_understanding_w,
        'factual_recall_w': factual_recall_w,
        'sum': weight_sum,
        'language': language,
    })

    try:
        await update.message.reply_text(f"Generating {num_questions} questions for {subject} and {topic}...")
        response = await model.ainvoke(prompt)
        await update.message.reply_text(f"Generated {num_questions} questions for {subject} and {topic}...")
        await update.message.reply_text(response.content, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error invoking model: {e}")
        await update.message.reply_text("Sorry, I couldn't generate questions. Try again later!")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    # Initialize the bot
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("generate", generate))
    application.add_error_handler(error)

    # Start polling
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()