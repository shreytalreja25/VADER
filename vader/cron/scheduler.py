import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from croniter import croniter

CRON_FILE = Path.home() / ".vader" / "cron_jobs.json"

class CronJob:
    def __init__(self, id: str, schedule: str, task_type: str, payload: str, enabled: bool = True, last_run: Optional[str] = None):
        self.id = id
        self.schedule = schedule
        self.task_type = task_type # 'prompt', 'workflow', 'command'
        self.payload = payload
        self.enabled = enabled
        self.last_run = last_run

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "schedule": self.schedule,
            "task_type": self.task_type,
            "payload": self.payload,
            "enabled": self.enabled,
            "last_run": self.last_run
        }

class CronScheduler:
    """
    Schedules and executes periodic automated Vader tasks (audits, syncs, self-healing).
    """
    def __init__(self):
        CRON_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.jobs = self.load_jobs()

    def load_jobs(self) -> List[CronJob]:
        if not CRON_FILE.exists():
            return []
        try:
            with open(CRON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [CronJob(**j) for j in data]
        except Exception:
            return []

    def save_jobs(self):
        with open(CRON_FILE, "w", encoding="utf-8") as f:
            json.dump([j.to_dict() for j in self.jobs], f, indent=2)

    def add_job(self, job_id: str, schedule: str, task_type: str, payload: str) -> CronJob:
        if not croniter.is_valid(schedule):
            raise ValueError(f"Invalid cron expression: {schedule}")
        job = CronJob(id=job_id, schedule=schedule, task_type=task_type, payload=payload)
        self.jobs = [j for j in self.jobs if j.id != job_id]
        self.jobs.append(job)
        self.save_jobs()
        return job

    def remove_job(self, job_id: str) -> bool:
        before = len(self.jobs)
        self.jobs = [j for j in self.jobs if j.id != job_id]
        self.save_jobs()
        return len(self.jobs) < before

    def list_jobs(self) -> List[CronJob]:
        return self.jobs

cron_scheduler = CronScheduler()
