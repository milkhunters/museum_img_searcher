FROM python:3.12


RUN pip install poetry

COPY . /code
WORKDIR /code

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

ENV PYTHONPATH=/code/src

CMD ["python", "src/museum_img_searcher/main.py"]
