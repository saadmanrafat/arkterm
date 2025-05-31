# arkterm
Wire an LLM Directly into Your Linux Terminal

![ArkTerm Demo Gif](https://saadman.dev/assets/images/blog/arkterm.gif)

# Installation 
```shell
$ git clone https://github.com/saadmanrafat/arkterm.git
$ cd arkterm
$ uv pip install -e .
$ arkterm
```

## Setup
```bash
# Create configuration file
arkterm --setup
```

This creates a YAML configuration file at `~/.aiterm/config.yaml`:

```yaml
API:
  api_key: "YOUR_GROQ_API_KEY_HERE"
  model: "deepseek-r1-distill-llama-70b"
  api_base: "https://api.groq.com/openai/v1"

SETTINGS:
  allow_command_execution: false
  max_tokens: 2048
```

## Groq API Key

Navigate to [Groq](https://groq.com/) (not Grok), register for their service, and obtain a free API key from their developer portal. Groq offers production-ready models such as `gemma2-9b-it`, `meta-llama/Llama-Guard-4-12B`, `llama-3.1-8b-instant` and more at no cost, though API rate limits and context token window restrictions apply. A comprehensive list of their [supported models is provided](https://console.groq.com/docs/models).


Add your Groq API key and you're ready to go!



