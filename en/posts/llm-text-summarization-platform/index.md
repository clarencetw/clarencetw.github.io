---
title: "Designing an LLM Summarization Pipeline: OpenAI API, Ollama, and Local Models"
url: "https://clarence.tw/en/posts/llm-text-summarization-platform/"
language: "en"
---

# Designing an LLM Summarization Pipeline: OpenAI API, Ollama, and Local Models

The principles and trade-offs I use when designing and operating an LLM text summarization pipeline, covering preprocessing and chunking, cloud API versus local models, batch processing, retries, cost control, and output validation.

Since 2022, I have been bringing LLMs into real product workflows. One part of that work is an internal text summarization and AI application platform that integrates the OpenAI API, Ollama, local models, and batch processing, with the focus on model usage that stays controllable and maintainable.

The details of an internal system like this are not suitable for publication, so this is not a full case study. Instead, it collects the principles and trade-offs I apply when designing and operating a summarization pipeline. API behavior described here was checked against the official documentation at the time of writing (October 2026); check the latest docs before relying on it.

## Why summarization is more than an API call

A summarization demo is quick to build: put the text in a prompt, ask the model to summarize it, and you have a result in minutes. The real work starts after the demo:

- Input length varies, and some texts exceed the model's context length.
- A batch contains many items, so you run into rate limits, timeouts, and partial failures.
- Downstream systems need a fixed format, but model output is not always shaped the same way.
- Cost, latency, and data sensitivity all affect which model each item should go to.
- After changing a model or a prompt, you need to know whether quality improved or regressed.

That is why I design summarization as a data processing pipeline rather than a single API call.

## Breaking down the pipeline

I split the flow into stages that can each be observed and re-run on their own:

1. **Preprocessing**: remove formatting noise, duplicated content, and fields the model does not need, and handle data that should not leave the environment at this step. Cleaner input makes both token usage and output quality easier to control.
2. **Chunking**: estimate the token count first. If the text exceeds what the model can handle, split it on paragraph or semantic boundaries, with a small overlap where needed so key points are not cut in half.
3. **Model calls**: summarize short texts directly. For long texts, use a map-reduce approach: summarize each chunk, then combine the chunk summaries into a final summary. Every call stays within a controlled input size, and a failure only requires re-running one chunk.
4. **Validation**: check output format, required fields, length, and obvious errors. Anything that fails is marked as failed or sent to retry.
5. **Output**: store the result together with the model used, the prompt version, and the processing status, so it can be traced and compared later.

With local models, pay close attention to context length. Ollama picks its default context length based on available VRAM; you can change it with `OLLAMA_CONTEXT_LENGTH` and confirm the actual allocation in the CONTEXT column of `ollama ps` ([Context length docs](https://docs.ollama.com/context-length)). If you do not check this setting, the model may not see all of a long text. I keep Ollama installation, commands, and environment variables in [Ollama Commands and Settings](https://clarence.tw/en/notes/llm/ollama-setup/).

### Structured output for downstream systems

When summaries are consumed by other systems, I ask the model for JSON and constrain the fields with a schema:

- OpenAI [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) in `strict` mode makes the output follow a supplied JSON Schema. JSON mode only guarantees valid JSON, not schema adherence. You still need to handle refusals and responses that are incomplete because they hit the output token limit.
- Ollama supports JSON schemas through the `format` parameter, and through `response_format` on its OpenAI-compatible API. The docs recommend also including the schema in the prompt and setting temperature to 0 for more consistent results ([Structured outputs docs](https://docs.ollama.com/capabilities/structured-outputs)).

A schema only guarantees the shape, not the content. Output that passes format validation can still miss key points or include things that are not in the source.

## Choosing between cloud APIs and local models

In my [post on Gemma 4 12B](https://blog.clarence.tw/2026/06/04/google-%e7%99%bc%e5%b8%83-gemma-4-12b%ef%bc%9alocal-ai-%e7%9a%84%e9%87%8d%e9%bb%9e%e4%b8%8d%e6%98%af%e5%8f%96%e4%bb%a3%e9%9b%b2%e7%ab%af%e6%a8%a1%e5%9e%8b%ef%bc%8c%e8%80%8c%e6%98%af%e8%a3%9c%e4%b8%8a/) (in Traditional Chinese), I argued that the point of local models is not to replace cloud models but to fill in a deployable middle tier. That is also my starting point when choosing models for summarization:

- **Cloud APIs** suit tasks that need stronger comprehension, longer context, or more complex instructions, and they spare you from maintaining GPUs and runtimes.
- **Local models** solve a different set of problems: whether the workload can run in a private environment, whether data can stay in your own environment, and whether inference cost and latency can be controlled.

In practice I do not rely on only one. A better approach is to let both plug into the same pipeline. Ollama provides an OpenAI-compatible API (by default at `http://localhost:11434/v1/` locally), so the same client code can switch by changing the base URL and model name ([OpenAI compatibility docs](https://docs.ollama.com/api/openai-compatibility)). Compatible does not mean identical, though. For example, context length cannot be set through the OpenAI-compatible API, so test each backend before switching.

When choosing, I look at data sensitivity, required quality, acceptable latency, overall cost, and how a quantized model actually performs on the available hardware. Benchmarks are only a reference; in the end you have to test with your own data.

## Batch processing, retries, and cost control

### Batch processing

For work that does not need immediate results, I use batch processing. The OpenAI [Batch API](https://developers.openai.com/api/docs/guides/batch) takes requests as a JSONL file, completes within 24 hours, costs 50% less than synchronous calls, and has its own rate limits. Output order may not match input order, so results must be matched back by each request's `custom_id`. Failed and expired requests go to a separate error file that needs its own handling.

Local models have no hosted batch service like this, so you control the pace yourself: limit concurrency so you do not exhaust GPU memory or overload the service.

### Retries

Retries need rules; they cannot resend forever. The OpenAI [rate limits guide](https://developers.openai.com/api/docs/guides/rate-limits) recommends:

- Wait according to `Retry-After` when it is present; otherwise use exponential backoff with jitter.
- Cap both the number of retries and the total wait time.
- Failed requests still count toward per-minute limits, so continuously resending makes recovery harder.
- The official SDKs retry some errors automatically, so avoid double-counting when you implement your own retries.
- Do not retry quota or billing errors.

I add one more principle: retry per chunk or per item, and make sure you can tell which parts already succeeded, so you never have to re-run a whole batch.

### Cost control

Most of the cost is decided at design time:

- Remove unnecessary content during preprocessing to cut input tokens.
- Set `max_tokens` close to the expected output length. OpenAI counts the larger of `max_tokens` and the estimated request tokens toward rate limits, so an oversized value wastes capacity.
- Send non-urgent work to the Batch API or to local models.
- Record the model and token usage for each call so you can see where the cost goes.

## Validating output quality

Summary quality is hard to judge with automation alone, so I use two layers:

- **Automated checks**: whether the schema passes, required fields exist, length is reasonable, and whether any output was refused or truncated. These are hard requirements; anything that fails does not move downstream.
- **Human spot checks**: regularly sample summaries and compare them with the source, looking for missed key points, distorted meaning, or content that is not in the source. Compare the same sample set before and after changing a model or prompt to know whether the change actually helped.

The OpenAI docs also note that structured output only guarantees format, and that you should build evaluations to confirm the content meets your needs. Keep the spot-check samples and results so they can be reused the next time you change models.

## What I learned

- **Design the pipeline first, then pick the model.** Once preprocessing, chunking, validation, and retries are in place, switching models becomes much cheaper.
- **Cloud and local are not an either-or choice.** Let both plug into the same pipeline, then decide per type of work based on data, quality, and cost.
- **Correct format is not correct content.** Schema validation catches format errors but not summaries that miss key points, so human spot checks cannot be skipped.
- **Traceability matters more than getting it right the first time.** Keep the model, prompt version, token usage, and processing status so you know where to start when something goes wrong.
