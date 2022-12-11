import cv2
import math
import pydash as _
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from aia.agent import create_ai_action_agent, AI_ACTIONS
from dbs.sa_models import Document, DocumentContent, Embedding, File
from files.opencv_utils import video_frames
from files.s3_utils import s3_get_file_url, s3_upload_file_string
from indexers.utils.extract_document_events import extract_document_events_v1
from indexers.utils.extract_document_summary import extract_document_summary
from indexers.utils.tokenize_string import tokenize_string, TOKENIZING_STRATEGY
from models.assemblyai import assemblyai_transcribe
from models.gpt import gpt_completion
from models.gpt_prompts import gpt_prompt_video_type

async def _index_video_process_content(session, document_id: int) -> None:
    print("INFO (index_pdf.py:_index_video_process_content) started", document_id)
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()

    if len(document_content) == 0:
        # 1. VIDEO -> TEXT (SENTENCES)
        files_query = await session.execute(sa.select(File).where(File.document_id == document_id))
        files = files_query.scalars()
        file = files.first()
        # --- process file for transcript
        transcript_response = assemblyai_transcribe(file.upload_url)
        sentences = transcript_response['sentences']
        # 2. DOCUMENT CONTENT CREATION
        # --- by sentence (w/ start/end times)
        document_content_sentences = []
        counter_sentences = 0
        for sentence in sentences:
            counter_sentences += 1
            document_content_sentences.append(DocumentContent(
                document_id=document_id,
                text=sentence['text'],
                tokenizing_strategy=TOKENIZING_STRATEGY.sentence.value,
                second_start=sentence['second_start'],
                second_end=sentence['second_end'],
                sentence_number=counter_sentences,
            ))
        session.add_all(document_content_sentences)
        # --- sentence clusters
        document_content_sentence_chunks = _.chunk(document_content_sentences, 20)
        document_content_sentences_20 = []
        for dcsc in document_content_sentence_chunks:
            sentence_start = dcsc[0].sentence_number
            sentence_end = dcsc[-1].sentence_number
            second_start = dcsc[0].second_start
            second_end = dcsc[-1].second_end
            document_content_sentences_20.append(DocumentContent(
                document_id=document_id,
                text=' '.join(map(lambda dc: dc.text, dcsc)),
                tokenizing_strategy=TOKENIZING_STRATEGY.sentences_20.value,
                sentence_start=sentence_start,
                sentence_end=sentence_end,
                second_start=second_start,
                second_end=second_end
            ))
        session.add_all(document_content_sentences_20)
        print(f"INFO (index_pdf.py:_index_audio_process_content): Inserted new document content records")

        # IMAGE
        # https://www.storminthecastle.com/posts/video_search/
        # https://www.youtube.com/watch?v=7IL7LKSLb9I&t=159s
        # https://stackoverflow.com/questions/68249421/how-to-modify-patches-made-by-patchify
        # https://stackoverflow.com/questions/55583861/upload-image-from-opencv-to-s3-bucket
        freq=15.0
        last_index = 0
        image_patch_size = 720 // 2 # TODO: probably should adjust patch size based on video dimensions, so we reduce num of patches we make
        image_patch_shape = (image_patch_size, image_patch_size, 3)
        image_patch_step = image_patch_size // 2 # // means disregard the remainder after dividing
        path = s3_get_file_url(file.upload_key)
        # --- get frames
        for frame, timestamp in video_frames(path):
            if timestamp - last_index > freq:
                last_index = timestamp
                second_start = math.floor(last_index)
                # FRAME
                # --- frame before patching vectors
                frame_file_name = f'{document.id}' + '_' + 'image' + '_' + str(second_start).zfill(12) + '.png'
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
                        second_start=second_start,
                    )
                )
                # PATCHIFY # TODO: re-enable this when/if we need to parallelize. takes too long
                # patches = patchify(frame, image_patch_shape, image_patch_step) # don't squeeze, we want the matrix structure as is for saving files
                # for i in range(patches.shape[0]):
                #     for j in range(patches.shape[1]):
                #         # for each patch...
                #         single_image_patch_img = patches[i, j, 0, :, :, :]
                #         single_image_patch_string = cv2.imencode('.png', single_image_patch_img)[1].tostring() # Save as PNG, not JPEG for keeping the quality.
                #         image_patch_file_name = f'{document.id}' + '_' + 'image_patch' + '_' + str(second_start).zfill(12) + '_'+ str(i).zfill(2) + '_' + str(j).zfill(2) + '.png'
                #         image_patch_file_key = 'patches/' + image_patch_file_name
                #         # --- upload the patch
                #         s3_upload_file_string(image_patch_file_key, single_image_patch_string)
                #         # --- create a file + document record
                #         session.add(
                #             DocumentContent(
                #                 document_id=document_id,
                #                 image_patch_size=image_patch_size,
                #                 image_file=File(
                #                     document_id=document_id,
                #                     filename=image_patch_file_name,
                #                     mime_type='image/png',
                #                     upload_key=image_patch_file_key,
                #                     upload_url=s3_get_file_url(image_patch_file_key),
                #                 ),
                #                 second_start=second_start,
                #             )
                #         )
    else:
        print(f"INFO (index_pdf.py:_index_video_process_content): already processed content for document #{document_id} (content count: {len(document_content)})")

    # SAVE
    document.status_processing_content = "completed"
    session.add(document)
    print("INFO (index_pdf.py:_index_video_process_content) done", document_id)

async def _index_video_process_embeddings(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_image_process_embeddings): start')
    # SETUP
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()
    print('INFO (index_pdf.py:_index_image_process_embeddings): document content', document_content)
    document_content_sentences = list(filter(lambda c: c.tokenizing_strategy == TOKENIZING_STRATEGY.sentence.value, document_content))
    document_content_sentences_20 = list(filter(lambda c: c.tokenizing_strategy == TOKENIZING_STRATEGY.sentences_20.value, document_content))
    document_content_images = list(filter(lambda c: c.image_file_id != None, document_content))
    # CREATE EMBEDDINGS (context is derived from relation)
    # --- agents
    aiagent_sentence_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentence_embed, case_id=document.case_id)
    aiagent_sentences_20_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentences_20_embed, case_id=document.case_id)
    aiagent_image_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_image_embed, case_id=document.case_id)
    # --- sentences (batch processing to avoid rate limits/throttles)
    print('INFO (index_pdf.py:_index_video_process_embeddings): encoding sentences...', document_content_sentences)
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
    # --- batch sentences (batch processing to avoid rate limits/throttles)
    print('INFO (index_pdf.py:_index_video_process_embeddings): encoding sentences in chunks of 20...', document_content_sentences_20)
    sentences_20_embeddings = aiagent_sentences_20_embeder.encode_text(list(map(lambda c: c.text, document_content_sentences_20)))
    sentences_20_embeddings_as_models = []
    for index, embedding in enumerate(sentences_20_embeddings):
        sentences_20_embeddings_as_models.append(Embedding(
            document_id=document_id,
            document_content_id=document_content_sentences_20[index].id,
            encoded_model_engine=aiagent_sentences_20_embeder.model_name,
            encoding_strategy="text",
            vector_dimensions=len(embedding),
            vector_json=embedding.tolist(),
        ))
    session.add_all(sentences_20_embeddings_as_models)
    # --- images
    print('INFO (index_pdf.py:_index_video_process_embeddings): images...', document_content_images)
    image_embeddings_as_models = []
    for content in document_content_images:
        document_content_file_query = await session.execute(
            sa.select(File)
                .options(joinedload(File.document_content_image_file))
                .where(File.document_content_image_file.any(DocumentContent.id == int(content.id))))
        document_content_file = document_content_file_query.scalars().first()
        image_embeddings = aiagent_image_embeder.encode_image([s3_get_file_url(document_content_file.upload_key)])
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
    print('INFO (index_pdf.py:_index_video_process_embeddings): done')

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
