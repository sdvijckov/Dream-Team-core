# Dream-Team-core/dataset_preparation/src/dialogue_identifier.py
import re
from typing import Dict, Optional, Tuple, Union

# Регулярные выражения для поиска диалогов
# 1. Прямая речь в кавычках (елочки или двойные)
RE_QUOTED_SPEECH = re.compile(r'(«[^»]+»|"[^"]+")')

# 2. Прямая речь, начинающаяся с тире (и пробела, опционально)
RE_DASH_SPEECH_START = re.compile(r'^\s*[-–—]\s*([А-ЯЁA-Z])') # Тире, пробелы, затем заглавная буква

# 3. Слова автора ПОСЛЕ прямой речи: «П», – а. / «П!» – а. / «П?» – а.
#    Или: "П", – а. / "П!" – а. / "П?" – а.
#    Захватывает прямую речь и слова автора.
RE_AUTHOR_WORDS_AFTER = re.compile(
    r'([«"].+[»"!?,])\s*[-–—]\s*([а-яё\s\w]+[.?!]?)',  # \w включает буквы, цифры, _
    re.IGNORECASE # Чтобы "сказал Он" тоже сработало, хотя обычно слова автора с маленькой
)
# TODO: Улучшить RE_AUTHOR_WORDS_AFTER для более точного захвата слов автора

# 4. Слова автора ПЕРЕД прямой речью: А: «П». / А: "П".
RE_AUTHOR_WORDS_BEFORE = re.compile(
    r'^([\w\s.\-]+?):\s*([«"].+[»"]|[А-ЯЁA-Z])' # Захватывает автора и начало прямой речи
)
# TODO: Улучшить RE_AUTHOR_WORDS_BEFORE

def extract_dialogue_info(sentence_text: str) -> Dict[str, Optional[Union[bool, str]]]:
    """
    Анализирует предложение на наличие признаков диалога и пытается извлечь спикера.

    Returns:
        dict: {
            "is_dialogue": bool,
            "speaker": Optional[str],
            "dialogue_cue": Optional[str] # Тип найденного маркера диалога
        }
    """
    dialogue_info = {
        "is_dialogue": False,
        "speaker": None,
        "dialogue_cue": None
    }
    
    # Приводим к нижнему регистру для некоторых проверок, но сохраняем оригинал для спикера
    # cleaned_sentence = sentence_text.strip() # Предполагаем, что текст уже немного очищен

    # 1. Проверка на слова автора ПОСЛЕ прямой речи (наиболее явный признак)
    # Пример: «Привет!», – сказал он.
    match_author_after = RE_AUTHOR_WORDS_AFTER.search(sentence_text)
    if match_author_after:
        dialogue_info["is_dialogue"] = True
        dialogue_info["dialogue_cue"] = "author_words_after"
        # Пытаемся извлечь спикера из слов автора (очень упрощенно)
        author_words = match_author_after.group(2).strip()
        # Простая эвристика: если есть слово "сказал", "спросил", "ответил" и т.п. + имя
        # Это очень грубо и требует доработки, например, с помощью NER или морфологии
        # Здесь можно будет интегрировать NER, чтобы найти PER в author_words
        # Пока просто возвращаем все слова автора как возможного спикера, если они короткие
        if len(author_words.split()) <= 3 and not any(c in author_words for c in '?!.'): # Если это не полное предложение
            # Попробуем найти имена собственные (заглавные буквы)
            potential_speaker = re.findall(r'\b[А-ЯЁ][а-яё]+\b', author_words)
            if potential_speaker:
                 dialogue_info["speaker"] = " ".join(potential_speaker)
            # else:
            #     dialogue_info["speaker"] = author_words # менее надежно
        return dialogue_info # Возвращаем, так как это сильный признак

    # 2. Проверка на слова автора ПЕРЕД прямой речью
    # Пример: Иван: «Привет!»
    match_author_before = RE_AUTHOR_WORDS_BEFORE.match(sentence_text) # match, т.к. с начала строки
    if match_author_before:
        dialogue_info["is_dialogue"] = True
        dialogue_info["dialogue_cue"] = "author_words_before"
        potential_speaker_text = match_author_before.group(1).strip().rstrip(':')
        # Здесь тоже можно использовать NER или более сложные правила
        dialogue_info["speaker"] = potential_speaker_text # Пока берем все до двоеточия
        return dialogue_info

    # 3. Проверка на прямую речь, начинающуюся с тире
    # Пример: – Привет!
    if RE_DASH_SPEECH_START.match(sentence_text):
        dialogue_info["is_dialogue"] = True
        dialogue_info["dialogue_cue"] = "dash_start"
        # Спикера из этого формата извлечь сложно без контекста предыдущих предложений
        return dialogue_info

    # 4. Проверка на прямую речь в кавычках (без явных слов автора в этом же предложении)
    # Пример: «Привет!»
    if RE_QUOTED_SPEECH.search(sentence_text):
        # Если все предложение это только цитата, то это диалог
        # Удаляем кавычки и проверяем, не осталось ли чего-то кроме пробелов
        dequoted = sentence_text.replace('«','').replace('»','').replace('"','').strip()
        original_dequoted_len = len(dequoted)
        
        # Проверяем, есть ли что-то кроме цитаты в предложении
        non_quote_parts = RE_QUOTED_SPEECH.sub('', sentence_text).strip()

        if not non_quote_parts or len(non_quote_parts) < original_dequoted_len * 0.3 : # Если вне цитаты мало текста
            dialogue_info["is_dialogue"] = True
            dialogue_info["dialogue_cue"] = "quoted_speech"
            # Спикера из этого формата извлечь сложно без контекста
            return dialogue_info
            
    return dialogue_info


if __name__ == '__main__':
    test_sentences = [
        "«Привет! Как дела?», – спросил Иван.",
        "Он ответил: «Все отлично!»",
        "– Добрый день, – сказал он.",
        "– А ты кто?",
        "«Просто проходил мимо.»",
        "Это обычное предложение без диалога.",
        "Иван сказал: «Пойдем гулять».",
        "«Пойдем», – согласилась Маша.",
        "Маша подумала: «Какая хорошая погода!» (это внутренняя речь, но формально как диалог)",
        "– Ну что ж, – вздохнул он, – придется идти.",
        "Предложение с цитатой: В книге было написано «жили-были». Это не диалог.",
        "«Полностью цитата»",
    ]

    print("Тестирование идентификации диалогов:")
    for sentence in test_sentences:
        info = extract_dialogue_info(sentence)
        print(f"\nПредложение: '{sentence}'")
        print(f"  Результат: {info}")