import json
from groq import Groq
from app.core.config import settings
from app.core.logging_config import logger
from typing import List, Dict
from prompts.classifier_prompt import CLASSIFIER_PROMPT


class LLMService:
    def __init__(self, bedrock_runtime):
        self.region = settings.AWS_DEFAULT_REGION
        self.model_id = settings.MODEL_ID
        self.bedrock_runtime = bedrock_runtime
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)

    def classify_intent(self, query: str, history_str: str) -> bool:
        """
        Uses Groq to determine if the Knowledge Base is needed.
        
        Args:
            query: The user's current question
            history_str: Formatted conversation history
            
        Returns:
            bool: True if KB is required, False otherwise
        """
        prompt = CLASSIFIER_PROMPT.format(history=history_str, query=query)
        
        try:
            response = self.groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",  # High intelligence for classification
                messages=[{"role": "user", "content": prompt}],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "intent_classification",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "kb_required": {"type": "boolean"},
                                "reasoning": {"type": "string"}
                            },
                            "required": ["kb_required", "reasoning"],
                            "additionalProperties": False
                        }
                    }
                }
            )
            
            result = json.loads(response.choices[0].message.content)
            kb_required = result.get("kb_required", True)
            reasoning = result.get("reasoning", "No reasoning provided")
            
            # Log the classification decision with reasoning
            logger.info(
                f"🔍 Query Classification | "
                f"Query: '{query[:100]}{'...' if len(query) > 100 else ''}' | "
                f"KB Required: {kb_required} | "
                f"Reasoning: {reasoning}"
            )
            
            return kb_required
        except Exception as e:
            logger.error(f"❌ Classification error: {e} | Defaulting to KB fetch")
            return True

    def infer_claude(self, system_prompt: str, user_prompt: str, conversation_history: List[Dict[str, str]] = None):
        """
        Invoke Claude using the proper system and messages structure.
        
        Args:
            system_prompt: The system instructions (Rebecca's personality and rules)
            user_prompt: The current user prompt with context
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            Tuple of (response_text, input_tokens, output_tokens)
        """
        messages = []
        
        # 1. Add conversation history (this is your memory)
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": [{"text": msg["content"]}]
                })
        
        # 2. Add current user prompt
        messages.append({
            "role": "user",
            "content": [{"text": user_prompt}]
        })
        
        # 3. Use the dedicated 'system' parameter in Bedrock
        response = self.bedrock_runtime.converse(
            modelId=self.model_id,
            system=[{"text": system_prompt}],  # Correct way to pass system instructions
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
