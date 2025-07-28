# stage one, build packages
FROM python:3.13.2-slim AS builder

WORKDIR /usr

RUN apt-get update && apt-get install -y --no-install-recommends\
  libgl1-mesa-glx \
  build-essential \
  git \
  gcc \
  curl \
  cmake \
  && apt-get clean && rm -rf /var/lib/apt/lists/*


# stage two, building whisper.cpp executale
FROM builder AS whisper-builder

WORKDIR /whisper

RUN git clone https://github.com/ggml-org/whisper.cpp.git && \ 
  cd whisper.cpp && \
  sh ./models/download-ggml-model.sh base.en && \
  cmake -B build && \
  cmake --build build -j --config Release

# stage three, building my pyhton agent 
FROM builder AS python-builder

WORKDIR /python-app

COPY requirements.txt .

RUN pip install --upgrade pip && \
  pip install --prefix=/install --no-cache-dir -r requirements.txt 


# stage four, copying essesntial and creating image
FROM python:3.13.2-slim 

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends\
  sox \
  supervisor \
  redis-server \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=python-builder /install /usr/local

COPY --from=whisper-builder /whisper/whisper.cpp/build/bin/whisper-cli /usr/local/bin/
COPY --from=whisper-builder /whisper/whisper.cpp/build/libwhisper.so* /usr/local/lib/

RUN chmod +x /usr/local/bin/whisper-cli

COPY . .
RUN mkdir -p /etc/supervisor/conf.d
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8080

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
