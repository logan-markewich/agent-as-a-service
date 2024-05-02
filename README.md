# Agent-as-a-Service

This project showcases using an agent beyond just a chat interface.

By exposing the lower-level agent APIs in LlamaIndex, this project creates an agent that continuously processes incoming tasks.

Features include:

- create tasks
- view current tasks
- view the output of tasks
- view the steps related to a task
- running the agent continuously vs. step-by-step

[](./api.png)

## Getting Started

First, setup the environment with poetry:

> **_Note:_** This step is not needed if you are using the dev-container.

```
poetry install
poetry shell
```

All config for models and data sources is in the `config/` folder -- here you can configure the LLM and embedding model, the agent parameters, and data loading parameters.

> **_Note:_** If using openai, ensure `OPENAI_API_KEY` is in your environment variables.

Second, generate the embeddings of the documents/data sources configured in `config/loaders.yaml`. By default, its looking for files to index inside a `./data` folder:

```
poetry run generate
```

Third, run the development server:

```
python main.py
```

Once running, the easiest way to get started with testing it out is opening the API docs at `https://127.0.0.1:8000/` and executing some API calls

- create a tasks
- list the current tasks
- toggle the agent on and off
- etc.

## Customization

There are several things you may want to customize

- The settings in the `configs/` folder
- The actual index definition in `app/engine/generate.py` and `app/engine/index.py`
- The actual agent and tools definition in `app/engine/__init__.py`
- The API endpoints in `app/api/routers/agent.py`

## Documentation

After launching the application, visit `https://127.0.0.1:8000/` to view the full Swagger API documentation.

## Using Docker

1. Build an image for the FastAPI app:

```
docker build -t <your_backend_image_name> .
```

2. Generate embeddings:

Parse the data and generate the vector embeddings if the `./data` folder exists - otherwise, skip this step:

```
docker run \
  --rm \
  -v $(pwd)/.env:/app/.env \ # Use ENV variables and configuration from your file-system
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \ # Use your local folder to read the data
  -v $(pwd)/storage:/app/storage \ # Use your file system to store the vector database
  <your_backend_image_name> \
  poetry run generate
```

3. Start the API:

```
docker run \
  -v $(pwd)/.env:/app/.env \ # Use ENV variables and configuration from your file-system
  -v $(pwd)/config:/app/config \
  -v $(pwd)/storage:/app/storage \ # Use your file system to store gea vector database
  -p 8000:8000 \
  <your_backend_image_name>
```

## Learn More

To learn more about LlamaIndex, take a look at the following resources:

- [LlamaIndex Documentation](https://docs.llamaindex.ai) - learn about LlamaIndex.

You can check out [the LlamaIndex GitHub repository](https://github.com/run-llama/llama_index) - your feedback and contributions are welcome!
