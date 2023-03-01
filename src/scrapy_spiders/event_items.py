from datetime import datetime as dt, timedelta
from dataclasses import dataclass, field

def serialize_datetime(obj):
    if isinstance(obj, dt):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

def serialize_timedelta(obj):
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    raise TypeError("Type %s not serializable" % type(obj))

@dataclass
class EventItem:
    title: str  = field()
    datetime: dt = field(metadata={"serializer": serialize_datetime})
    locations: list = field()
    url: str = field(default="https://www.e-werk.de/programm/alle-termine/")
    duration: timedelta = field(metadata={"serializer": serialize_timedelta}, default=timedelta(hours=2))