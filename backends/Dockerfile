FROM python:3.10.7-bullseye

WORKDIR /usr/src/backends

COPY . .

RUN pip install -r requirements.txt

EXPOSE 3000

CMD ["python", "src/server.py"]
 