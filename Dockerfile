FROM python:3.13.2-slim

WORKDIR /home/Asuna

RUN apt-get update && apt-get install -y --no-install-recommends\
  libgl1-mesa-glx \
  gcc \
  supervisor \
  redis-server \
  build-essential \
  && apt-get clean

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /etc/supervisor/conf.d

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8080

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
