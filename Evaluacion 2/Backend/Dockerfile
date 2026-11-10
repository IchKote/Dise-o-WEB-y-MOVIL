FROM python:3.13-slim

ARG SERVICE
ENV SERVICE=${SERVICE} PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY masala_common masala_common
COPY services services
COPY gateway gateway
COPY scripts scripts

RUN useradd --system --no-create-home app
USER app

EXPOSE 8000
CMD ["sh", "-c", "if [ \"$SERVICE\" = gateway ]; then M=gateway.app:app; else M=services.$SERVICE.app:app; fi; exec uvicorn $M --host 0.0.0.0 --port 8000 --no-server-header"]
