# arkterm
Wire an LLM Directly into Your Linux Terminal

![ArkTerm Demo Gif](https://saadman.dev/assets/images/blog/term.gif)

## Groq API Key

Navigate to [Groq](https://groq.com/) (not Grok), register for their service, and obtain a free API key from their developer portal. Groq offers production-ready models such as `gemma2-9b-it`, `meta-llama/Llama-Guard-4-12B`, `llama-3.1-8b-instant` and more at no cost, though API rate limits and context token window restrictions apply. A comprehensive list of their [supported models is provided](https://console.groq.com/docs/models).

## Usage 
```shell
$ git clone https://github.com/saadmanrafat/arkterm.git
$ cd arkterm
$ uv pip install -e .
$ arkterm
```

