---
title: "Speech AI and GPU Runtime: Notes on Deploying and Operating Kaldi and Whisper"
date: 2026-10-26T00:00:00+08:00
description: How I approach Speech AI and GPU runtime work, covering the trade-offs between Kaldi and Whisper, the NVIDIA driver / CUDA / container layers, and what I check during deployment and performance maintenance.
menu:
  sidebar:
    name: Speech AI and GPU Runtime
    identifier: speech-ai-gpu-runtime
    weight: 55
tags: ["Speech AI", "Kaldi", "Whisper", "GPU", "CUDA", "Infrastructure"]
categories: ["Portfolio", "Engineering"]
---

Since 2022, part of my work has been bringing speech recognition technologies such as Kaldi and Whisper, together with GPU runtime, into real systems. That covers model inference, system deployment, and the performance maintenance that follows.

This is not a full case study of a specific project, and it does not include internal architecture, data, or performance numbers. Instead, it describes how I approach this kind of work: how I think about the differences between Kaldi and Whisper, why I stabilize the GPU runtime first, and what I check after deployment. Technical details follow the official documentation, and the troubleshooting lessons come from articles I have published on [blog.clarence.tw](https://blog.clarence.tw/) (written in Chinese).

## Where Speech AI Fits in a Product

As I wrote in [How I Work]({{< relref "/posts/technical-delivery-chain" >}}), LLM and Speech AI work is not just calling a model API. It has to connect with batch processing, local models, GPU runtime, and existing backend workflows.

Speech recognition is usually one stage of a larger flow. Typically, audio is captured, converted, and segmented before recognition; afterwards, the text is post-processed, stored, searched, or passed on to other services. So when I evaluate a Speech AI component, I look beyond the recognition result itself:

- Is the input audio consistent in format and quality, and which layer owns preprocessing?
- Is recognition streaming or batch, and how are failures retried?
- How is the model output validated, and when does a person need to review it?
- Can this runtime be rebuilt on another machine?

I learned early on that the same tool can behave very differently on different content. In 2019, when Amazon Transcribe added Simplified Chinese, I [tried it and wrote up my impressions](https://blog.clarence.tw/2019/08/25/amazon-transcribe-supports-simplified-chinese-using-teaching-and-experience/). A song gave poor results, while a conversation-heavy video worked much better. Whether you use a managed service or a self-hosted model, you need to judge it with audio close to your real use case.

## Kaldi and Whisper: Characteristics and Trade-offs

I use both Kaldi and Whisper in my work. I do not see one as a replacement for the other; they are tools built on very different design ideas.

### Kaldi

According to the [Kaldi documentation](https://kaldi-asr.org/doc/about.html), Kaldi is a speech recognition toolkit written in C++ and licensed under the Apache License v2.0, intended for speech recognition researchers. Its main characteristics include:

- Finite state transducers (FSTs) at its core, built on OpenFst. The classic decoding graph is [HCLG](https://kaldi-asr.org/doc/graph.html), composed from the HMM definitions, context dependency, lexicon, and grammar / language model.
- Recipes for many datasets, covering data preparation, training, and decoding.
- A library for [online decoding](https://kaldi-asr.org/doc/online_decoding.html), plus a batched CUDA decoding implementation under `src/cudadecoder`.

From an operations perspective, Kaldi's strength is its fine-grained components: the lexicon, language model, and acoustic model can each be adjusted. The cost is a long build process, a lot of required speech expertise, and an environment that breaks easily when compiler flags or dependencies differ.

### Whisper

According to [openai/whisper](https://github.com/openai/whisper), Whisper is a general-purpose speech recognition model based on a Transformer sequence-to-sequence architecture, trained on a large and diverse audio dataset. It supports multilingual transcription, translation into English, and language identification. The code and model weights are released under the MIT License.

Points that matter for deployment:

- The model comes in tiny, base, small, medium, large, and turbo sizes. The official VRAM requirements range from roughly 1 GB to 10 GB, and speed varies widely, so model choice has to be made together with GPU capacity.
- It requires `ffmpeg`, and `transcribe()` processes the whole file with a 30-second sliding window.
- turbo is an optimized version of large-v3. It is fast but not trained for translation, so translation needs a multilingual model.
- The official [model card](https://github.com/openai/whisper/blob/main/model-card.md) warns that the model may produce text that was not spoken (hallucination), may repeat itself, and performs unevenly across languages, accents, and dialects. It also recommends against use in high-risk decision-making contexts.

### How I Choose

| Aspect | Kaldi | Whisper |
| :-- | :-- | :-- |
| Design | A pipeline of components (acoustic model, lexicon, language model, FST decoding) | An end-to-end Transformer model |
| Learning curve | High; you need to understand recipes and the build process | Low; install the package and start transcribing |
| Adjustability | Vocabulary, language model, and other components can be tuned separately | Mostly through model size, decoding options, and pre/post-processing |
| Multilingual | Depends on training data and recipe | Built-in multilingual transcription, translation into English, and language ID |
| Watch out for | Build environment, dependencies, model and graph versioning | VRAM, long audio, hallucination, and repetition |

My rule is simple: compare with audio close to the real use case first, then weigh deployment and maintenance cost, rather than relying only on public benchmarks.

### My Public Contribution to Kaldi

My public contribution to Kaldi is a small fix: [kaldi-asr/kaldi#4657](https://github.com/kaldi-asr/kaldi/pull/4657), merged in December 2021. Opening Kaldi in Gitpod failed because the configuration referenced `.gitpod.dockerfile`, while the actual file was `.gitpod.Dockerfile`. The PR fixed the filename, removed a non-existent user and an unused path from the Dockerfile, and pinned the Intel MKL package version.

The change was small, but it reflects something I care about with tools like this: development and runtime environments should be reproducible by someone else.

## Stabilize the GPU Runtime First: Driver, CUDA, Container

Whether you use Kaldi or Whisper, once a GPU is involved there is a whole runtime stack beneath the model. I split it into layers and troubleshoot in this order:

1. **Hardware and firmware settings**: Is the GPU detected, and is Secure Boot enabled?
2. **Kernel and NVIDIA kernel module**: Is the module built for the running kernel, and is it allowed to load?
3. **NVIDIA driver**: Does `nvidia-smi` respond?
4. **CUDA and libraries**: Are the CUDA runtime, cuDNN, and similar libraries compatible with the driver and framework?
5. **Container runtime**: Can containers see the GPU?
6. **Application and model**: PyTorch, the Kaldi build, and the model files themselves.

### Driver and CUDA Versions

According to NVIDIA's [CUDA Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/index.html) documentation, the driver and CUDA toolkit can be upgraded on separate schedules. Starting with CUDA 11, [minor version compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html) lets an application built within one major release family run on any driver at or above a minimum version (for example, 525 or newer for CUDA 12.x and 450 or newer for CUDA 11.x). Some features that need a newer driver are limited, and applications that compile device code to PTX for JIT are not covered.

In practice, this means deciding on the driver version first and then deciding which CUDA versions can run on top of it, instead of touching the driver every time a framework is upgraded.

### Isolate CUDA and Frameworks with Containers

The [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) requires the NVIDIA driver to be installed on the host. For Docker, after installing the packages, run:

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

`nvidia-ctk` modifies `/etc/docker/daemon.json` on the host, so this step belongs in configuration management. Then use the official [sample workload](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/sample-workload.html) to confirm containers can see the GPU:

```bash
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

With this split, the host is mainly responsible for the driver and the container toolkit, while CUDA, cuDNN, and frameworks travel with the image. Different services can use different CUDA versions, and upgrades or rollbacks become a matter of switching images instead of repeatedly installing and removing packages on the host.

### Problems I Have Documented

These are GPU environment issues I have written about publicly (articles in Chinese). They did not necessarily happen in the same environment, but together they show why the runtime should be managed in layers:

| Symptom | Cause and fix | Lesson |
| :-- | :-- | :-- |
| [nvidia-smi cannot communicate with the driver](https://blog.clarence.tw/2023/07/14/%e8%a7%a3%e6%b1%ba-ubuntu-%e4%b8%ad-nvidia-gpu-%e9%a9%85%e5%8b%95%e5%95%8f%e9%a1%8c/) | The driver module was not rebuilt after a kernel update; rebuild it for the new kernel with DKMS | A kernel update is also a GPU environment change |
| [Driver fails to load under Secure Boot](https://blog.clarence.tw/2026/01/31/%e8%a7%a3%e6%b1%ba-ubuntu-24-04-secure-boot-%e7%92%b0%e5%a2%83%e4%b8%8b-nvidia-%e9%a9%85%e5%8b%95%e7%84%a1%e6%b3%95%e8%bc%89%e5%85%a5%e5%95%8f%e9%a1%8c/) | The locally built DKMS module was unsigned and rejected; switch to Ubuntu's pre-signed `linux-modules-nvidia-*` packages | You do not need to disable Secure Boot for the driver |
| [nvidia-smi reports No devices were found](https://blog.clarence.tw/2024/02/19/%e8%a7%a3%e6%b1%ba-nvidia-linux-%e4%bd%bf%e7%94%a8-nvidia-smi-%e5%87%ba%e7%8f%be-no-devices-were-found-%e5%95%8f%e9%a1%8c/) | The packaged driver could not initialize the GPU; reinstall with NVIDIA's official installer and resolve the kernel / GCC version mismatch | When installation fails, read the kernel log and installer log first |
| [CUDA package dependencies cannot be installed](https://blog.clarence.tw/2022/05/31/%e5%ae%89%e8%a3%9d-cuda-%e5%87%ba%e7%8f%be-depends-cuda-11-7-11-7-0-but-it-is-not-going-to-be-installed-%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/) | The graphical session holds the driver; switch to `multi-user.target` before removing and reinstalling | Driver updates need a maintenance window |
| [dpkg file overwrite error](https://blog.clarence.tw/2023/07/14/%e5%9c%a8-ubuntu-%e7%99%bc%e7%94%9f-dpkg-error-processing-archive-%e7%9a%84%e5%95%8f%e9%a1%8c%e8%a9%b2%e5%a6%82%e4%bd%95%e8%99%95%e7%90%86%ef%bc%9f/) | Different versions of NVIDIA packages try to overwrite the same file | Keep driver package sources consistent on each machine |
| [NO_PUBKEY on a DGX system](https://blog.clarence.tw/2023/03/04/dgx-%e7%b3%bb%e7%b5%b1-ubuntu-18-04-%e5%87%ba%e7%8f%be-no_pubkey-a4b469963bf863cc-%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/) | The NVIDIA CUDA repository changed its signing key; updating the key fixed it | External repositories change too; read the update error first |
| [cuDNN verification sample fails to build](https://blog.clarence.tw/2022/06/01/%e5%ae%89%e8%a3%9d-cuda-deep-neural-network-cudnn-%e9%81%87%e5%88%b0-test-c110-fatal-error-freeimage-h-no-such-file-or-directory-%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/) | The sample needs the extra FreeImage library | Verification steps have dependencies of their own |

Two more posts, on [CUDA Toolkit 11.7 installation methods](https://blog.clarence.tw/2022/05/31/%e5%ae%89%e8%a3%9d-cuda-toolkit-11-7/) (deb local, deb network, runfile) and [selecting a GPU in darknet](https://blog.clarence.tw/2021/10/24/yolo-alexeyab-darknet-set-gpu-number/) (`CUDA_VISIBLE_DEVICES` versus framework-level settings), cover basics I still return to when planning a GPU environment.

## Deployment and Performance Maintenance Checklist

These are general checks; the details depend on the environment.

### Before Deployment

- Record the full version set: OS, kernel, NVIDIA driver, CUDA, cuDNN, framework, model version, and image tag.
- Check the Secure Boot state (`mokutil --sb-state`) and decide whether to use pre-signed kernel modules or sign them yourself.
- Decide on an update policy for the kernel and driver so automatic updates do not change the GPU environment unnoticed.
- Estimate VRAM from model size and expected concurrency, then decide how many processes run on each GPU and how to assign them with `CUDA_VISIBLE_DEVICES`.

### After Deployment

- Host: confirm the module is loaded with `lsmod | grep nvidia` and that `nvidia-smi` responds.
- Container: run the sample workload to confirm containers can see the GPU.
- Application: run the full flow on a short, fixed test clip and confirm the output format and content make sense.
- Reboot and verify again so the driver and services recover on their own.

### Day-to-Day Monitoring

- Track GPU utilization and memory with commands such as `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv`, or feed them into monitoring.
- Watch processing time and queue length to tell whether the bottleneck is GPU capacity, slow preprocessing, or I/O.
- Look for abnormal recognition output, such as heavy repetition or text that clearly is not in the audio.

### Risky Operations

- `apt purge nvidia*`, switching to `multi-user.target`, and removing or replacing kernel modules all interrupt GPU services. Schedule them in a maintenance window and confirm a recovery path first.
- `nvidia-ctk runtime configure` rewrites the Docker daemon configuration, so review it together with existing settings.
- Do not disable Secure Boot just for convenience; if it is truly necessary, assess the security impact first.

## What I Learned

- **The model is only one layer.** Whether Speech AI runs reliably over time depends heavily on how well the driver, kernel, CUDA, and container layers are managed.
- **Keep the driver on the host and everything else in the image.** With CUDA and frameworks in containers, upgrades and rollbacks become much simpler.
- **Validate with your own use case.** Kaldi and Whisper each have trade-offs. Public benchmarks are only a reference; the final comparison should use audio close to the real scenario.
- **Write down the problems you hit.** Every GPU issue I documented on my blog later became an item on my deployment checklists.
