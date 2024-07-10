# views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
import os

def home(request):
    return render(request, 'webapp/home.html')

def sort(request):
    return render(request, 'webapp/sort.html')

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
