#!/usr/bin/python3

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

scheduler = BackgroundScheduler()


def event_reached(event):
    """
    This function runs when the scheduled event time is reached.
    """

    print(f"Event reached: {event.title}")

    # Put whatever should happen here.
    # Example:
    # send_email(...)
    # socketio.emit(...)
    # send_sms(...)


def schedule_event(event):
    """
    Schedule an event to run at its start_time.
    """

    scheduler.add_job(
        event_reached,
        trigger="date",
        run_date=event.start_time,
        args=[event],
        id=f"event_{event.id}",
        replace_existing=True
    )


def start_scheduler():
    """
    Start the background scheduler.
    """

    if not scheduler.running:
        scheduler.start()
