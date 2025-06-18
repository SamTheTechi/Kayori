import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from uuid import uuid4
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_google_community.calendar.base import CalendarBaseTool
from langchain_google_community.calendar.utils import is_all_day_event


class CreateEventSchema(BaseModel):
    """Input for CalendarCreateEvent."""

    summary: str = Field(..., description="The title of the event.")
    start_datetime: str = Field(
        ...,
        description=(
            "The start datetime for the event in 'YYYY-MM-DD HH:MM:SS' format."
            "If the event is an all-day event, set the time to 'YYYY-MM-DD' format."
            "Use 'current_date_time' if unknown."
        ),
    )
    end_datetime: str = Field(
        ...,
        description=(
            "The end datetime for the event in 'YYYY-MM-DD HH:MM:SS' format. "
            "If the event is an all-day event, set the time to 'YYYY-MM-DD' format."
            "Use 'current_date_time' if unknown."
            "Defaults to 7 days from the current date and time if not specified."
        ),
    )
    timezone: Optional[str] = Field(
        default="Asia/Kolkata", description="Event timezone. Defaults to 'Asia/Kolkata'."
    )
    calendar_id: str = Field(
        default="primary", description="ID of the calendar where the event will be created."
    )
    recurrence: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "The recurrence of the event. "
            "Format: {'FREQ': <'DAILY' or 'WEEKLY'>, 'INTERVAL': <number>, "
            "'COUNT': <number or None>, 'UNTIL': <'YYYYMMDD' or None>, "
            "'BYDAY': <'MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU' or None>}. "
            "Use either COUNT or UNTIL, but not both; set the other to None."
        ),
    )
    location: Optional[str] = Field(
        default=None, description="The location of the event."
    )
    description: Optional[str] = Field(
        default=None, description="The description of the event."
    )
    attendees: Optional[List[str]] = Field(
        default=None, description="A list of attendees' email addresses for the event."
    )
    conference_data: Optional[bool] = Field(
        default=None, description="Whether to include conference data."
    )
    color_id: Optional[str] = Field(
        default=None,
        description=(
            "Event color ID (None for default). Choices: "
            "'1': Lavender, '2': Sage, '3': Grape, '4': Flamingo, '5': Banana, "
            "'6': Tangerine, '7': Peacock, '8': Graphite, '9': Blueberry, "
            "'10': Basil, '11': Tomato."
        )
    )
    transparency: Optional[str] = Field(
        default=None, description="'transparent' (available) or 'opaque' (busy)."
    )


class CalendarCreateEvent(CalendarBaseTool):

    name: str = "create_calendar_event"
    description: str = (
        "Use this tool to create an event. "
        "The input must include the summary, timezone ,start,\
        and end datetime for the event."
    )
    args_schema: Type[CreateEventSchema] = CreateEventSchema

    def _prepare_event(
        self,
        summary: str,
        start_datetime: str,
        end_datetime: str,
        timezone: Optional[str] = "Asia/Kolkata",
        recurrence: Optional[Dict[str, Any]] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        conference_data: Optional[bool] = None,
        color_id: Optional[str] = None,
        transparency: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            if is_all_day_event(start_datetime, end_datetime):
                start = {"date": start_datetime}
                end = {"date": end_datetime}
            else:
                datetime_format = "%Y-%m-%d %H:%M:%S"
                start_dt = datetime.strptime(start_datetime, datetime_format)
                end_dt = datetime.strptime(end_datetime, datetime_format)
                start = {
                    "dateTime": start_dt.astimezone().isoformat(),
                    "timeZone": timezone or "Asia/Kolkate",
                }
                end = {
                    "dateTime": end_dt.astimezone().isoformat(),
                    "timeZone": timezone or "Asia/Kolkate",
                }
        except ValueError as error:
            raise ValueError("The datetime format is incorrect.") from error
        recurrence_data = None
        if recurrence:
            if isinstance(recurrence, dict):
                recurrence_items = [
                    f"{k}={v}" for k, v in recurrence.items() if v is not None
                ]
                recurrence_data = "RRULE:" + ";".join(recurrence_items)
        attendees_emails: List[Dict[str, str]] = []
        if attendees:
            email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
            for email in attendees:
                if not re.match(email_pattern, email):
                    raise ValueError(f"Invalid email address: {email}")
                attendees_emails.append({"email": email})
        conference_data_info = None
        if conference_data:
            conference_data_info = {
                "createRequest": {
                    "requestId": str(uuid4()),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }
        event_body: Dict[str, Any] = {
            "summary": summary, "start": start, "end": end}
        if location:
            event_body["location"] = location
        if description:
            event_body["description"] = description
        if recurrence_data:
            event_body["recurrence"] = [recurrence_data]
        if len(attendees_emails) > 0:
            event_body["attendees"] = attendees_emails
        if conference_data_info:
            event_body["conferenceData"] = conference_data_info
        if color_id:
            event_body["colorId"] = color_id
        if transparency:
            event_body["transparency"] = transparency
        return event_body

    def _run(
        self,
        summary: str,
        start_datetime: str,
        end_datetime: str,
        timezone: Optional[str],
        calendar_id: str = "primary",
        recurrence: Optional[Dict[str, Any]] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        conference_data: Optional[bool] = None,
        color_id: Optional[str] = None,
        transparency: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            body = self._prepare_event(
                summary=summary,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                timezone=timezone,
                recurrence=recurrence,
                location=location,
                description=description,
                attendees=attendees,
                conference_data=conference_data,
                color_id=color_id,
                transparency=transparency,
            )
            conference_version = 1 if conference_data else 0
            event = (
                self.api_resource.events()
                .insert(
                    calendarId=calendar_id,
                    body=body,
                    conferenceDataVersion=conference_version,
                )
                .execute()
            )
            return f"Event created: {event.get('htmlLink')}"
        except Exception as error:
            raise Exception(f"An error occurred: {error}") from error
