#!/usr/bin/python3

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

scheduler = BackgroundScheduler()


def event_reached(event):
    """
    This function runs when the scheduled event time is reached.
    """

    if event.tittle==Terminate:
        result=db.query.session(GiftRegistration).filter(gift_id==event.gift_id).first()
        result.status="Terminated"
        db.commit()
    else:
        html=render_template("emails/special_day.html")
        send_email(event.sender_email,"Day Notification",html)

def schedule_event(event):
    """
    Schedule an event to run at its start_time.
    """

    scheduler.add_job(
        event_reached,
        trigger="date",
        run_date=event.delivery_date,
        args=[event],
        id=f"event_{event.gift_id}",
        replace_existing=True
    )
    print("Event logged in")


def start_scheduler():
    """
    Start the background scheduler.
    """

    if not scheduler.running:
        scheduler.start()
