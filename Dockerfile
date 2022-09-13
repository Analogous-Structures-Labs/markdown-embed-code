
RUN apk update && apk --no-cache add git
FROM python:3.10-alpine

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache -r /app/requirements.txt

COPY ./markdown_embed_code /app/markdown_embed_code

ENV PYTHONPATH=/app

WORKDIR /app

CMD ["python", "-m", "markdown_embed_code"]
