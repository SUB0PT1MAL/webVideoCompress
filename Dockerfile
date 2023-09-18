FROM python

RUN mkdir /var/www
RUN mkdir /var/www/py
RUN mkdir /var/www/py/static
RUN mkdir /var/www/py/templates
RUN mkdir /var/www/py/uploads
RUN mkdir /var/www/py/downloads

COPY main.py /var/www/py/
COPY compressor.py /var/www/py/
COPY decor /var/www/py/static/
COPY index.html /var/www/py/templates/
COPY requirements.txt .

#RUN chmod 777 -R /var/www/py/static/
#RUN chmod 777 -R /var/www/py/uploads/
#RUN chmod 777 -R /var/www/py/downloads/

RUN echo "deb http://deb.debian.org/debian/ sid main contrib non-free non-free-firmware" >> /etc/apt/sources.list
RUN apt update -y

#RUN apt install -y --no-install-recommends nvidia-driver libffmpeg-nvenc-dev
#RUN apt install -y ffmpeg python3 python3-pip python3-venv
RUN apt install -y libffmpeg-nvenc-dev ffmpeg

RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install ffmpeg-python

ENV FLASK_APP=/var/www/py/main.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]