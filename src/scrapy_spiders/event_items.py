from datetime import datetime as dt 
from dataclasses import dataclass, field

def serialize_datetime(obj):
    if isinstance(obj, dt):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

@dataclass
class EventItem:
    title: str  = field()
    datetime: dt = field(metadata={"serializer": serialize_datetime})
    locations: list = field()
    url: str = field(default="https://www.e-werk.de/programm/alle-termine/")