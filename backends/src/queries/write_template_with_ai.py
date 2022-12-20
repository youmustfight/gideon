import sqlalchemy as sa
from dbs.sa_models import LegalBriefFact, Writing
from models.gpt import GTP3_COMPLETION_MODEL_ENGINE, gpt_completion


async def write_template_with_ai(session, writing_model):
    # FETCH
    # --- grab case facts
    query_legal_brief_facts = await session.execute(
        sa.select(LegalBriefFact).where(LegalBriefFact.case_id == writing_model.case_id))
    legal_brief_facts = query_legal_brief_facts.scalars().all()
    FACTS = "\n".join(map(lambda cf: cf.text, legal_brief_facts))
    # --- grab template text
    query_template = await session.execute(
        sa.select(Writing).where(Writing.id == writing_model.forked_writing_id))
    template = query_template.scalars().one()

    # COMPOSE
    # --- compose prompt text
    gpt_prompt_template_text_fill = """
    Edit the writing statement with facts filled in..
    
    FACTS:
    <<FACTS>>

    STATEMENT:
    <<STATEMENT>>

    STATEMENT WITH FACTS EDITED IN:
    """.replace("<<FACTS>>", FACTS).replace("<<STATEMENT>>", template.body_text)
    generated_body_text = gpt_completion(
      engine=GTP3_COMPLETION_MODEL_ENGINE,
      max_tokens=500,
      prompt=gpt_prompt_template_text_fill)
    print(gpt_prompt_template_text_fill)
    print(generated_body_text)
    # --- compose prompt html
    gpt_prompt_template_html_fill = """
    Edit the HTML with facts filled in. Preserve the html structure.
    
    FACTS:
    <<FACTS>>

    HTML:
    <<HTML>>

    HTML WITH FACTS EDITED IN:
    """.replace("<<FACTS>>", FACTS).replace("<<HTML>>", template.body_html)
    generated_body_html = gpt_completion(
      engine=GTP3_COMPLETION_MODEL_ENGINE,
      max_tokens=500,
      prompt=gpt_prompt_template_html_fill)

    # UPDATE VALUES
    writing_model.body_html = generated_body_html
    writing_model.body_text = generated_body_text
    writing_model.generated_body_html = generated_body_html
    writing_model.generated_body_text = generated_body_text

    # RETURN
    return writing_model
