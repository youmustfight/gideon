import cv2
import math
import numpy as np
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from time import sleep

from aia.agent import create_ai_action_agent, AI_ACTIONS
from dbs.sa_models import Document, DocumentContent, Embedding, File
from dbs.vector_utils import tokenize_string
from files.opencv_utils import video_frames
from files.s3_utils import s3_get_file_url, s3_upload_file_string
from indexers.utils.extract_document_events import extract_document_events_v1
from indexers.utils.extract_document_summary import extract_document_summary
from models.assemblyai import assemblyai_transcribe
from models.clip import clip_image_embedding
from models.gpt import gpt_embedding, gpt_vars, gpt_completion
from models.gpt_prompts import gpt_prompt_video_type

async def _index_video_process_content(session, document_id: int) -> None:
    print("INFO (index_pdf.py:_index_audio_process_content) started", document_id)
    # PROCESS FILE + PROPERTIES
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    files_query = await session.execute(sa.select(File).where(File.document_id == document_id))
    files = files_query.scalars()
    file = files.first()

    # TEXT
    # --- process file for transcript
    transcript_response = assemblyai_transcribe(file.upload_url)
    # DOCUMENT CONTENT CREATION
    # --- chunk audio text: document
    document_text = transcript_response['text']
    document_text_chunks = tokenize_string(document_text, "max_size")
    document_content_text = list(map(lambda chunk: DocumentContent(
        document_id=document_id,
        text=chunk,
        tokenizing_strategy="max_size"
    ), document_text_chunks))
    session.add_all(document_content_text)
    # --- chunk audio text: by sentence (w/ start/end times)
    sentences = transcript_response['sentences']
    document_content_sentences = list(map(lambda sentence: DocumentContent(
        document_id=document_id,
        text=sentence['text'],
        tokenizing_strategy="sentence",
        start_second=sentence['start_second'],
        end_second=sentence['end_second'],
    ), sentences))
    session.add_all(document_content_sentences)

    # IMAGE
    # https://www.storminthecastle.com/posts/video_search/
    # https://www.youtube.com/watch?v=7IL7LKSLb9I&t=159s
    # https://stackoverflow.com/questions/68249421/how-to-modify-patches-made-by-patchify
    # https://stackoverflow.com/questions/55583861/upload-image-from-opencv-to-s3-bucket
    freq=15.0
    last_index = 0
    patch_size = 720 // 2 # TODO: probably should adjust patch size based on video dimensions, so we reduce num of patches we make
    patch_shape = (patch_size, patch_size, 3)
    patch_step = patch_size // 2 # // means disregard the remainder after dividing
    path = s3_get_file_url(file.upload_key)
    # --- get frames
    for frame, timestamp in video_frames(path):
        if timestamp - last_index > freq:
            last_index = timestamp
            start_second = math.floor(last_index)
            # FRAME
            # --- frame before patching vectors
            frame_file_name = f'{document.id}' + '_' + 'image' + '_' + str(start_second).zfill(12) + '.png'
            frame_file_key = 'images/' + frame_file_name
            frame_file_string = cv2.imencode('.png', frame)[1].tostring()
            # --- upload frame
            s3_upload_file_string(frame_file_key, frame_file_string)
            # --- save
            session.add(
                DocumentContent(
                    document_id=document_id,
                    image_file=File(
                        document_id=document_id,
                        filename=frame_file_name,
                        mime_type='image/png',
                        upload_key=frame_file_key,
                        upload_url=s3_get_file_url(frame_file_key),
                    ),
                    start_second=start_second,
                )
            )
            # PATCHIFY # TODO: re-enable this when/if we need to parallelize. takes too long
            # patches = patchify(frame, patch_shape, patch_step) # don't squeeze, we want the matrix structure as is for saving files
            # for i in range(patches.shape[0]):
            #     for j in range(patches.shape[1]):
            #         # for each patch...
            #         single_patch_img = patches[i, j, 0, :, :, :]
            #         single_patch_string = cv2.imencode('.png', single_patch_img)[1].tostring() # Save as PNG, not JPEG for keeping the quality.
            #         patch_file_name = f'{document.id}' + '_' + 'image_patch' + '_' + str(start_second).zfill(12) + '_'+ str(i).zfill(2) + '_' + str(j).zfill(2) + '.png'
            #         patch_file_key = 'patches/' + patch_file_name
            #         # --- upload the patch
            #         s3_upload_file_string(patch_file_key, single_patch_string)
            #         # --- create a file + document record
            #         session.add(
            #             DocumentContent(
            #                 document_id=document_id,
            #                 patch_size=patch_size,
            #                 image_file=File(
            #                     document_id=document_id,
            #                     filename=patch_file_name,
            #                     mime_type='image/png',
            #                     upload_key=patch_file_key,
            #                     upload_url=s3_get_file_url(patch_file_key),
            #                 ),
            #                 start_second=start_second,
            #             )
            #         )    
    # SAVE
    document.status_processing_content = "completed"
    session.add(document)

async def _index_video_process_embeddings(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_image_process_embeddings): start')
    # SETUP
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()
    print('INFO (index_pdf.py:_index_image_process_embeddings): document content', document_content)
    document_content_sentences = list(filter(lambda c: c.tokenizing_strategy == "sentence", document_content))
    document_content_maxed_size = list(filter(lambda c: c.tokenizing_strategy == "max_size", document_content))
    document_content_images = list(filter(lambda c: c.image_file_id != None, document_content))
    # CREATE EMBEDDINGS (context is derived from relation)
    # --- agents
    aiagent_sentence_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentence_embed, case_id=document.case_id)
    aiagent_max_size_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_max_size_embed, case_id=document.case_id)
    aiagent_image_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_image_embed, case_id=document.case_id)
    # --- sentences (batch processing to avoid rate limits/throttles)
    sentence_embeddings = aiagent_sentence_embeder.encode_text(list(map(lambda c: c.text, document_content_sentences)))
    sentence_embeddings_as_models = []
    for index, embedding in enumerate(sentence_embeddings):
        sentence_embeddings_as_models.append(Embedding(
            document_id=document_id,
            document_content_id=document_content_sentences[index].id,
            encoded_model_engine=aiagent_sentence_embeder.model_name,
            encoding_strategy="text",
            vector_dimensions=len(embedding),
            vector_json=embedding.tolist(), # converts ndarry -> list (but also makes serializable data)
        ))
    session.add_all(sentence_embeddings_as_models)
    # --- max_size (batch processing to avoid rate limits/throttles)
    maxed_size_embeddings = aiagent_max_size_embeder.encode_text(list(map(lambda c: c.text, document_content_maxed_size)))
    maxed_size_embeddings_as_models = []
    for index, embedding in enumerate(maxed_size_embeddings):
        maxed_size_embeddings_as_models.append(Embedding(
            document_id=document_id,
            document_content_id=document_content_maxed_size[index].id,
            encoded_model_engine=aiagent_max_size_embeder.model_name,
            encoding_strategy="text",
            vector_dimensions=len(embedding),
            vector_json=embedding.tolist(),
        ))
    session.add_all(maxed_size_embeddings_as_models)
    # --- images
    image_embeddings_as_models = []
    for content in document_content_images:
        document_content_file_query = await session.execute(
            sa.select(File)
                .options(joinedload(File.document_content_image_file))
                .where(File.document_content_image_file.any(DocumentContent.id == int(content.id))))
        document_content_file = document_content_file_query.scalars().first()
        image_embeddings = aiagent_image_embeder.encode_image(s3_get_file_url(document_content_file.upload_key))
        image_embeddings_as_models.append(Embedding(
            document_id=document_id,
            document_content_id=content.id,
            encoded_model_engine=aiagent_image_embeder.model_name,
            encoding_strategy="image",
            vector_json=image_embeddings[0].tolist(),
        ))
    session.add_all(image_embeddings_as_models)
    # --- SAVE
    document.status_processing_embeddings = "completed"
    session.add(document)

async def _index_video_process_extractions(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_video_process_extractions): start')
    # FETCH
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars()
    document_content_text = " ".join(map(
        lambda content: content.text if content.tokenizing_strategy == "max_size" else "", document_content))
    # COMPILE/EXTRACT
    # --- classification/description
    print('INFO (index_pdf.py:_index_video_process_extractions): document_description')
    document.document_description = gpt_completion(
        gpt_prompt_video_type.replace('<<SOURCE_TEXT>>', document_content_text[0:11_000]),
        max_tokens=75)
    # --- summary
    print('INFO (index_pdf.py:_index_video_process_extractions): document_summary')
    if len(document_content_text) < 250_000:
        document.document_summary = extract_document_summary(document_content_text)
    # --- events
    print('INFO (index_pdf.py:_index_video_process_extractions): document_events')
    document.document_events = await extract_document_events_v1(document_content_text)
    # SAVE
    document.status_processing_extractions = "completed"
    session.add(document)


# INDEX_VIDEO
async def index_video(session, document_id) -> int:
    print(f"INFO (index_pdf.py): indexing document #{document_id}")
    try:
        # PROCESS FILE & EMBEDDINGS
        print(f"INFO (index_video.py): processing document #{document_id} content")
        await _index_video_process_content(session=session, document_id=document_id)
        print(f"INFO (index_video.py): processing document #{document_id} embeddings")
        await _index_video_process_embeddings(session=session, document_id=document_id)
        print(f"INFO (index_video.py): processing document #{document_id} extractions")
        await _index_video_process_extractions(session=session, document_id=document_id)
        print(f"INFO (index_video.py): finished intake of document #{document_id}")
        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        return document_id
    except Exception as err:
        print(f"ERROR (index_video.py):", err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
