# Build
FROM node:22.11-bullseye-slim as build

WORKDIR /app

COPY ./package.json .
RUN npm install

COPY ./static-src ./static-src
COPY ./tsconfig.json .
RUN npm run build

# Final
FROM python:3.11.4-slim-buster

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

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
