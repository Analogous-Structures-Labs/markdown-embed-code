FROM python:3.10-alpine

ENV APP_DIR=/app \
    GITHUB_WORKSPACE=/github/workspace
ENV PYTHONPATH=$APP_DIR:$PYTHONPATH

COPY ./requirements.txt $APP_DIR/requirements.txt
RUN apk add --no-cache --update \
    git \
    gcc \
    && \
    pip install --no-cache -r $APP_DIR/requirements.txt

COPY ./markdown_embed_code $APP_DIR/markdown_embed_code

USER 1001:121

WORKDIR $GITHUB_WORKSPACE

CMD ["python", "-m", "markdown_embed_code"]
