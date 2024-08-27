FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN apt-get update && \
    apt-get -y install gcc g++ && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -r /app/requirements.txt --no-cache-dir

RUN python -c "from llama_cpp import Llama; Llama.from_pretrained(repo_id='TheBloke/Tinyllama-2-1b-miniguanaco-GGUF', filename='tinyllama-2-1b-miniguanaco.Q2_K.gguf')"

EXPOSE 8000

CMD ["uvicorn", "chat:app", "--host", "0.0.0.0", "--port", "8000"]
