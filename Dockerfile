FROM python:3.10


RUN mkdir /app

COPY . /app/code
WORKDIR /app/code

RUN python -m venv venv
RUN . venv/bin/activate
RUN pip install -e .

ENV PYTHONPATH=/app/code/src

CMD ["python", "src/museum_img_searcher/main.py"]
