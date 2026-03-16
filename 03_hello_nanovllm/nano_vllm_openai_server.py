import asyncio
import uuid
import time
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from transformers import AutoTokenizer
from nanovllm import LLM, SamplingParams


# ============================================================
# Configuration
# ============================================================

MODEL_PATH = "/home/jovyan/shared-data/models/huggingface/Qwen3-8B"

MAX_BATCH_SIZE = 8
BATCH_TIMEOUT = 0.01

# ============================================================
# OpenAI API Schemas
# ============================================================

class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str]


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    choices: List[Choice]


# ============================================================
# Request Object
# ============================================================

class InferenceRequest:

    def __init__(self, prompt, params):

        self.id = str(uuid.uuid4())

        self.prompt = prompt
        self.params = params

        self.future = asyncio.get_event_loop().create_future()

        self.created = time.time()


# ============================================================
# Tokenizer Manager
# ============================================================

class TokenizerManager:

    def __init__(self, model_path):

        print("Loading tokenizer...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )

        print("Tokenizer loaded")

    def apply_chat_template(self, messages):

        chat = []

        for m in messages:

            chat.append(
                {"role": m.role, "content": m.content}
            )

        prompt = self.tokenizer.apply_chat_template(
            chat,
            tokenize=False,
            add_generation_prompt=True
        )

        return prompt


# ============================================================
# Inference Engine
# ============================================================

class NanoVLLMEngine:

    def __init__(self, model_path):

        print("Loading model...")

        self.llm = LLM(
            model=model_path,
            enforce_eager=True,
            tensor_parallel_size=1,
            dtype="bfloat16"
        )

        print("Model loaded")

    def generate(self, prompts, params):

        sampling = SamplingParams(
            temperature=params["temperature"],
            max_tokens=params["max_tokens"]
        )

        outputs = self.llm.generate(prompts, sampling)

        texts = []

        for out in outputs:

            texts.append(out["text"])

        return texts


# ============================================================
# Request Scheduler
# ============================================================

class RequestScheduler:

    def __init__(self, engine):

        self.engine = engine

        self.queue = []

        self.lock = asyncio.Lock()

    async def submit(self, req: InferenceRequest):

        async with self.lock:

            self.queue.append(req)

        return await req.future

    async def batch_loop(self):

        print("Scheduler started")

        while True:

            await asyncio.sleep(BATCH_TIMEOUT)

            batch = []

            async with self.lock:

                if len(self.queue) == 0:
                    continue

                batch = self.queue[:MAX_BATCH_SIZE]

                self.queue = self.queue[MAX_BATCH_SIZE:]

            prompts = []

            params = None

            for r in batch:

                prompts.append(r.prompt)

                params = r.params

            start = time.time()

            outputs = self.engine.generate(prompts, params)

            latency = time.time() - start

            for r, text in zip(batch, outputs):

                if not r.future.done():

                    r.future.set_result(
                        {
                            "text": text,
                            "latency": latency
                        }
                    )


# ============================================================
# Server
# ============================================================

class NanoVLLMServer:

    def __init__(self, model_path):

        self.tokenizer = TokenizerManager(model_path)

        self.engine = NanoVLLMEngine(model_path)

        self.scheduler = RequestScheduler(self.engine)

    async def start(self):

        asyncio.create_task(self.scheduler.batch_loop())


# ============================================================
# FastAPI
# ============================================================

app = FastAPI()

server: Optional[NanoVLLMServer] = None


@app.on_event("startup")
async def startup():

    global server

    server = NanoVLLMServer(MODEL_PATH)

    await server.start()

    print("nano_vLLM server started")


# ============================================================
# Utilities
# ============================================================

def format_openai_response(text):

    return ChatCompletionResponse(
        id="chatcmpl-" + str(uuid.uuid4()),
        object="chat.completion",
        created=int(time.time()),
        choices=[
            Choice(
                index=0,
                message=Message(
                    role="assistant",
                    content=text
                ),
                finish_reason="stop"
            )
        ]
    )


# ============================================================
# OpenAI API Endpoint
# ============================================================

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):

    prompt = server.tokenizer.apply_chat_template(
        req.messages
    )

    params = {
        "temperature": req.temperature,
        "max_tokens": req.max_tokens
    }

    infer_req = InferenceRequest(
        prompt,
        params
    )

    result = await server.scheduler.submit(infer_req)

    return format_openai_response(result["text"])


# ============================================================
# Models Endpoint
# ============================================================

@app.get("/v1/models")
async def models():

    return {
        "data": [
            {
                "id": "qwen3",
                "object": "model"
            }
        ]
    }


# ============================================================
# Main
# ============================================================

def main():

    import uvicorn

    uvicorn.run(
        "nano_vllm_openai_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )


if __name__ == "__main__":
    main()