from flask import Flask, request, render_template, abort
import re
import pandas as pd
import os
from werkzeug.utils import secure_filename
import io
import math

app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.txt']
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
corpus = []
app.config['UPLOAD_PATH'] = corpus


@app.route('/')
def index():
    return render_template('my-form.html')


@app.route('/', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist('file')
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            save_file(file, app.config['UPLOAD_PATH'])
    tables = make_data(corpus)
    view = make_tables(tables)
    return view


def save_file(file, path):
    bytesio = io.BytesIO()

    file.save(bytesio)
    path.append(bytesio.getvalue().decode('UTF-8'))
    return path


def text_to_words(text: str) -> list:
    pattern = r'[^a-zа-яё;/\s]*'
    text = re.sub(pattern, '', text, flags=re.I | re.U | re.DOTALL)
    words = text.split()
    return words


def count_words(words: list) -> dict:
    wordfreq = {}
    for word in words:
        if word not in wordfreq:
            wordfreq[word] = 0
        wordfreq[word] += 1
    return wordfreq


def calculate_idf(texts: list, word: str) -> float:
    return math.log10(len(texts) / sum([1.0 for text in texts if word in text.keys()]))


def make_data(texts: list):
    texts = [text_to_words(text) for text in texts]
    texts = [count_words(text) for text in texts]
    for text in texts:
        for key in text:
            text[key] = [text[key], float(text[key]) / float(len(text))]

    for text in texts:
        for key in text:
            text[key].append(calculate_idf(texts, key))

    return texts


def make_tables(data: list):
    data = [pd.DataFrame.from_dict(text, orient='index', columns=['count', 'tf', 'idf']).head(50).to_html() for text in data]
    return "\n\n".join(data)



