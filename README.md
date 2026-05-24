# YoutubeThumbnail
```python
# Let's generate a highly polished, comprehensive, and clean Markdown (README.md) file for this project.
# We will use the explicit structure based on the code provided by the user.

md_content = """# Automated YouTube Thumbnail Generator & Critic

An intelligent, stateful agentic pipeline built with **LangGraph** that automatically generates, validates, and refines YouTube thumbnail concepts. It coordinates a critique-driven feedback loop between a prompt engineering LLM, an open-weights image generation engine, and a vision-capable validation agent to ensure your output thumbnails are vibrant, contextual, and high-impact.

---

## Key Features

- **Stateful Orchestration**: Powered by LangGraph to seamlessly manage execution flow, data states, and multi-actor iterations.
- **Master Designer Expansion**: Expands simple text entries into high-fidelity, high-contrast, professional visual layout instructions.
- **Automated Validation Loop**: A dedicated vision-critic agent evaluates the generated thumbnail layout criteria against strict art direction rules.
- **Configurable Fallbacks & Limits**: Prevents runaway execution or infinite looping using a strict retry-budget constraint system.

---

## System Architecture & Feedback Loop

The agent treats thumbnail creation as an iterative refinement loop rather than a single-shot generation. The workflow operates as follows:

1. **Refine Prompt (`refineprompt`)**: The user's basic video concept is transformed by a Master Designer prompt engineer agent (NVIDIA API) into a visually descriptive rendering prompt. It takes past artistic critique/feedback into account during retries.
2. **Generate Image (`imagegenerate`)**: The refined rendering prompt is handed off to the Hugging Face Inference API (`FLUX.1-schnell`) to generate the physical thumbnail image file.
3. **Image Validation (`imagevalidation`)**: A Senior Art Director validation agent inspects the file paths and composition against strict creative parameters (Luminance, Exposure, Contextual Props, English text readability).
4. **Approval Router**: A conditional routing gate evaluates the validation report:
   - If it **passes**, the workflow terminates (`END`) successfully.
   - If it **fails** and the retry threshold is not yet breached, the counter increments, and control routes back to step 1 along with structural feedback.
   - If the maximum attempts are exhausted, it exits cleanly (`END`) to avoid an infinite loop.

---

## Core Libraries Used

- **`langgraph`**: Orchestrates the multi-actor state machine framework, handling data persistence and conditional routing.
- **`openai`**: Leverages the official client library pointing to high-performance model infrastructure (e.g., hosted on NVIDIA NIM endpoints) for prompt building and visual critique.
- **`huggingface_hub`**: Utilizes the native `InferenceClient` wrapper to effortlessly pull down state-of-the-art open-weights image generation pipelines (`black-forest-labs/FLUX.1-schnell`).
- **`python-dotenv`**: Safely loads local environment context variables and API authorization keys (`NVIDIA_API_KEY`, `HF_TOKEN`).
- **`pillow` (PIL)**: Manages image processing, byte conversion, rendering formats, and localized disk persistence.

---

## Project Structure


```

```text
Markdown file generated successfully.

```text
├── .env                              # Secrets and infrastructure API tokens
├── thumbnail_generate_validate.py   # Core Graph workflow architecture and agent logic
└── tests.ipynb                       # Jupyter Notebook containing system demonstrations & execution examples

```

---

## Quick Start Guide

### 1. Prerequisites & Installation

Clone or enter your repository directory and install the necessary dependencies:

```bash
pip install langgraph openai huggingface_hub python-dotenv pillow ipython

```

### 2. Environment Configuration

Create a file named `.env` in the root folder of the workspace and include your valid platform credentials:

```ini
NVIDIA_API_KEY="nvapi-your-nvidia-integrated-token-goes-here"
HF_TOKEN="hf_your_huggingface_inference_token_goes-here"

```

### 3. Basic Execution

You can run the engine directly from a terminal execution script or import it into your custom applications:

```python
from thumbnail_generate_validate import YTThumbnail

# Initialize the state machine with your video topic
yt = YTThumbnail(user_prompt="mickey mouse rowing a boat")

# Execute the automated generation, validation, and correction loop
yt.generate_thumbnail()

```

### 4. Interactive Testing

For step-by-step validation, visual workflow graphs, and sample output inspections, launch your environment and open the interactive notebook:

```bash
jupyter notebook tests.ipynb

```

"""
