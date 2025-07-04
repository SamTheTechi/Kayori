FROM python:3.13.2-slim

WORKDIR /home/Asuna

RUN apt-get update && apt-get install -y \
  libgl1-mesa-glx \
  gcc \
  build-essential \
  && apt-get clean

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD [ "python", "app.py" ]
