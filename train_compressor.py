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
