# E-Commerce Recommendation System

A full-stack intelligent recommendation engine that combines **Selenium web scraping**, **user behavior tracking**, **vector embeddings**, and a **hybrid recommendation algorithm** to deliver personalized product suggestions at scale.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Pipeline Breakdown](#pipeline-breakdown)
  - [1. Data Collection & Scraping](#1-data-collection--scraping)
  - [2. User Interaction Tracking](#2-user-interaction-tracking)
  - [3. Vector Embeddings with Qdrant](#3-vector-embeddings-with-qdrant)
  - [4. Hybrid Recommendation Engine](#4-hybrid-recommendation-engine)

---

## Overview

This project is an end-to-end recommendation system built for e-commerce platforms. It ingests real product data through Selenium-based web scraping, tracks rich user interaction signals, stores dense vector embeddings in Qdrant, and serves personalized recommendations through a **FastAPI** backend using a hybrid approach combining **Content-Based Filtering** and **Collaborative Filtering (ALS)**.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          Data Layer                              │
│                                                                  │
│  [Selenium Scraper] ──► [MongoDB: Product] ◄── [Event Tracker]  │
│     6000+ Products                               [MongoDB: Event]│
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Embedding Layer                            │
│                                                                  │
│         [Sentence Transformer] ──► [Qdrant Vector DB]            │
│           Product content encoding   + Metadata payload          │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                  Hybrid Recommendation Engine                    │
│                                                                  │
│   [Content-Based Filtering] + [Collaborative Filtering (ALS)]    │
│                          ↓                                       │
│               Personalized Recommendations                       │
│                          ↓                                       │
│                   [FastAPI Backend]                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Features

- **Large-scale product scraping** — 6,000+ products scraped with Selenium and stored in MongoDB
- **Multi-signal interaction tracking** — product opens, add-to-cart, exits, duration, and timestamps stored in MongoDB
- **Vector search** — product content encoded and stored in Qdrant with full metadata payload
- **Implicit ALS Collaborative Filtering** — matrix factorization on implicit user feedback
- **Hybrid recommendations** — combines content-based cosine similarity with collaborative signals
- **FastAPI backend** — clean REST API for serving recommendations

---

## Tech Stack

| Component | Technology |
|---|---|
| Web Scraping | Python, Selenium |
| Product & Event Storage | MongoDB |
| Vector Search | Qdrant |
| Collaborative Filtering | `implicit` library — ALS |
| Backend | Python, FastAPI |

---

## Pipeline Breakdown

### 1. Data Collection & Scraping

Over **6,000 products** were scraped using **Selenium**. Each product is stored in the **`Product`** MongoDB collection, capturing the product name/description as a `content` field for embedding, alongside structured metadata including `product_id`, `category`, `stock`, `price`, and `product_link`.

---

### 2. User Interaction Tracking

User behavior is captured across multiple event types and stored in the **`Event`** MongoDB collection. Each document records a single user action on a product:

| Event Type | Description |
|---|---|
| `product_open` | User opened the product detail page |
| `add_to_cart` | User added the product to cart |
| `product_exit` | User left the product page |
| `duration` | Time (seconds) spent on the product page (attached to `product_exit`) |
| `timestamp` | ISO 8601 UTC timestamp of the event |

These signals are aggregated per user–product pair to form the **implicit feedback matrix** used by the ALS model.

---

### 3. Vector Embeddings with Qdrant

Product `content` fields are encoded into dense vectors using a **Sentence Transformer** model. The resulting embeddings are stored in **Qdrant** alongside the full metadata payload from MongoDB.

Each Qdrant point contains:
- **Vector** — dense embedding of the product `content`
- **Payload** — `product_id`, `category`, `stock`, `price`, `product_link`

This enables **content-based retrieval** by computing **cosine similarity** between a query product's vector and all stored product vectors.

---

### 4. Hybrid Recommendation Engine

The system combines two complementary approaches:

**Content-Based Filtering**
- Retrieves the embeddings of products a user has interacted with from Qdrant
- Computes cosine similarity against all product vectors
- Returns the most similar products ranked by similarity score

**Collaborative Filtering — Implicit ALS (Alternating Least Squares)**
- Aggregates user–product interaction events into a weighted implicit feedback matrix (e.g., `product_open` = 1, `add_to_cart` = 3)
- Trains an ALS model from the `implicit` library to learn latent user and item factors
- Generates candidate product recommendations based on learned user preferences

The **FastAPI** backend exposes endpoints that query both models and return a merged, ranked list of personalized recommendations for each user.

---

## Author

**Mourad Adel**  
[GitHub](https://github.com/Mouradadel1919)

