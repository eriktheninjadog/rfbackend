from icalendar import Calendar
from datetime import datetime
import pytz
import os

#icsp.py


def parse_ics_file(filepath):
    """
    Parse an ICS calendar file and return the calendar events.
    
    Args:
        filepath (str): Path to the ICS file
        
    Returns:
        list: List of dictionaries containing event information
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"ICS file not found: {filepath}")
    
    events = []
    
    try:
        with open(filepath, 'rb') as file:
            cal = Calendar.from_ical(file.read())
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    event = {}
                    
                    # Get basic event details
                    event['summary'] = str(component.get('summary', 'No Title'))
                    event['description'] = str(component.get('description', ''))
                    event['location'] = str(component.get('location', ''))
                    
                    # Get start and end times
                    start = component.get('dtstart')
                    if start:
                        start_dt = start.dt
                        if isinstance(start_dt, datetime):
                            if start_dt.tzinfo is None:
                                start_dt = pytz.UTC.localize(start_dt)
                            event['start'] = start_dt
                        else:
                            event['start'] = start_dt
                    
                    end = component.get('dtend')
                    if end:
                        end_dt = end.dt
                        if isinstance(end_dt, datetime):
                            if end_dt.tzinfo is None:
                                end_dt = pytz.UTC.localize(end_dt)
                            event['end'] = end_dt
                        else:
                            event['end'] = end_dt
                    
                    # Get UID
                    event['uid'] = str(component.get('uid', ''))
                    
                    events.append(event)
        
        return events
    except Exception as e:
        raise ValueError(f"Error parsing ICS file: {str(e)}")
    
    
    
if __name__ == "__main__":  
    # Example usage
    filepath = '/home/erik/Downloads/Erik Tamm_erik.tamm@eriktamm.com.ics'  # Replace with your ICS file path
    try:
        events = parse_ics_file(filepath)
        for event in events:
            #print(f"Event: {event['summary']}")
            #print(f"Start: {event['start']}")
            #print(f"End: {event['end']}")
            #print(f"Location: {event['location']}")
            if len(event['summary']) < 30:
                print(f"{str(event['start'])[0:10]}, {event['summary']}")
            #print(f"Event: {event['summary']}")
            #if (len(event['description'])< 100):
            #    print(f"Description: {event['description']}")
            #print(f"UID: {event['uid']}")
            #print("-" * 40)
            
    except Exception as e:
        print(e)
    