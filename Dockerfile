FROM python:3.13.2-slim

WORKDIR /home/Asuna

RUN apt-get update && apt-get install -y \
  libgl1-mesa-glx \
  gcc \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --upgrade pip

COPY . .

EXPOSE 8080

CMD [ "python", "app.py" ]
