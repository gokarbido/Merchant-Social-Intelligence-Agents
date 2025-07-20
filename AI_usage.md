# AI Usage in Merchant Social Network Agent Swarm

## Overview
This project leverages a variety of AI tools and techniques to build a modular, intelligent, and safe multi-agent system for merchant social networks. Below is a summary of how AI was used in both the codebase and the development process.

## LLMs (Large Language Models)
- **Ollama (llama3.2):** All core agents (router, matchmaker, moderator) use LLMs for classification, matchmaking, and moderation. Prompts are carefully designed to delegate decision-making to the LLM, removing hardcoded logic.
- **System Prompts:** Each agent is guided by a system prompt that defines its role and expected output, ensuring consistent and explainable behavior.

## Embeddings & Vector Search
- **Embeddings:** The system is ready to use vector embeddings (via PGVector, FAISS, ChromaDB) for semantic search and profile matching. This enables more relevant matchmaking and context-aware recommendations.
- **Vector Search:** FAISS and ChromaDB are integrated for fast, scalable similarity search, supporting future improvements in matchmaking and retrieval.

## Moderation
- **LLM-based Moderation:** The ModeratorAgent uses LLMs to classify and flag inappropriate, abusive, or low-quality content. This ensures responsible and safe interactions.
- **Escalation:** A Human Escalation Agent routes complex or high-risk cases to a human operator, ensuring that AI does not make critical decisions alone.

## Multi-Agent Orchestration
- **Pydantic-based Orchestrator:** Agents are orchestrated in a modular, testable way using Pydantic models, enabling clear workflows and easy extensibility.
- **Google ADK Integration:** The system is compatible with Google’s Agent Development Kit (ADK), allowing for advanced multi-agent workflows, memory, and deployment options.

## Feedback Loop
- **User Feedback:** The system collects thumbs-up/down feedback on agent responses, storing it for future learning and improvement.

## Testing & Evaluation
- **Pytest:** Automated tests simulate real user scenarios, verifying that agents route, moderate, and escalate as expected.
- **Scenario Coverage:** Tests ensure that the system is relevant, responsible, and robust.

## Development Process
- **AI-Assisted Coding:** LLMs (like ChatGPT, Claude) and coding assistant tools (like Cursor) were used to design, refactor, and document the codebase, ensuring best practices and rapid iteration.
- **Prompt Engineering:** Iterative prompt design was used to optimize agent behavior and output quality.

## Summary
AI is used throughout the system for decision-making, moderation, matchmaking, and orchestration, with human-in-the-loop escalation and feedback for safety and continuous improvement. 