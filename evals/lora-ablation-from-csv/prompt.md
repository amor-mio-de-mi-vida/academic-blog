---
tags: [skill-creator]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch, WebSearch]
---

我做了一组 LoRA rank 的消融实验，结果在 lora_ablation.csv 里（Llama-3-8B，分别在 GSM8K 和 MBPP 上微调，rank 从 1 到 256，每个设置跑了 3 个 seed，另外还有全参数微调作为参照）。帮我写成一篇技术博客：先用图讲清楚 LoRA 的原理，再分析实验结果，给出选 rank 的建议。输出 HTML。

Input files: lora_ablation.csv
