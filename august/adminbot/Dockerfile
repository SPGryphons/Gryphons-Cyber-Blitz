FROM python:3.11-slim-bullseye

COPY bot.py .

COPY webhook_logger.py .

RUN pip3 install --no-cache-dir python-dotenv requests playwright

RUN playwright install --with-deps chromium

ENTRYPOINT ["python3", "-u", "bot.py"]

CMD ["host.docker.internal", "1337"]