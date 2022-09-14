FROM python:3.10-alpine

ENV APP_DIR=/app \
    GITHUB_WORKSPACE=/github/workspace
ENV PYTHONPATH=$APP_DIR:$PYTHONPATH

COPY ./requirements.txt $APP_DIR/requirements.txt
RUN apk add --no-cache --update \
    gcc \
    git \
    && \
    pip install --no-cache -r $APP_DIR/requirements.txt

# Handle scenario where host runner owns the repository.
RUN chown -R $(id -u):$(id -g) $GITHUB_WORKSPACE

COPY ./markdown_embed_code $APP_DIR/markdown_embed_code

CMD ["python", "-m", "markdown_embed_code"]
