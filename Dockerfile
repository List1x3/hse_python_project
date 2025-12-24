FROM python:3.10

ENV PYTHONPATH=/app/src:$PYTHONPATH
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest", "tests", "-v"]