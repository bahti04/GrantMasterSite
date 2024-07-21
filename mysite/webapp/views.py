# views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
import os

def home(request):
    return render(request, 'webapp/home.html')

def sort(request):
    return render(request, 'webapp/sort.html')

def separation(request):
    return render(request, 'webapp/separation.html')

def merge(request):
    return render(request, 'webapp/merge.html')

def normalization(request):
    return render(request, 'webapp/normalization.html')

def reformat(request):
    return render(request, 'webapp/reformat.html')

def empty(request):
    return render(request, 'webapp/empty.html')

def find_duplicate(request):
    return render(request, 'webapp/find_duplicate.html')

@csrf_exempt
def find_duplicates(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['file']
            input_file_path = os.path.join('uploaded_files', uploaded_file.name)

            # Сохраняем загруженный файл
            with open(input_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Поиск дубликатов
            duplicate_questions = find_duplicate_questions(input_file_path)
            num_duplicates = len(duplicate_questions)

            return JsonResponse({'duplicates': num_duplicates})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

def find_duplicate_questions(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    current_question = []
    question_tags = {'<q>', '<va>', '<v>'}
    seen_questions = set()  # Множество для хранения уже встреченных вопросов
    duplicate_questions = []  # Список для хранения дубликатов

    for line in lines:
        if any(line.startswith(tag) for tag in question_tags):
            if line.startswith('<q>'):
                if current_question:
                    question_text = ' '.join(current_question).strip()
                    # Проверяем, если вопрос уже встречался и не содержит unwanted words
                    if question_text in seen_questions:
                        duplicate_questions.append(question_text)
                    else:
                        seen_questions.add(question_text)
                # Начинаем новый вопрос
                current_question = [line]
            else:
                # Добавляем строку в текущий вопрос
                current_question.append(line)
        else:
            # Пропускаем простые предложения
            continue

    # Проверяем последний вопрос в документе
    if current_question:
        question_text = ' '.join(current_question).strip()
        if question_text in seen_questions:
            duplicate_questions.append(question_text)
        else:
            seen_questions.add(question_text)

    return duplicate_questions

@csrf_exempt
def check_empty_entries(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['file']
            input_file_path = os.path.join('uploaded_files', uploaded_file.name)

            # Сохраняем загруженный файл
            with open(input_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            output_file_path = os.path.join('processed_files', input_file_path[15:len(input_file_path)-4] + '_empty.txt')
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            # Проверка на пустые записи
            empty_entries = find_empty_entries(input_file_path)

            if empty_entries:
                find_and_move_empty_entries(input_file_path, output_file_path)
                download_link = request.build_absolute_uri('/download/' + input_file_path[15:len(input_file_path)-4] + '_empty.txt')
                return JsonResponse({'message': 'Found empty entries.', 'link': download_link})
            else:
                return JsonResponse({'message': 'No empty entries found.'})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

def find_and_move_empty_entries(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split questions by the blank line
    questions = content.strip().split('\n\n')

    valid_questions = []
    invalid_questions = []

    for question in questions:
        lines = question.split('\n')
        question_dict = {
            'q': None,
            'va': None,
            'v': []
        }

        for line in lines:
            if line.startswith('<q>'):
                question_dict['q'] = line[3:].strip()
            elif line.startswith('<va>'):
                question_dict['va'] = line[4:].strip()
            elif line.startswith('<v>'):
                question_dict['v'].append(line[3:].strip())

        if not question_dict['q'] or not question_dict['va'] or '' in question_dict['v']:
            invalid_questions.append(question)
        else:
            valid_questions.append(question)

    # Join the valid and invalid questions with a blank line separator
    sorted_content = '\n\n'.join(valid_questions + invalid_questions)

    # Write the sorted content to the new output file
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(sorted_content)

def find_empty_entries(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split questions by the blank line
    questions = content.strip().split('\n\n')

    empty_entries = []

    for question in questions:
        lines = question.split('\n')
        question_dict = {
            'q': None,
            'va': None,
            'v': []
        }

        for line in lines:
            if line.startswith('<q>'):
                question_dict['q'] = line[3:].strip()
            elif line.startswith('<va>'):
                question_dict['va'] = line[4:].strip()
            elif line.startswith('<v>'):
                question_dict['v'].append(line[3:].strip())

        if not question_dict['q']:
            empty_entries.append(f"Empty question in block:\n{question}")
        if not question_dict['va']:
            empty_entries.append(f"Empty correct answer in block:\n{question}")
        for v in question_dict['v']:
            if not v:
                empty_entries.append(f"Empty variant answer in block:\n{question}")

    return empty_entries

@csrf_exempt
def reformat_file(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['file']
            output_file_name = request.POST.get('output_file_name')
            input_file_path = os.path.join('uploaded_files', uploaded_file.name)

            # Сохраняем загруженный файл
            with open(input_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            output_file_path = os.path.join('processed_files', output_file_name)
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            # Переработка файла
            reformat_questions(input_file_path, output_file_path)

            download_link = request.build_absolute_uri(f'/download/{output_file_name}')

            return JsonResponse({'message': 'File has been reformatted successfully.', 'link': download_link})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

def reformat_questions(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.read()

    questions = lines.split("<q>")
    new_lines = []

    for question in questions:
        if question.strip():
            parts = question.split("<va>")
            if len(parts) > 1:
                question_text = parts[0].strip()
                va_and_vs = parts[1].split("<v>")
                va = va_and_vs[0].strip()
                vs = [f"<v>{v.strip()}" for v in va_and_vs[1:]]

                if va and len(vs) == 3:  # Проверяем, что есть <va> и ровно 3 <v>
                    new_lines.append(f"<q>{question_text}\n<va>{va}")
                    new_lines.extend(vs)
                    new_lines.append("")  # Добавляем пустую строку между вопросами

    with open(output_file, 'w', encoding='utf-8') as file:
        for line in new_lines:
            file.write(line + '\n')

@csrf_exempt
def normalize_file(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['file']
            input_file_path = os.path.join('uploaded_files', uploaded_file.name)

            # Сохраняем загруженный файл
            with open(input_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            output_file_path = os.path.join('processed_files', input_file_path[15:len(input_file_path)-4] + '_norm.txt')
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            # Нормализация файла
            format_questions(input_file_path, output_file_path)

            download_link = request.build_absolute_uri('/download/' + input_file_path[15:len(input_file_path)-4] + '_norm.txt')

            return JsonResponse({'message': 'File has been normalized successfully.', 'link': download_link})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

def format_questions(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # Замена скобок на $
    text = text.replace('\(', '$').replace('\)', '$')

    # Стандартизация тегов
    patterns = {
        r'<\s*q\s*>': '<q>',
        r'<\s*va\s*>': '<va>',
        r'<\s*v\s*>': '<v>'
    }
    for pattern, replacement in patterns.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Перемещаем теги на начало строки
    def move_tag_to_start(match):
        parts = match.groups()
        if len(parts) == 3 and parts[1] in ['<q>', '<va>', '<v>']:
            return f"{parts[1]}{parts[2].strip()}"
        return match.group(0)

    text = re.sub(r'^(.*?)(<q>|<va>|<v>)(.*)$', move_tag_to_start, text, flags=re.MULTILINE)

    # Коррекция форматирования между долларами
    text = re.sub(r'\$\s*([^$]+?)\s*\$', r"$\1$", text)

    lines = text.split('\n')

    with open(output_file, 'w', encoding='utf-8') as file:
        question_block = False
        added_blank_line = False
        option_count = 0

        for i, line in enumerate(lines):
            line = line.rstrip()  # Удаляем пробелы и символы новой строки с конца строки

            if line.startswith('<q>'):
                if question_block and not added_blank_line:
                    file.write('\n')  # Добавляем одну пустую строку перед началом нового блока вопросов
                question_block = True
                added_blank_line = False
                option_count = 0  # Сброс счётчика опций при начале нового вопроса
            elif not question_block:  # Если строка не начинается с <q> и мы не в блоке вопроса
                file.write('<q>')  # Добавляем <q> перед строкой
                question_block = True

            if question_block:
                if line.startswith('<va>') or line.startswith('<v>'):
                    if option_count < 4:  # Проверяем, что добавлено не более одного <va> и трёх <v>
                        file.write(line + '\n')
                        option_count += 1
                    continue

            if line.strip() and not line.startswith('<v>'):  # Пишем строку, если она не пустая и не лишний <v>
                file.write(line + '\n')
                added_blank_line = False
            else:
                if question_block and not added_blank_line:  # Записываем одну пустую строку только если она не добавлена
                    file.write('\n')
                    added_blank_line = True
                    question_block = False  # Конец блока вопросов

@csrf_exempt
def merge_files(request):
    if request.method == 'POST':
        try:
            uploaded_files = request.FILES.getlist('files')
            uploaded_files_paths = []

            # Директория для сохранения загруженных файлов
            upload_dir = os.path.join('uploaded_files')
            os.makedirs(upload_dir, exist_ok=True)

            for uploaded_file in uploaded_files:
                file_path = os.path.join(upload_dir, uploaded_file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                uploaded_files_paths.append(file_path)

            output_file_path = os.path.join('processed_files', 'merged_output.txt')
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            # Объединение файлов
            merge_txt_files(uploaded_files_paths, output_file_path)

            download_link = request.build_absolute_uri('/download/merged_output.txt')

            return JsonResponse({'message': 'Files have been merged successfully.', 'link': download_link})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

def merge_txt_files(files, output_file):
    """Объединяет все загруженные текстовые файлы в один файл."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
                outfile.write('\n')  # Добавляем новую строку между частями для читаемости
    print(f"All files have been merged into {output_file}")

@csrf_exempt
def split_file(request):
    if request.method == 'POST':
        try:
            questions_per_part = int(request.POST.get('questions_per_part'))
            uploaded_file = request.FILES['file']
            input_file_path = os.path.join('uploaded_files', uploaded_file.name)

            # Создаем директории, если они не существуют
            os.makedirs(os.path.dirname(input_file_path), exist_ok=True)

            # Сохраняем загруженный файл
            with open(input_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Разделяем файл на части
            parts = split_txt_into_parts_by_questions(input_file_path, questions_per_part)

            # Генерируем ссылки на скачивание файлов
            download_links = [request.build_absolute_uri(f'/download/{part}') for part in parts]

            return JsonResponse({'message': f'File split into parts with {questions_per_part} questions each.',
                                 'links': download_links})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

def split_txt_into_parts_by_questions(file_path, questions_per_part):
    """Разделяет текстовый файл на части, каждая из которых содержит указанное количество вопросов."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Собираем вопросы
    questions = []
    current_question = []

    # Группировка строк в вопросы
    for line in lines:
        if line.strip().startswith('<q>'):  # Новый вопрос начинается
            if current_question:  # Если текущий вопрос уже содержит данные, сохраняем его
                questions.append(''.join(current_question))
                current_question = []  # Сброс для нового вопроса
        current_question.append(line)
    if current_question:  # Добавляем последний вопрос
        questions.append(''.join(current_question))

    # Создание и запись частей
    part_number = 1
    part_files = []
    for i in range(0, len(questions), questions_per_part):
        part_filename = file_path[15:len(file_path)-4] + f'_{part_number}.txt'
        part_file_path = os.path.join('processed_files', part_filename)
        with open(part_file_path, 'w', encoding='utf-8') as part_file:
            part_file.writelines(questions[i:i + questions_per_part])
        part_files.append(part_filename)
        part_number += 1

    return part_files

@csrf_exempt
def process_file(request):
    if request.method == 'POST':
        try:
            lang = request.POST.get('lang')
            uploaded_file = request.FILES['file']
            input_file_path = os.path.join('uploaded_files', uploaded_file.name)

            # Создаем директории, если они не существуют
            os.makedirs(os.path.dirname(input_file_path), exist_ok=True)

            # Сохраняем загруженный файл
            with open(input_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            output_file_path = os.path.join('processed_files', 'sort_' + uploaded_file.name)

            if lang == 'rus':
                words = ["картин", "изображен", "диаграмм", "график", "таблиц", "текст", "рисун", "рис.", "страниц", "стр.",
                         "абзац", "согласна автор", "глав", "раздел", "в формуле", "в уравнении"]
            elif lang == 'kaz':
                words = ["бейне", "бейнеленген", "диаграмм", "график", "кесте", "мәтін", "сурет", " сурет.", "бет", "бет.",
                         "абзац", "автор келіседі", "тарау", "бөлім", "формулада", "теңдеуде"]
            else:
                return JsonResponse({'message': 'Invalid language'}, status=400)

            remove_unwanted_parts_and_add_space_txt(input_file_path, output_file_path, words)

            return JsonResponse({'message': f'File processed for {lang}', 'output_file': output_file_path})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

def remove_unwanted_parts_and_add_space_txt(txt_path, output_path, words):
    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    line1 = lines[0]
    new_lines = []
    new_lines.append(line1)
    current_question = []
    question_tags = {'<q>', '<va>', '<v>'}
    seen_questions = set()

    pattern = re.compile(r'\d+\.\d+[a-zA-Z]?|\(\s*\d+\.\d+[a-zA-Z]?\s*\)')

    keep_paragraph = True

    for line in lines:
        if any(line.startswith(tag) for tag in question_tags):
            if line.startswith('<q>'):
                if current_question:
                    question_text = ' '.join(current_question).strip()
                    if keep_paragraph and question_text not in seen_questions:
                        if new_lines:
                            new_lines.append('\n')
                        new_lines.extend(current_question)
                        seen_questions.add(question_text)
                current_question = [line]
                keep_paragraph = not any(word.lower() in line.lower() for word in words) and not pattern.search(line)
            else:
                if any(word.lower() in line.lower() for word in words) or pattern.search(line):
                    keep_paragraph = False
                current_question.append(line)
        else:
            continue

    if current_question:
        question_text = ' '.join(current_question).strip()
        if keep_paragraph and question_text not in seen_questions:
            if new_lines:
                new_lines.append('\n')
            new_lines.extend(current_question)
            seen_questions.add(question_text)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)

def download_file(request, file_path):
    file_path = os.path.join('processed_files', file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    return JsonResponse({'message': 'File not found'}, status=404)


