#  RegTech: On-Premise AML Transaction Monitoring & AI Agent System

##  Project Architecture & Regulatory Alignment
This is a production-grade RegTech prototype designed to align with the latest regulatory guidelines issued by the **Hong Kong Monetary Authority (HKMA)** and the **Securities and Futures Commission (SFC)** regarding Artificial Intelligence adoption in financial institutions. 

Unlike traditional "black-box" AI applications, this system addresses strict regulatory double-bottom lines via an advanced **Parallel Override Logic Matrix** and an air-gapped Generative AI workflow.

###  Compliance Core Pillars:
1. **High-Level Principles on AI (HKMA 2019):** Board and senior management retain ultimate accountability. The framework provides structured explainability matrices with zero "black-box" excuses.
2. **Human-in-the-Loop (SFC Dec 2024 Circular):** Strictly forbids automated case closures for high-risk flags. The LLM acts purely as an investigator co-pilot, generating JFIU-standard Suspicious Activity Report (SAR) narratives for MLRO review and final sign-off.
3. **Data Secrecy & Privacy Engineering (HK PDPO & GDPR):** Runs 100% locally via Ollama (Llama 3). Zero external network API requests are made, completely eliminating Protected Non-Public Information (PNI) data leakage or prompt injection threats via public clouds.

---

##  Decision Logic: Parallel Override Matrix
To mitigate **Model Under-detection (False Negatives)** and **Concept Drift**, the monitoring core evaluates transaction telemetry via a parallel dual-track validation system:

| Track A: Traditional Rule-Based | Track B: XGBoost ML Score | System Risk Tag | Operational Action Taken (HITL) |
| :--- | :--- | :--- | :--- |
| 🔴 **Hit** (Threshold Trigger) |  **High Score** (>= 0.80) | `🔴 Critical (Dual Hit)` | **Agentic Accelerator:** Triggers Local Llama 3 to auto-draft SAR narrative. Highest Priority. |
| 🔴 **Hit** (Threshold Trigger) |  **Low Score** (< 0.50) | `延 Medium (Rule Override)` | **Regulatory Safety Net:** Traditional rules override AI. Routed immediately to the human investigation queue. |
| ⚪ **No Hit** (Evaded Rules) |  **High Score** (>= 0.80) | `🟠 High (AI Flagged)` | **Smurfing Detection:** Captures structured/mule behaviors bypassing hard limits. Triggers SAR narrative. |
| ⚪ **No Hit** (Evaded Rules) |  **Low Score** (< 0.50) | `🟢 Low (Cleared)` | **Automated Disposition:** Archived and subjected to 1% randomized monthly QA backtesting sampling. |

---

##  Deployment & Local Demonstration ($0 Token Cost)

### 1. Environmental Setup
Ensure you have [Ollama](https://ollama.com/) running in your local background environment:
```bash
ollama run llama3