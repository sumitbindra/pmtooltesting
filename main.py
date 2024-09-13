# main.py
import os
import shutil
import json
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from document_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_tasks
)
from github_integration import create_github_issue
from scheduler import start_scheduler, suggestions, update_schedule, get_next_run_time

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Start the scheduler with default time 9:00 AM
start_scheduler(hour=9, minute=0)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, message: str = None):
    next_run = get_next_run_time()
    # Format the next run time for display
    if next_run:
        # Convert to local time if necessary
        next_run_formatted = next_run.strftime("%Y-%m-%d %H:%M:%S")
    else:
        next_run_formatted = "No scheduled job."

    return templates.TemplateResponse("index.html", {
        "request": request,
        "suggestions": suggestions,
        "message": message,
        "next_run_time": next_run_formatted
    })

@app.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    file_location = f"temp_files/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.endswith(".pdf"):
        text = await extract_text_from_pdf(file_location)
    elif file.filename.endswith(".docx"):
        text = await extract_text_from_docx(file_location)
    else:
        return {"error": "Unsupported file type"}

    tasks_json = await extract_tasks(text)
    try:
        tasks_data = json.loads(tasks_json)
    except json.JSONDecodeError:
        return RedirectResponse(
            url="/?message=Failed+to+parse+tasks+from+the+document.",
            status_code=303
        )

    tasks = tasks_data.get("tasks", [])
    for task in tasks:
        await create_github_issue(task, "Imported from project scope document.")

    # Redirect to home page with success message
    return RedirectResponse(
        url="/?message=Tasks+created+successfully",
        status_code=303
    )

@app.post("/update_schedule/")
async def update_schedule_endpoint(hour: int = Form(...), minute: int = Form(0)):
    update_schedule(hour, minute)
    return RedirectResponse(
        url=f"/?message=Cron+job+time+updated+to+{hour:02d}:{minute:02d}",
        status_code=303
    )
