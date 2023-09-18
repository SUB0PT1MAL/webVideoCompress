import os
import subprocess
import random
from datetime import datetime
from flask import Flask, request, redirect, send_file, render_template

from compressor import compress_video


app = Flask(__name__, static_folder='/var/www/py/static/')

# Define the target sizes and their labels
target_sizes = [8, 25, 50, 100]
target_size_labels = {
    8: '8 MB',
    25: '25 MB',
    50: '50 MB',
    100: '100 MB'
}


def format_size(size):
    power = 1024
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.1f} {power_labels[n]}B"


@app.route('/')
def index():
    return render_template('index.html', target_sizes=target_sizes, target_size_labels=target_size_labels)


@app.route('/', methods=['POST'])
def upload_file():
    file = request.files['file']
    target_size = int(request.form.get('target_size'))
    print(target_size)
    random_number = random.randint(10001, 99998)
    file_name = f"up_{random_number}_{file.filename}"
    file_path = ("/var/www/py/uploads/" + file_name)
    file.save(file_path)

    compressed_file_name = f"chibi_{file.filename}"
    compressed_file_path = ("/var/www/py/downloads/" + compressed_file_name)

    file_path_io = open(file_path, 'rb')
    compress_video(file_path_io, file_path, compressed_file_path, target_size)

    download_link = f"/var/www/py/downloads/{compressed_file_name}"
    download_filename = compressed_file_name
    download_size = format_size(os.path.getsize(compressed_file_path))
    os.remove(file_path)

    return render_template('index.html', download_link=download_link, download_filename=download_filename,
                           download_size=download_size, target_sizes=target_sizes, target_size_labels=target_size_labels)


@app.route('/var/www/py/downloads/<path:filename>', methods=['GET'])
def download(filename):
    file_path = os.path.join(app.root_path, 'downloads', filename)
    response = send_file(file_path, as_attachment=True)
    os.remove(file_path)
    return response


if __name__ == '__main__':
    app.run()
