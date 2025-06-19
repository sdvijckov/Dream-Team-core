# Dream-Team-core/dataset_preparation/src/ner_extractor.py
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser, # Пока не используется активно, но является частью стандартного пайплайна
    NewsNERTagger,
    Doc
)
from typing import List, Dict, Union

# --- Инициализация компонентов Natasha (один раз при загрузке модуля) ---
# Эти объекты довольно "тяжелые", поэтому создаем их глобально для модуля
try:
    segmenter_ner = Segmenter()
    morph_vocab_ner = MorphVocab()
    emb_ner = NewsEmbedding()
    morph_tagger_ner = NewsMorphTagger(emb_ner)
    syntax_parser_ner = NewsSyntaxParser(emb_ner) 
    ner_tagger_ner = NewsNERTagger(emb_ner)
    _NATASHA_COMPONENTS_LOADED = True
    print("Компоненты Natasha для NER успешно инициализированы.")
except Exception as e:
    _NATASHA_COMPONENTS_LOADED = False
    print(f"Ошибка при инициализации компонентов Natasha для NER: {e}")
    print("Функция извлечения сущностей может не работать корректно.")
# -----------------------------------------------------------------------------

def extract_entities(text_content: str) -> List[Dict[str, Union[str, int]]]:
    """
    Извлекает именованные сущности (PER, LOC, ORG и др.) из текста с помощью Natasha.
    """
    if not _NATASHA_COMPONENTS_LOADED:
        print("Ошибка: Компоненты Natasha для NER не были загружены. Извлечение сущностей невозможно.")
        return []
        
    if not text_content:
        return []
    
    doc = Doc(text_content)
    try:
        doc.segment(segmenter_ner)
        doc.tag_morph(morph_tagger_ner)
        # doc.parse_syntax(syntax_parser_ner) # Можно раскомментировать, если синтаксис нужен для NER или других задач
        doc.tag_ner(ner_tagger_ner)
    except Exception as e:
        print(f"Ошибка во время обработки текста Natasha: {e}")
        return []

    entities = []
    for span in doc.spans:
        # span.normalize(morph_vocab_ner) # Можно добавить нормализацию, если нужно
        entities.append({
            "text": span.text,
            "type": span.type,
            "start_char": span.start, # Natasha использует start/stop для символьных индексов
            "end_char": span.stop
        })
    return entities

if __name__ == '__main__':
    # Пример использования
    sample_text = "Иван Грозный взял Казань в 1552 году. Петр Первый основал Санкт-Петербург."
    print(f"Текст: '{sample_text}'")
    
    # Для теста может потребоваться время на первую загрузку моделей Natasha, если они не кешированы
    extracted_entities = extract_entities(sample_text)
    
    if extracted_entities:
        print("Извлеченные сущности:")
        for entity in extracted_entities:
            print(f"  - {entity}")
    else:
        print("Сущности не найдены или произошла ошибка.")

    empty_text = ""
    print(f"\nТекст: '{empty_text}'")
    extracted_entities_empty = extract_entities(empty_text)
    print(f"Извлеченные сущности из пустого текста: {extracted_entities_empty}")