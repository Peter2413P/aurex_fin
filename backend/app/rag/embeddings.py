import os
import urllib.request
from typing import List
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
from langchain_core.embeddings import Embeddings
from functools import lru_cache

class MultilingualONNXEmbeddings(Embeddings):
    """
    High-performance, lightweight multilingual embedding engine using ONNX Runtime
    and pure-Rust Tokenizers. Supports Tamil, English, Tanglish, and 50+ languages
    with zero PyTorch runtime DLL overhead.
    """
    def __init__(self, model_path: str = None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            onnx_dir = os.path.join(base_dir, "onnx_models")
            os.makedirs(onnx_dir, exist_ok=True)
            model_path = os.path.join(onnx_dir, "multilingual_minilm_l12.onnx")
            
            if not os.path.exists(model_path):
                print(f"[EMBEDDINGS] Downloading multilingual ONNX model to {model_path}...", flush=True)
                url = "https://huggingface.co/Xenova/paraphrase-multilingual-MiniLM-L12-v2/resolve/main/onnx/model_quantized.onnx"
                urllib.request.urlretrieve(url, model_path)
                print("[EMBEDDINGS] Download complete.", flush=True)

        self.model_path = model_path
        self.session = ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
        self.tokenizer = Tokenizer.from_pretrained("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.input_names = [inp.name for inp in self.session.get_inputs()]

    def _encode_single(self, text: str) -> List[float]:
        if not text or not text.strip():
            # Return zero vector for empty strings
            return [0.0] * 384
            
        enc = self.tokenizer.encode(text)
        input_ids = np.array([enc.ids], dtype=np.int64)
        attention_mask = np.array([enc.attention_mask], dtype=np.int64)
        
        inputs = {"input_ids": input_ids, "attention_mask": attention_mask}
        if "token_type_ids" in self.input_names:
            inputs["token_type_ids"] = np.zeros_like(input_ids)
            
        outputs = self.session.run(None, inputs)
        token_embeddings = outputs[0]  # Shape: (1, seq_len, 384)
        
        # Mean pooling weighted by attention mask
        mask_expanded = np.expand_dims(attention_mask, -1).astype(float)
        sum_embeddings = np.sum(token_embeddings * mask_expanded, axis=1)
        sum_mask = np.clip(mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
        mean_pooled = sum_embeddings / sum_mask
        
        # L2 Normalization for exact cosine distance via inner product
        norm = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
        norm = np.clip(norm, a_min=1e-9, a_max=None)
        normalized = (mean_pooled / norm)[0]
        return normalized.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._encode_single(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._encode_single(text)

@lru_cache(maxsize=1)
def get_embeddings_model() -> Embeddings:
    return MultilingualONNXEmbeddings()

get_embeddings = get_embeddings_model

