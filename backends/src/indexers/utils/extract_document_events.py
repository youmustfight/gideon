import textwrap
from models.gpt import gpt_completion, gpt_edit, gpt_vars
from models.gpt_prompts import gpt_prompt_timeline, gpt_prompt_edit_event_timeline, gpt_prompt_edit_event_timeline_structure
from models.ner import ner_parse

# EXTRACT TIMELINE
async def extract_document_events_v1(document_text):
    print(f'INFO (extract_document_events): getting event timeline for..."', document_text)

    completion_event_responses = []
    # build timelines for each chunk of text (expecting)
    chunks = textwrap.wrap(document_text, 11000)
    for chunk in chunks:
        # # --- check if any dates are mentioned at all (dates are found all over, this only slows things down as an extra step)
        # date_entities = ner_parse(document_text, ['DATE'])
        # if (len(date_entities) == 0): continue
        # --- extract timeline
        prompt = gpt_prompt_timeline.replace('<<SOURCE_TEXT>>', chunk)
        timeline_completion = gpt_completion(
            prompt, max_tokens=500, engine=gpt_vars()['ENGINE_COMPLETION'])
        # TODO: v2 extraction with ner
        # --- delelte lines without dates
        timeline_completion_with_dates = gpt_edit(
            gpt_prompt_edit_event_timeline,
            timeline_completion)
        # --- reformat specifically for ISO strings
        timeline_completion_with_dates_as_iso = gpt_edit(
            gpt_prompt_edit_event_timeline_structure,
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
