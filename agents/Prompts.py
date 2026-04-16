
# ------------------------
# FEW-SHOT PROMPTS
# ------------------------
QUICK_FEWSHOT = """
EXAMPLE:

TOPIC: Cloud Computing

OUTPUT:
# Cloud Computing

## Key Points
- On-demand computing resources
- Scalable infrastructure
- Pay-as-you-go pricing

## Explanation
Cloud computing allows users to access servers over the internet.

---

Follow the same structure.
"""

DEEP_FEWSHOT = """
EXAMPLE:

TOPIC: Machine Learning

OUTPUT:
# Machine Learning

## Overview
Machine Learning enables systems to learn from data.

## Key Concepts
- Supervised Learning
- Unsupervised Learning

## Detailed Explanation
ML models identify patterns...

## Comparison Table

| Type | Description | Use Case |
|------|------------|----------|
| Supervised | Labeled data | Classification |
| Unsupervised | Pattern discovery | Clustering |

## Insights
- Data quality is critical

## Conclusion
ML is essential in AI.

---

Follow the same structure.
"""

ACADEMIC_FEWSHOT = """
EXAMPLE:

TOPIC: Natural Language Processing

OUTPUT:
# Natural Language Processing

## Abstract
This study explores NLP...

## Introduction
NLP studies human language...

## Methodology
Transformer models...

## Findings
High accuracy achieved...

## Discussion
Limitations exist...

## Conclusion
Future research is needed.

---

Follow the same structure.
"""


