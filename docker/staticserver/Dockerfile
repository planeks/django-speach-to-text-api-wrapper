FROM python:3.10-bullseye

COPY ./src/config/static ./opt/project

WORKDIR ./opt/project

CMD python -m http.server 8080