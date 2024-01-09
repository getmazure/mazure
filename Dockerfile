FROM python:3.11-slim

ADD . /mazure/
ENV PYTHONUNBUFFERED 1

WORKDIR /mazure/
RUN  pip install -e . && pip install -r requirements.txt

ENTRYPOINT ["/usr/local/bin/mazure", "-H", "0.0.0.0"]

EXPOSE 5005
