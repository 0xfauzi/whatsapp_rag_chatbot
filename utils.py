from PyPDF2 import PdfReader
import logging
import os
from urllib.parse import urlparse
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_text_from_pdf(pdf_doc_path):
    text = ''
    pdf_reader = PdfReader(pdf_doc_path)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_media_id(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    media_id = os.path.basename(path)
    return media_id

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)