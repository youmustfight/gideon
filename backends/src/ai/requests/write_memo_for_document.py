from datetime import date
import sqlalchemy as sa
from ai.requests.question_answer import question_answer
from dbs.sa_models import Brief, Document, Writing
from models.gpt import gpt_completion, gpt_edit
from models.gpt_prompts import gpt_prompt_article_title, gpt_prompt_edit_separate_research_questions_list


async def write_memo_for_document(session, document_id: int, prompt_text: str, user_id: int):
    print('INFO (write_memo_for_document.py) start')
    # CONTENT
    # --- prompts
    # Separate out research questions from prompt
    research_prompt_edited = gpt_edit(
        gpt_prompt_edit_separate_research_questions_list,
        prompt_text)
    print('INFO (write_memo_for_document.py) research_prompt_edited', research_prompt_edited)
    research_prompt_arr = research_prompt_edited.strip().split("-")
    # --- remove empty strings
    research_prompt_arr = list(filter(lambda str: str != '', research_prompt_arr))
    # --- clean start/end line breaks or gaps
    research_prompt_arr = list(map(lambda str: str.strip(), research_prompt_arr))
    print('INFO (write_memo_for_document.py) research_prompt_arr', research_prompt_arr)
    # Run Q&A with each question against document
    research_prompt_responses = []
    for research_prompt in research_prompt_arr:
        answer, locations = await question_answer(
            session,
            query_text=research_prompt,
            document_id=document_id,
            user_id=user_id)
        research_prompt_responses.append(dict(
            research_prompt=research_prompt,
            answer=answer,
            locations=locations,
        ))
    print('INFO (write_memo_for_document.py) research_prompt_responses', research_prompt_responses)
    
    # GENERATED
    # writing_name = f'Memo for {document.name}'
    writing_title = gpt_completion(prompt=gpt_prompt_article_title.replace('<<SOURCE_TEXT>>', prompt_text), max_tokens=150)
    writing_byline = f'Drafted by AI on {date.today()}'
    
    # TEXT
    def write_research_memo_response_to_text(research_response):
        sources_text = '\n-'.join(map(lambda loc: f"{loc.get('document').name} ({loc.get('document_content').sentence_start}-{loc.get('document_content').sentence_end})", research_response.get('locations')))
        return f"{research_response.get('research_prompt')}:\n{research_response.get('answer')}\nSources:{sources_text}"
    research_prompts_text = "\n\n".join(map(write_research_memo_response_to_text, research_prompt_responses))
    print('INFO (write_memo_for_document.py) research_prompts_text', research_prompts_text)
    research_memo_text = f'{writing_title}\n{writing_byline}\n\n{research_prompts_text}'
    print('INFO (write_memo_for_document.py) research_memo_text', research_memo_text)

    # HTML
    def write_research_memo_response_to_html(research_response):
        sources_html = '</li><li>'.join(map(lambda loc: f"{loc.get('document').name} ({loc.get('document_content').sentence_start}-{loc.get('document_content').sentence_end})", research_response.get('locations')))
        return f"<h2>{research_response.get('research_prompt')}</h2><p>{research_response.get('answer')}</p><p>Sources:</p><ul><li>{sources_html}</li></ul>"
    research_prompts_html = "<br><br><br>".join(map(write_research_memo_response_to_html, research_prompt_responses))
    print('INFO (write_memo_for_document.py) research_prompts_html', research_prompts_html)
    research_memo_html = f'<h1>{writing_title}</h1><p>{writing_byline}</p><br><br>{research_prompts_html}'
    print('INFO (write_memo_for_document.py) research_memo_html', research_memo_html)

    # BUILD MODEL
    writing_model = Writing(
        document_id=document_id,
        user_id=user_id,
        type="memo_document",
        name=writing_title,
        generated_body_text=research_memo_text,
        body_text=research_memo_text, # this is what the user will edit
        generated_body_html=research_memo_html,
        body_html=research_memo_html, # this is what the user will edit
        is_template=False,
    )

    # return html so frontend can render w/ lexical
    return writing_model
