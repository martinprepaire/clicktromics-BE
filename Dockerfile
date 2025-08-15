FROM python:3.12

RUN apt-get update && apt-get install -y \
    libxrender1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install git+https://LOudPrepaire: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@github.com/LOudPrepaire/bio-core-lib.git@v1.0.12

COPY . /app/

EXPOSE 80

CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "80", "--reload"]