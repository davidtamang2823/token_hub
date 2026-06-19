FROM python:3.12-slim-bookworm

WORKDIR /usr/tokenhub

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/usr/tokenhub/app

RUN addgroup --system tokenhub && adduser --system --ingroup tokenhub tokenhub
USER tokenhub

CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8000"]