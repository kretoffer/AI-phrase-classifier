FROM python:3.12.3
WORKDIR /app

COPY src src
COPY www www
COPY config.py config.py
COPY main.py main.py
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8585
VOLUME /AI-phrase-classifier-data
CMD ["python", "main.py"]