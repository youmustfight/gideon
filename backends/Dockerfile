FROM python:3.10.7-bullseye

WORKDIR /user/src/backends

COPY . .

RUN pip install -r requirements.txt

ENV PYTHONPATH /backends

EXPOSE 3000

CMD ["python", "src/server.py"]
 