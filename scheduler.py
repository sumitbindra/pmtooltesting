# scheduler.py
import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from openai import AsyncOpenAI
from github_integration import get_open_issues
from pytz import utc, timezone

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

suggestions = []  # Global variable to store suggestions
scheduler = AsyncIOScheduler()
job = None  # Reference to the scheduled job

# Store the next run time
next_run_time = None

async def generate_suggestions():
    global next_run_time
    today = datetime.now()
    if today.weekday() >= 5:  # Skip weekends
        return

    issues = await get_open_issues()
    tasks = [issue['title'] for issue in issues]
    tasks_text = "\n".join(tasks)

    prompt = f"""
    Given the following list of tasks:

    {tasks_text}

    What are the immediate concerns and what should be considered in the near future? Provide suggestions and questions to think about.
    """
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7
    )
    content = response.choices[0].message.content
    suggestions.append({
        "date": today.strftime("%Y-%m-%d %H:%M"),
        "content": content
    })
    # Update the next run time after the job has executed
    job = scheduler.get_job('suggestion_job')
    if job:
        next_run_time = job.next_run_time

def start_scheduler(hour=9, minute=0):
    global job, next_run_time
    scheduler.start()  # Start the scheduler first
    job = scheduler.add_job(
        generate_suggestions,
        'cron',
        id='suggestion_job',
        hour=hour,
        minute=minute,
        replace_existing=True,
        next_run_time=datetime.now()  # Schedule the job to run at the next possible time
    )
    next_run_time = job.next_run_time

def update_schedule(hour, minute):
    global job, next_run_time
    job.reschedule(trigger='cron', hour=hour, minute=minute)
    next_run_time = job.next_run_time

def get_next_run_time():
    return next_run_time
