"""Legacy shim forwarding to the Gemma-only pipeline."""

from __future__ import annotations

from .gemma_pipeline import (
    GemmaTranslationPipeline,
    create_pipeline_from_config,
    load_config,
)

HybridTranslationPipelineOllama = GemmaTranslationPipeline

__all__ = [
    "HybridTranslationPipelineOllama",
    "create_pipeline_from_config",
    "load_config",
]
