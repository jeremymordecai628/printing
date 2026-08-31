#!/usr/bin/python3

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

scheduler = BackgroundScheduler()


def event_reached(event):
    """
    This function runs when the scheduled event time is reached.
    """

    if event.tittle==Delivery:
        result=db.query.session(GiftRegistration.recipient_email).filter(account==event.account).first()
        html=render_template("emails/special_day.html")
        send_email(result,"Day Notification",html)
    else:
         result=db.query.session(GiftRegistration).filter(account==event.account).first()
         result.status="Terminated"
         db.commit()


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
