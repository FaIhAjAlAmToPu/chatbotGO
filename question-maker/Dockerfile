FROM python:3.12-alpine

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "app.py"]