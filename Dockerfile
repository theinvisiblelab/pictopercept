# syntax=docker/dockerfile:1.4

# Build
FROM node:22.11-bullseye-slim as build

WORKDIR /app

COPY ./package.json .
RUN npm install

COPY ./static-src ./static-src
COPY ./tsconfig.json .
RUN npm run build

# Final
FROM --platform=$BUILDPLATFORM python:3.11-alpine AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
RUN pip install --upgrade pip && \
	pip install -r requirements.txt && \
	pip install gunicorn

COPY ./pictopercept ./pictopercept
COPY ./wsgi.py .

COPY --from=build /app/pictopercept/static /app/pictopercept/static

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
