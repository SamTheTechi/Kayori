from typing import Optional, Type
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field
from langchain_google_community.calendar.base import CalendarBaseTool


class DeleteEventSchema(BaseModel): # Schema for deleting a calendar event.

    event_id: str = Field(..., description="The event ID to delete.")
    calendar_id: Optional[str] = Field(
        default="primary", description="The origin calendar ID."
    )
    send_updates: Optional[str] = Field(
        default=None,
        description=(
            "Whether to send updates to attendees."
            "Allowed values are 'all', 'externalOnly', or 'none'."
        ),
    )


# type: ignore[override, override]
class CalendarDeleteEvent(CalendarBaseTool): # Tool for deleting calendar events.
    """Tool that delete an event in Google Calendar."""

    name: str = "delete_calendar_event"
    description: str = "Use this tool to delete an event.\
    Use CalendarSearchEvent tool to find event_id"
    args_schema: Type[DeleteEventSchema] = DeleteEventSchema

    def _run(self, event_id: str, calendar_id: Optional[str] = "primary", send_updates: Optional[str] = None, run_manager: Optional[CallbackManagerForToolRun] = None) -> str: # Deletes a calendar event.
        try:
            self.api_resource.events().delete(
                eventId=event_id, calendarId=calendar_id, sendUpdates=send_updates
            ).execute()
            return "Event deleted"
        except Exception as error:
            raise Exception(f"An error occurred: {error}") from error
