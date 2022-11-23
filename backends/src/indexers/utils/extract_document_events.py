import textwrap
from env import env_get_open_ai_api_key
from files.file_utils import get_file_path, open_txt_file
from models.gpt import gpt_completion, gpt_edit, gpt_vars

# EXTRACT TIMELINE
async def extract_document_events(document_text):
    print(f'INFO (extract_document_events): getting event timeline for..."', document_text)

    completion_event_responses = []
    # build timelines for each chunk of text (expecting)
    chunks = textwrap.wrap(document_text, 11000)
    for chunk in chunks:
        # --- set up prompt
        prompt = open_txt_file(get_file_path('./prompts/prompt_timeline.txt')).replace('<<SOURCE_TEXT>>', chunk)
        # --- extract timeline
        print('INFO (extract_document_events.py): prompt\n\n', prompt)
        timeline_completion = gpt_completion(
            prompt, max_tokens=500, engine=gpt_vars()['ENGINE_COMPLETION'])
        # --- delelte lines without dates
        timeline_completion_with_dates = gpt_edit(
            open_txt_file(get_file_path('./prompts/edit_event_timeline.txt')),
            timeline_completion)
        # --- reformat specifically for ISO strings
        timeline_completion_with_dates_as_iso = gpt_edit(
            open_txt_file(get_file_path('./prompts/edit_event_timeline_structure.txt')),
            timeline_completion_with_dates)
        # --- append
        completion_event_responses.append(timeline_completion_with_dates_as_iso)

    events = []
    # format events: split each into a date, description, documents involved
    for completion_event in completion_event_responses:
        for line in completion_event.split('\n'):
            if line != '' and line is not None:
                events.append(line)
    print(f'INFO (extract_document_events): events\n', events)

    # create structured data of events
    events_objects = []
    for event in events:
        if ':' in event:
            colon_index = int(event.index(':'))
            date = event[slice(colon_index - 10, colon_index)], # in case there's a bullet, just move back from colon
            event = event[slice(colon_index + 1, -1)]
            print('date', date)
            print('event', event)
            if (date != None and event != None and len(event.strip()) > 0):
                events_objects.append({ 'date': date, 'event': event.strip() })
    print(f'INFO (extract_document_events): events_objects\n', events_objects)

    # TODO: order into chronological order

    # return!
    return events_objects
