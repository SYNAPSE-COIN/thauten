"""Symbolic Compression Training Routine

This module provides a staged GRPO-based training pipeline for symbolic compression and recovery
using the verifiers setup. Each phase applies targeted prompt templates with placeholder tags.

=== TRAINING PHASES & PROMPTS ===

Phase 1: Identity (α=0.005, β=3.0) - Emphasis on accuracy
├── prompts/identity_compression.txt     → {content}
├── prompts/identity_decompression.txt   → {compressed}
└── prompts/evaluation.txt               → {original}, {restored}

Phase 2: Structured (α=0.02, β=2.0) - Learn abbreviations/symbol systems
├── prompts/structured_compression.txt   → {content}
├── prompts/structured_decompression.txt → {compressed}
└── prompts/evaluation.txt               → {original}, {restored}

Phase 3: Freeform (α=0.05, β=1.5) - Develop symbolic style
├── prompts/freeform_compression.txt     → {content}
├── prompts/freeform_decompression.txt   → {compressed}
└── prompts/evaluation.txt               → {original}, {restored}

Phase 4: Cognition (α=0.1, β=1.0) - Reasoning with compression priority
├── prompts/cognition_compression.txt    → {content}
├── prompts/cognition_decompression.txt  → {compressed}
└── prompts/evaluation.txt               → {original}, {restored}

=== PROMPT TAG SOURCES ===

{content}       ← Sample text from dataset
                  • agentlans/wikipedia-paragraphs (phases 1–3)
                  • willcb/gsm8k-python-test (phase 4, mapped to 'text' field)

{compressed}    ← Result from compression rollout
                  • Extracted from <compress>...</compress> sections
                  • Input for decompression rollout

{original}      ← Initial dataset text
                  • Identical to {content}, preserved for scoring

{restored}      ← Output from decompression rollout
                  • Extracted from <decompress>...</decompress> sections
                  • Compared against {original} for fidelity

=== EXECUTION FLOW ===

For each dataset example:
1. Compression:        {content} → compression_prompt → <compress>result</compress>
2. Decompression:      {compressed} → decompression_prompt → <decompress>result</decompress>
3. Evaluation:         {original} + {restored} → evaluation_prompt → fidelity_score
4. Reward Function:    reward = base_score - α×tokens - β×(1-fidelity)
5. Both steps receive identical reward for gradient updates

=== PROMPT FORMATS ===

Supported formats:
• Legacy: Plain string templates with {tag} substitutions
• Conversation: Dialogue format using <|im_start|>role...content<|im_end|>

Format is auto-detected via "# Multi-turn conversation format" marker.
"""
import logging
from synapse.main import main

logger = logging.getLogger("synapse")

if __name__ == "__main__":
    main(
        "🧠 Symbolic Compressor Training",
        default_model="",
        default_data=""
    )

