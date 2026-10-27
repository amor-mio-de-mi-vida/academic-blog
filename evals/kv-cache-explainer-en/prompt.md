---
tags: [skill-creator]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch, WebSearch]
---

Write an explainer blog post on how the KV cache speeds up autoregressive transformer inference, and why it becomes the memory bottleneck at long context lengths (cover MQA/GQA as the fix). Audience: ML engineers who know the transformer architecture. I want clear diagrams, plus a chart of KV-cache memory vs. context length for a Llama-2-7B-like model compared with a GQA variant. Deliver a single HTML file.
