from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random
from scheduling.weather import weather
from scheduling.locations import location_change
from scheduling.nature import change_pfp, mood_drift, mood_spike
from scheduling.greetings import good_evening, good_morning


def setup_scheduler(client, private_executer,  vector_store, USER_ID):
    scheduler = AsyncIOScheduler()
    config = {"configurable": {"thread_id": str(USER_ID)}}

    # Periodic jobs
    scheduler.add_job(change_pfp, "interval", hours=random.randint(17, 20), args=[client])
    scheduler.add_job(mood_drift, "interval", minutes=random.randint(4, 7))
    scheduler.add_job(mood_spike, "interval", minutes=random.randint(50, 60))

    # Scheduled greetings
    scheduler.add_job(good_morning, "cron", hour=random.randint(7, 9), args=[client, private_executer, config])
    scheduler.add_job(good_evening, "cron", hour=random.randint(17, 19), args=[client, private_executer, config])

    # Weather/location updates
    scheduler.add_job(weather, "interval", hours=random.randint(14, 16), args=[client, private_executer, config])
    scheduler.add_job(location_change, "interval", minutes=30, args=[client, private_executer, config, vector_store])

    scheduler.start()
