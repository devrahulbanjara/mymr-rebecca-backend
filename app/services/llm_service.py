# import torch
# from transformers import pipeline, BitsAndBytesConfig
from app.core.config import settings


class LLMService:
    # _medgemma_pipeline = None

    def __init__(self, bedrock_runtime):
        self.region = settings.AWS_DEFAULT_REGION
        self.model_id = settings.MODEL_ID
        self.bedrock_runtime = bedrock_runtime

    def infer_claude(self, prompt):
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        response = self.bedrock_runtime.converse(
            modelId=self.model_id,
            messages=messages,
            inferenceConfig={"maxTokens": 1024, "temperature": 0.2},
        )
        usage = response.get("usage", {})
        return (
            response["output"]["message"]["content"][0]["text"],
            usage.get("inputTokens", 0),
            usage.get("outputTokens", 0),
        )

    # Comment out the entire MedGemma logic below
    """
    def _get_medgemma_pipeline(self):
        if LLMService._medgemma_pipeline is None:
            from huggingface_hub import login

            login(new_session=False)

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )

            LLMService._medgemma_pipeline = pipeline(
                "text-generation",
                model="google/medgemma-4b-it",
                device_map="auto",
                model_kwargs={
                    "quantization_config": quantization_config,
                    "dtype": torch.bfloat16,
                    "low_cpu_mem_usage": True,
                    "attn_implementation": "sdpa",
                },
            )

        return LLMService._medgemma_pipeline

    def infer_medgemma(self, prompt):
        pipe = self._get_medgemma_pipeline()

        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            },
        ]

        response = pipe(
            text_inputs=messages, max_new_tokens=512, do_sample=True, temperature=0.1
        )

        return response[0]["generated_text"][-1]["content"]
    """
