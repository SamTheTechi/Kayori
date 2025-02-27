from langchain_google_community.calendar.base import CalendarBaseTool
from zoneinfo import ZoneInfo
from langchain_core.callbacks import CallbackManagerForToolRun
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field


class SearchEventsSchema(BaseModel):
    min_datetime: str = Field(
        ..., description="The start date and time for the event search in 'YYYY-MM-DD\
        HH:MM:SS' format. Defaults to the current_date_time if not specified."
    )
    max_datetime: str = Field(
        ..., description="The end datetime for the events search.Defaults to \
        7 days from the current date and time if not specified."
    )
    single_events: bool = Field(
        default=True,
        description="Whether to expand recurring events into instances and only return single events."
    )
    order_by: str = Field(
        default="startTime",
        description="The order of the events, either 'startTime' or 'updated'."
    )
    query: Optional[str] = Field(
        default=None,
        description="Free text search terms to find events in various fields\
        such as summary, description, location, and attendees."
    )


class CalendarSearchEvent(CalendarBaseTool):
    name: str = "search_events"
    description: str = "Use this tool to search events in the calendar,\
    use this calender as primary 'gsameer478@gmail.com' unless it's spicified "
    args_schema: Type[SearchEventsSchema] = SearchEventsSchema

    def _get_calendars_info(self) -> List[Dict[str, Any]]:
        try:
            calendar_list = self.api_resource.calendarList().list().execute()
            calendars = calendar_list.get("items", [])

            return [
                {"id": cal["id"], "summary": cal.get(
                    "summary"), "timeZone": cal.get("timeZone")}
                for cal in calendars
            ]
        except Exception as error:
            raise Exception(f"Failed to fetch calendar info: {
                            error}") from error

    def _get_calendar_timezone(
        self, calendars_info: List[Dict[str, str]], calendar_id: str
    ) -> Optional[str]:
        for cal in calendars_info:
            if cal["id"] == calendar_id:
                return cal.get("timeZone")
        return None

    def _get_calendar_ids(self, calendars_info: List[Dict[str, str]]) -> List[str]:
        return [cal["id"] for cal in calendars_info]

    def _process_data_events(
        self, events_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Optional[str]]]:
        simplified_data = []
        for data in events_data:
            event_dict = {
                "id": data.get("id"),
                "htmlLink": data.get("htmlLink"),
                "summary": data.get("summary"),
                "creator": data.get("creator", {}).get("email"),
                "organizer": data.get("organizer", {}).get("email"),
                "start": data.get("start", {}).get("dateTime")
                or data.get("start", {}).get("date"),
                "end": data.get("end", {}).get("dateTime")
                or data.get("end", {}).get("date"),
            }
            simplified_data.append(event_dict)
        return simplified_data

    def _run(
        self,
        min_datetime: str,
        max_datetime: str,
        order_by: str = "startTime",
        query: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[Dict[str, Optional[str]]]:
        try:
            calendars_data = self._get_calendars_info()
            calendars = self._get_calendar_ids(calendars_data)
            events = []
            for calendar in calendars:
                tz_name = self._get_calendar_timezone(calendars_data, calendar)
                calendar_tz = ZoneInfo(tz_name) if tz_name else None
                time_min = (
                    datetime.strptime(min_datetime, "%Y-%m-%d %H:%M:%S")
                    .astimezone(calendar_tz)
                    .isoformat()
                )
                time_max = (
                    datetime.strptime(max_datetime, "%Y-%m-%d %H:%M:%S")
                    .astimezone(calendar_tz)
                    .isoformat()
                )
                events_result = (
                    self.api_resource.events()
                    .list(
                        calendarId=calendar,
                        timeMin=time_min,
                        timeMax=time_max,
                        maxResults=10,
                        singleEvents=True,
                        orderBy=order_by,
                        q=query,
                    )
                    .execute()
                )
                cal_events = events_result.get("items", [])
                events.extend(cal_events)
            return self._process_data_events(events)
        except Exception as error:
            raise Exception(
                f"An error occurred while fetching events: {error}"
            ) from error
