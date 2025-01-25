# syntax=docker/dockerfile:1.4

FROM --platform=$BUILDPLATFORM python:3.13-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
RUN pip install --upgrade pip && \
	pip install -r requirements.txt && \
	pip install gunicorn

COPY ./pictopercept ./pictopercept
COPY ./wsgi.py .

CMD ["gunicorn", "wsgi:app"]

FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF

# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /

CMD ["gunicorn", "wsgi:app"]
