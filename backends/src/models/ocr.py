import boto3
import io
import os
from pdf2image import convert_from_bytes
from dbs.sa_models import File
from files.s3_utils import s3_get_file_bytes

# PDF SPLITTING (not really ocr but w/e same gist/world)
def split_file_pdf_to_pil(file: File):
    print('INFO (ocr.py:split_file_pdf_to_pil) start')
    # get file data from s3
    file_bytes = s3_get_file_bytes(file.upload_key)
    # take those bytes and get back a list of PIL.PngImageFile (known as 'pillow images')
    pdf_image_files = convert_from_bytes(file_bytes, fmt='png')  # TODO: always ensure max size to limit processing OCR demand? size=(1400, None)
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
def ocr_parse_image_text(pil_image):
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
        print("Couldn't detect text.", err)
        raise
    else:
        print("INFO Detected blocks count:", len(response['Blocks']))
        # "LINE" blocks can be helpful for chunking by table rows for example
        # "WORD" blocks can be helpful for just concat'ing all data
        blocks_words = list(filter(lambda block: block['BlockType'] == 'WORD', response['Blocks']))
        words = map(lambda block: block['Text'], blocks_words)
        words = " ".join(words) # word blocks will contain periods (ex: { ... Text: 'attacked.' ...})
        # --- return
        return words