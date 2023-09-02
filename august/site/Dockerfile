FROM python:3.11-slim-bullseye

RUN groupadd -r ctf && useradd -r -g ctf ctf

WORKDIR /app

COPY app .

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 1337

USER ctf

CMD ["python3", "-u", "app.py"]
