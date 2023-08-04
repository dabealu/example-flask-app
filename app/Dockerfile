# syntax=docker/dockerfile:1
FROM python:3.9-bookworm

WORKDIR /app

RUN useradd -d /app -s /bin/bash -U app &&\
    chown -R app:app /app

USER app

COPY --chown=app:app requirements.txt /app

RUN pip3 install -r requirements.txt

COPY --chown=app:app . /app

ENV PATH="$PATH:/app/.local/bin"

CMD ["python3", "userapi.py"]
