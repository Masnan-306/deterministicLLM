FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app
COPY . /app

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

ENV CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS"

RUN pip install -r /app/requirements.txt --no-cache-dir

RUN python -c "from llama_cpp import Llama; Llama.from_pretrained(repo_id='TheBloke/Tinyllama-2-1b-miniguanaco-GGUF', filename='tinyllama-2-1b-miniguanaco.Q2_K.gguf')"

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
