from env import env_get_open_ai_api_key
from models.gpt import gpt_summarize

# ANSWER A QUESTION
def summarize_user(user):
    print('INFO (summarize_user.py): summarizing "{user}" notes'.format(user=user))
    # VECTOR SIMILARITY SCORING
    highlights = [] # get_highlights_json()
    def filter_user_highlight(highlight):
      return highlight['user'] == user
    user_highlights = list(filter(filter_user_highlight, highlights))

    # SUMMARIZE ANSWER
    print('INFO (summarize_user.py): summarizing from {num} highlight(s)...'.format(num=len(user_highlights)))
    summary = ''
    if len(user_highlights) > 0:
        notes = []
        # --- push notes together, with clear contrasts to the statements highlighted
        for idx, highlight in enumerate(user_highlights):
            notes.append(
              "{user} has the following opinion about this passage.\n\nOPINION: {note_text}\n\nPASSAGE: {highlight_text}".format(
                highlight_text=highlight['highlight_text'],
                note_text=highlight['note_text'],
                user=user
              )
            )
        # --- summarize notes
        print('INFO (summarize_user.py): summarizing notes\n\n', '\n\n'.join(notes))
        safe_notes = '\n\n'.join(notes).encode(encoding='ASCII',errors='ignore').decode()
        summary = gpt_summarize(safe_notes)
    else:
        summary = 'Found no highlights for user.'
    # RESPONSE
    print('INFO (summarize_user.py): answer = {summary}'.format(summary=summary))
    return summary

# RUN
if __name__ == '__main__':
    user = input("Enter user: ")
    summarize_user(user)