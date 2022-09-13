FROM python:3.10-alpine

COPY ./requirements.txt /app/requirements.txt
RUN apk add --no-cache --update \
 git \
 gcc \
 && \
 pip install --no-cache -r /app/requirements.txt

COPY ./markdown_embed_code /app/markdown_embed_code

ENV PYTHONPATH=/app

WORKDIR $GITHUB_WORKSPACE

CMD ["python", "-m", "markdown_embed_code"]
