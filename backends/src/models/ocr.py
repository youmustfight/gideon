from time import sleep
from typing import List
import boto3
import io
import os
from pdf2image import convert_from_bytes
from dbs.sa_models import File
import env
from files.s3_utils import s3_get_file_bytes

# PDF SPLITTING (not really ocr but w/e same gist/world)
def split_file_pdf_to_pil(file: File):
    print('INFO (ocr.py:split_file_pdf_to_pil) start')
    # get file data from s3
    file_bytes = s3_get_file_bytes(file.upload_key)
    # take those bytes and get back a list of PIL.PngImageFile (known as 'pillow images')
    print('INFO (ocr.py:split_file_pdf_to_pil) splitting pdf to PNGs')
    pdf_image_files = convert_from_bytes(file_bytes, fmt='png')  # TODO: always ensure max size to limit processing OCR demand? size=(1400, None)
    print(f'INFO (ocr.py:split_file_pdf_to_pil) split pdf to {len(pdf_image_files)} PNGs')
    return pdf_image_files


# PARSING
# # ATTEMPT #1 - EASYOCR (blows up local machine when in dev, sequentially blocking)
# reader = easyocr.Reader(['en'], gpu=env.env_is_gpu_available(), verbose=True) # don't think we'll have GPUs on AWS instances
# def ocr_parse_image_text(pil_image):
#     print('INFO (ocr.py:ocr_parse_image_text) start')
#     # --- ocr (confused as shit converting PIL.PngImagePlugin.PngImageFile to bytes)
#     img_byte_arr = io.BytesIO()
#     pil_image.save(img_byte_arr, format='png')
#     page_ocr_str_array = reader.readtext(img_byte_arr.getvalue(), detail=0)
#     # --- compile all extracted text tokens into 1 big string so we can break down into sentences
#     page_ocr_text = ' '.join(page_ocr_str_array).encode(encoding='ASCII',errors='ignore').decode()
#     return page_ocr_text

# ATTEMPT #2 - DONUT (extra blows up local machine when in dev, not for full document parsing)
# (in a separate PR)

# ATTEMPT #3 - AWS TEXTRACT (can do in parallel easily, 1k page pdfs doesn't matter)
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract.html#Textract.Client.analyze_document
session = boto3.session.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)
textract_client = session.client(service_name='textract', region_name=os.environ.get('AWS_REGION'))
async def ocr_parse_image_text(pil_image):
    print('INFO (ocr.py:ocr_parse_image_text) start')
    try:
        # --- convert image to bytes
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='png')
        # --- analyze
        response = textract_client.analyze_document(
            Document={'Bytes': img_byte_arr.getvalue()},
            FeatureTypes=['FORMS'], # 'TABLES','QUERIES','SIGNATURES'
        )
    except Exception as err:
        print("ERROR (ocr.py:ocr_parse_image_text) Couldn't detect text.", err)
        raise
    else:
        print(f'INFO (ocr.py:ocr_parse_image_text) Detected blocks count:', len(response['Blocks']))
        # 'LINE' blocks can be helpful for chunking by table rows for example
        # 'WORD' blocks can be helpful for just concat'ing all data
        blocks_words = list(filter(lambda block: block['BlockType'] == 'WORD', response['Blocks']))
        words_arr = list(map(lambda block: block['Text'], blocks_words))
        words = ' '.join(words_arr) # word blocks will contain periods (ex: { ... Text: 'attacked.' ...})
        # --- return
        print(f'INFO (ocr.py:ocr_parse_image_text) Word count: {len(words_arr)}')
        return words


# PDF -> TEXT BY PAGE
async def ocr_parse_pdf_to_text(file_pdf: File) -> List[str]:
    print('INFO (ocr.py:ocr_parse_pdf_to_text) start')
    try:
        # --- analyze (async job w/ file s3 location): https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract.html#Textract.Client.start_document_text_detection
        start_textract_response = textract_client.start_document_text_detection(
            DocumentLocation={
                'S3Object': {
                    'Bucket': env.env_get_aws_s3_files_bucket(),
                    'Name': file_pdf.upload_key,
                }
            },
            OutputConfig={
                'S3Bucket':  env.env_get_aws_s3_files_bucket(),
            }
        )
        textract_job_id = start_textract_response['JobId']
    except Exception as err:
        print("ERROR (ocr.py:ocr_parse_pdf_to_text) Couldn't detect text.", err)
        raise
    else:
        number_seconds_waited_for_textract_job = 0
        is_textract_job_done = False
        top_level_blocks = []
        # --- await textract job to finish: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract.html#Textract.Client.get_document_text_detection
        while is_textract_job_done == False:
            get_textract_response = textract_client.get_document_text_detection(JobId=textract_job_id)
            print(f'INFO (ocr.py:ocr_parse_pdf_to_text) getting textract job {textract_job_id}....', get_textract_response['JobStatus'])
            # --- if failed, raise 
            if get_textract_response['JobStatus'] == 'FAILED':
                raise get_textract_response
            # --- if in succeeded 
            elif get_textract_response['JobStatus'] == 'SUCCEEDED':
                print(f'INFO (ocr.py:ocr_parse_pdf_to_text) successful textract job {textract_job_id}....')
                is_textract_job_done = True
                # --- next token handler
                def get_next_blocks(blocks, NextToken):
                    print(f'INFO (ocr.py:ocr_parse_pdf_to_text) get_next_blocks {textract_job_id} - {NextToken}')
                    if (NextToken == None):
                        return blocks
                    next_get_textract_response = textract_client.get_document_text_detection(JobId=textract_job_id, NextToken=NextToken)
                    return get_next_blocks(blocks + next_get_textract_response['Blocks'], next_get_textract_response.get('NextToken'))
                # --- start
                top_level_blocks = get_next_blocks(get_textract_response['Blocks'], get_textract_response.get('NextToken'))
            # --- otherwise wait (IN_PROGRESS or PARTIAL_SUCCESS)
            number_seconds_waited_for_textract_job += 2
            sleep(2)

        # --- handle finished response, parsing by page
        print(f'INFO (ocr.py:ocr_parse_pdf_to_text) Detected page blocks count:', len(top_level_blocks))
        # --- block id map for page reference
        pages_text = dict()
        for block in top_level_blocks:
            if (block.get('BlockType') == 'WORD'):
                if (pages_text.get(block.get('Page')) == None): pages_text.update({ block.get('Page'): "" })
                pages_text.update({ block.get('Page'): pages_text.get(block.get('Page')) + f" {block.get('Text')}" })

        # --- return
        print(f'INFO (ocr.py:ocr_parse_pdf_to_text) Pages of text:', len(pages_text.keys()))
        return pages_text.values()
