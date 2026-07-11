---
title: "How I Work: Backend, AI, DevOps, and Infrastructure"
date: 2026-07-08T00:30:00+08:00
description: How I connect Backend, LLM / Speech AI, DevOps, Cloud, On-prem Infrastructure, and Network Operations into one delivery chain.
menu:
  sidebar:
    name: How I Work
    identifier: technical-delivery-chain
    weight: 5
tags: ["Backend", "LLM", "Speech AI", "DevOps", "Infrastructure", "Network"]
categories: ["Portfolio", "Engineering"]
---

I do not treat Backend, AI, DevOps, Infrastructure, and Network as isolated areas. For a product that has to go online, be used, and remain maintainable, these layers eventually become one delivery chain.

Features need stable APIs. Services need reliable CI/CD. Long-running systems need monitoring, backup, network visibility, and security. When a product needs LLMs, Speech AI, or GPU runtime, model integration also has to be deployable, observable, and operable.

## What I Work On

### Backend / API

Backend is my core area. I work on API design, service integration, database access, existing system integration, and admin workflows. I use Node.js, Python, Go, PHP, C/C++, Shell Script, and Java depending on the existing architecture, maintainability, and runtime environment.

I care about whether an API is clear, whether data flow can be traced, whether errors can be diagnosed, and whether the system can still be maintained by the next person.

### LLM / Speech AI

Since 2022, I have worked on LLM and Speech AI in real product workflows. This is not just about calling a model API. It means connecting prompts, batch processing, local models, GPU runtime, OpenAI API, Ollama, Kaldi, Whisper, and existing backend workflows.

I prioritize control and operability: how inputs are prepared, how outputs are validated, how failures are retried, how cost is controlled, when to use local models or cloud APIs, and whether the runtime environment can be reproduced.

### DevOps / CI/CD

I maintain GitLab CI/CD, GitHub Actions, Jest tests, container image builds, deployment workflows, and release processes. The goal is to make releases repeatable and to know exactly which stage failed when something breaks.

For me, CI/CD is not only automated deployment. It is the connection between testing, builds, image registries, environment differences, rollback, and review workflows.

### Cloud / On-prem Infrastructure

I work across both cloud and on-prem environments. On the cloud side, that includes AWS CDK / IaC, AWS, GCP, Azure, and common service integrations. On-prem work includes Proxmox VE, Proxmox Backup Server, Harbor, GitLab, LDAP, LibreNMS, GPU servers, NAS, and backup planning.

This is also one reason I wrote [AWS CDK 完全學習手冊](https://clarence.tw/en/#publications): infrastructure should be describable, repeatable, and reviewable, instead of living only in one machine or one person's memory.

### Network / Security Operations

I also work on enterprise network and security operations, including switches, firewalls, VLAN, VPN, SD-WAN, QoS, Wi-Fi, site-to-site backup, monitoring, and basic security controls.

Network is often underestimated. In real operations, many application issues eventually come back to DNS, routing, firewall rules, latency, Wi-Fi, certificates, proxy behavior, or missing monitoring visibility. Being able to trace from application behavior down to the network layer matters.

## What This Site Should Communicate

This site is not just a list of technologies. I want it to show the kind of engineering work I am good at:

- Connecting Backend, AI, DevOps, and Infrastructure into deliverable systems.
- Writing applications while also handling deployment, runtime, monitoring, and network operations.
- Turning technical needs into implementations that can be operated, purchased, and handed over.
- Writing down lessons as articles, notes, or open-source projects.

If I had to summarize it in one sentence: I am the kind of engineer who can help bring a product from code to stable production operation.
