from core.discord_bot import client
from datetime import datetime, timedelta
from langchain_core.tools import BaseTool
from core.scheduler import scheduler


# A tool for agent herself
class ReminderTool(BaseTool):
    def __init__(self, **data):
        super().__init__(**data)

    userId: str
    name: str = "reminder_tool"
    description: str = (
        "Tool for Kayori to perform self-actions like sending reminders. "
        "Schedules a one-time reminder that sends a message to the user after a delay. "
        "The 'time' argument should be specified in minutes. "
        "The 'content' should be written as if the reminder has already been delivered or the task has been completed."
        "The 'userId' argument MUST be the Discord User ID (snowflake) of the recipient. "
    )

    def _run(self, content, time):
        try:
            run_at = datetime.now() + timedelta(minutes=int(time))

            async def schedule_task():
                try:
                    user = await client.fetch_user(self.userId)
                    if user:
                        await user.send(content)

                except Exception as e:
                    print(f"Error sending reminder: {e}")

            scheduler.add_job(
                schedule_task,
                trigger="date",
                run_date=run_at,
                misfire_grace_time=2*60,
            )

            return "task scheduled!"
        except Exception as e:
            return f"can't schedule error occurs {e}"
