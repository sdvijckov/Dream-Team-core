# Dream-Team-core/dataset_preparation/src/__init__.py

# Можно сделать некоторые функции доступными для импорта напрямую из пакета src, например:
from .main_creator import run_dataset_creation_pipeline
from .data_processor import process_file_to_jsonl
from .file_loaders import load_paragraphs_from_docx, load_paragraphs_from_txt
from .sentence_splitter import split_text_into_sentences
from .ner_extractor import extract_entities
from .text_cleaner import clean_text

# Это позволит в будущем, если нужно, импортировать так:
# from dataset_preparation.src import run_dataset_creation_pipeline
# или если dataset_preparation сам по себе пакет (с __init__.py в dataset_preparation/):
# from dataset_preparation import src
# pipeline_runner = src.run_dataset_creation_pipeline

print("Пакет dataset_preparation.src инициализирован.")