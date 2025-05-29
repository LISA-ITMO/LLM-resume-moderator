# LLM-resume-moderator

---

![License](https://img.shields.io/github/license/LISA-ITMO/LLM-resume-moderator?style=flat&logo=opensourceinitiative&logoColor=white&color=blue)
[![OSA-improved](https://img.shields.io/badge/improved%20by-OSA-yellow)](https://github.com/aimclub/OSA)

---

## Overview

This system automates the process of reviewing resumes to ensure they meet specific requirements, aiming to significantly reduce manual effort for organizations dealing with large volumes of applications. It acts as an intelligent filter, evaluating each resume against a set of defined rules and flagging potential issues. Utilizing powerful language models, it doesn't just look for keywords but understands the *meaning* within the resume content – assessing tone, relevant experience, and adherence to guidelines. The goal is to provide a structured assessment, clearly explaining why a resume passed or failed certain checks. 

A practical application demonstrated involves assisting the Saint Petersburg Committee on Labor and Employment in managing hundreds of daily resumes. Various techniques like sentiment analysis and similarity comparisons were tested to determine feasibility. Ultimately, it offers a way to streamline recruitment by quickly identifying suitable candidates while ensuring fairness and consistency in the screening process.

---

## Repository content

The LLM-resume-moderator repository aims to automate the process of reviewing resumes, specifically for organizations like the Saint Petersburg Committee on Labor and Employment. It achieves this through a combination of several key components working together.

The core is a FastAPI application that exposes an API endpoint for moderation requests. This API receives a resume, a set of rules, and a specified LLM model as input.

The 'manager' component orchestrates the actual moderation process. It leverages large language models (LLMs) to analyze resumes against predefined rules and determine if they meet certain criteria. The project utilizes several LLMs including T-it-1.0 and Llama Guard 3 8B, with T-pro-it-1.0 being used for semantic similarity and rule application.

The 'schemas' define the data structures used throughout the system – how resumes are represented, what rules look like, and the format of moderation responses including status and violated rules. Rules themselves are loaded from a JSON file ('resume_rules.json').

A separate model service is provided via a Dockerfile that runs llama-cpp-python with the t-lite-it-1.0-q8_0.gguf model, serving as an LLM endpoint.

The project utilizes Elasticsearch for data storage and potentially analysis, integrated through a docker-compose setup. Kibana provides a user interface for interacting with the Elasticsearch data.

The entire system is containerized using Docker and orchestrated with Docker Compose, defining how these components interact in a production environment. Environment variables are used to configure connections to external services like Elasticsearch and manage API keys.

---

## Used algorithms

The project utilizes several algorithms centered around Natural Language Processing (NLP) and Large Language Models (LLMs) to moderate resumes. 

**Sentiment Analysis:** This algorithm assesses the emotional tone of the resume text, identifying if it expresses overly positive or negative sentiments which might be flagged as unusual.

**Semantic Similarity Comparison:**  This determines how closely a candidate's experience, as described in their resume, matches the requirements of a specific job position. It essentially measures how 'relevant' the resume is to the role.

**Content Safety Classification:** This algorithm checks if the resume contains potentially harmful or inappropriate content based on predefined safety guidelines.

**Zero-Shot Moderation:**  This applies formal rules directly to the resume content using an LLM. It evaluates whether the resume adheres to specific requirements without needing prior training examples for those exact rules – it understands and applies them 'on the fly'.

The core of these algorithms relies on converting text into numerical representations (vector embeddings) and then calculating the similarity between these vectors, often using cosine distance, to quantify relevance or identify potential issues. The LLM itself acts as a reasoning engine applying the moderation rules.

---
