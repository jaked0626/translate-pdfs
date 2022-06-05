import deepl
import os
from dotenv import load_dotenv
from multiprocessing import Pool

def main():
    load_dotenv()
    pool = Pool(os.cpu_count() - 1)
    interpreted_syllabi = os.listdir('./interpreted-syllabi2/')
    pool.map(translate_single_syllabus, interpreted_syllabi)
    

def translate_single_syllabus(syllabus):
    print(f'translating {syllabus}...')
    with open(f'./interpreted-syllabi2/{syllabus}', 'r') as f:
        text = f.read()
    translator = deepl.Translator(os.getenv('DEEPL_AUTH'))
    try: 
        results = translator.translate_text(text, target_lang="EN-US")
        with open(f'translated-syllabi/{syllabus}', 'w') as f:
            f.write(results.text)
    except Exception:
        print(f'translation of {syllabus} went wrong, skipping')
        pass
    


if __name__ == "__main__": 
    main()