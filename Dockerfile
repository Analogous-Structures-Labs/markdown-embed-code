FROM python:3.10-alpine

ARG GITHUB_WORKSPACE

ENV APP_DIR=/app
ENV PYTHONPATH=$APP_DIR:$PYTHONPATH

COPY ./requirements.txt $APP_DIR/requirements.txt
RUN apk add --no-cache --update \
    git \
    && \
    pip install --no-cache -r $APP_DIR/requirements.txt

COPY ./markdown_embed_code $APP_DIR/markdown_embed_code

RUN git config --global --add safe.directory /github/workspace

CMD ["python", "-m", "markdown_embed_code"]
