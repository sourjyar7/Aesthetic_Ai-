# Aesthetic --- Conversational Visual Shopping

## Product & Engineering Specification

### Version 1.0 --- Implementation specification for an autonomous coding agent

------------------------------------------------------------------------

## 0. Mission

Build a polished, browser-based AI shopping assistant for a single
controlled vertical: **flooring**.

The product should let a user describe the flooring they want using
natural language, optionally upload an inspiration image, refine
preferences conversationally, and receive visually and semantically
relevant product recommendations.

The initial product must use a **controlled synthetic/curated flooring
catalog** rather than depending on Amazon, Flipkart, or other external
e-commerce sites.

The architecture must be designed so the same system can later expand to
furniture, fashion, electronics, and eventually a browser extension that
can sit on top of external e-commerce websites.

The product is both:

1.  A real, usable consumer-facing demo.
2.  A serious AI engineering portfolio project demonstrating multimodal
    retrieval, hybrid search, reranking, conversational preference
    extraction, agentic behavior, evaluation, and production-oriented
    backend engineering.

------------------------------------------------------------------------

# 1. Product Vision

### Product promise

> **Describe what you want. Show us what you like. We'll find it.**

Traditional e-commerce requires users to manually navigate:

-   categories
-   filters
-   sorting
-   product pages
-   comparison pages

This product replaces much of that interaction with conversational
discovery.

Example:

> "I want a warm-looking wooden floor for my living room. Something
> light oak, not too glossy, modern and Scandinavian. My budget is
> around ₹200--250 per square foot."

The system should understand:

-   product category
-   visual style
-   color
-   finish
-   room/use case
-   budget
-   aesthetic preferences
-   negative preferences

It should then retrieve and rank suitable flooring products and explain
why they were selected.

------------------------------------------------------------------------

# 2. MVP Scope

## 2.1 In scope

### User interaction

-   Text-based conversational input.
-   Optional image upload as visual inspiration.
-   Conversational refinement.
-   Product recommendation cards.
-   Product comparison.
-   Recommendation explanations.
-   Explicit preference changes.
-   Basic voice input if technically practical after the text/image MVP
    is stable.

### AI

-   Natural-language intent extraction.
-   Shared image/text multimodal embeddings.
-   Vector similarity search.
-   Metadata filtering.
-   Hybrid retrieval.
-   Candidate reranking.
-   Conversational preference state.
-   Recommendation explanation.
-   Context-aware follow-up questions.

### Product catalog

-   Controlled flooring catalog.
-   Product images.
-   Product metadata.
-   Embeddings.
-   Searchable structured fields.

### Evaluation

-   Retrieval benchmark.
-   Recommendation benchmark.
-   Recall@K.
-   Precision@K where appropriate.
-   NDCG@K.
-   Constraint satisfaction rate.
-   Human- or LLM-assisted relevance judgments.
-   Latency and cost tracking.

### Portfolio presentation

-   Polished landing page.
-   Live playground.
-   Architecture explanation.
-   Retrieval visualization.
-   Evaluation dashboard.
-   GitHub repository.
-   Technical case study.

------------------------------------------------------------------------

# 3. Explicitly Out of Scope for MVP

Do NOT build these initially:

-   Amazon integration.
-   Flipkart integration.
-   General-purpose web scraping.
-   Real checkout.
-   Payments.
-   Real user accounts.
-   Real customer purchases.
-   General-purpose autonomous shopping across the web.
-   Browser extension.
-   Mobile app.
-   Full voice agent.
-   Arbitrary product categories.
-   Fully autonomous purchasing.
-   Unrestricted browser/computer control.

These are future roadmap items.

The first objective is to prove the core product:

> **Natural-language + image preference → high-quality flooring
> recommendations.**

------------------------------------------------------------------------

# 4. Target User Experience

## 4.1 Landing page

The landing page should immediately communicate the product.

Headline:

> **Find the floor you're imagining.**

Subheadline:

> Describe the style you want or upload an inspiration image. Our AI
> will find flooring that matches your taste, budget, and requirements.

Primary actions:

-   `Describe what I want`
-   `Upload inspiration`

Do not lead with technical terminology.

The portfolio visitor should be able to understand and use the product
within 30 seconds.

------------------------------------------------------------------------

# 5. Core User Flow

## Step 1 --- User describes intent

Example:

> "I want something warm and modern for my living room. Light oak,
> matte, Scandinavian style, under ₹250 per square foot."

System extracts structured requirements.

Example internal representation:

``` json
{
  "category": "flooring",
  "room": "living_room",
  "style": ["modern", "scandinavian", "warm"],
  "material": ["wood", "wood_look"],
  "color": ["light_oak"],
  "finish": "matte",
  "budget": {
    "max_price_per_sqft": 250,
    "currency": "INR"
  },
  "negative_preferences": []
}
```

------------------------------------------------------------------------

## Step 2 --- System decides whether clarification is necessary

Do not ask unnecessary questions.

If enough information exists, search immediately.

If an important constraint is missing, ask one concise question.

Example:

> "What's your approximate budget per square foot?"

Avoid interrogating the user with a long form.

------------------------------------------------------------------------

## Step 3 --- Retrieve candidate products

The retrieval system should combine:

1.  Text-to-image semantic retrieval.
2.  Structured metadata filtering.
3.  Optional image similarity.
4.  Candidate reranking.

------------------------------------------------------------------------

## Step 4 --- Generate recommendations

Return 3--6 strong recommendations.

Each recommendation should show:

-   image
-   product name
-   price per square foot
-   material
-   finish
-   style
-   similarity/relevance indicator
-   why it matches
-   possible trade-offs

------------------------------------------------------------------------

## Step 5 --- Conversational refinement

User can say:

> "I like #2 but it's too dark."

System should update preference state:

``` json
{
  "color": {
    "preferred": ["light", "light_oak"],
    "avoid": ["dark"]
  }
}
```

Then rerun retrieval.

------------------------------------------------------------------------

# 6. Inspiration Image Flow

The user may upload an image of:

-   a room
-   a floor
-   an interior
-   a Pinterest-style inspiration
-   another product

The system should use the image as a visual query.

Flow:

``` text
Uploaded image
      |
      v
Image encoder
      |
      v
Image embedding
      |
      v
Vector search
      |
      v
Candidate products
```

If the user also provides text:

> "Find something like this, but lighter and less glossy."

combine:

-   image embedding
-   text embedding
-   structured constraints

------------------------------------------------------------------------

# 7. Multimodal Embedding Architecture

## Critical requirement

The image and text embeddings used for semantic retrieval MUST come from
a model that places both modalities into a shared embedding space.

Do NOT independently embed:

-   images with an arbitrary image encoder
-   text with an unrelated text embedding model

and assume their vectors are directly comparable.

Use a CLIP-style or equivalent vision-language embedding model.

Candidate implementation:

-   OpenCLIP
-   Hugging Face CLIP-compatible models
-   another open multimodal model with a shared image/text embedding
    space

The exact model should be configurable.

------------------------------------------------------------------------

# 8. Embedding Pipeline

## Catalog ingestion

For every product:

``` text
Product
  |
  +-- image
  +-- title
  +-- description
  +-- metadata
  |
  v
Image encoder
  |
  v
image_embedding
  |
  v
Vector database
```

The catalog record should contain:

``` json
{
  "product_id": "floor_000123",
  "name": "Nordic Oak Matte",
  "image_url": "...",
  "price_per_sqft": 229,
  "currency": "INR",
  "material": "engineered_wood",
  "color_family": "light_oak",
  "finish": "matte",
  "style": ["scandinavian", "modern"],
  "room_types": ["living_room", "bedroom"],
  "brand": "Example Brand",
  "availability": true,
  "image_embedding": []
}
```

------------------------------------------------------------------------

# 9. Query Representation

A user request should produce three representations.

## 9.1 Semantic text query

Example:

``` text
warm modern Scandinavian light oak matte flooring for a living room
```

This is embedded into the shared multimodal embedding space.

## 9.2 Structured constraints

Example:

``` json
{
  "room": "living_room",
  "max_price_per_sqft": 250,
  "finish": "matte"
}
```

## 9.3 Optional visual query

If an image is provided:

``` text
image -> multimodal image embedding
```

------------------------------------------------------------------------

# 10. Hybrid Retrieval

Do not rely purely on vector similarity.

Use:

``` text
                 USER QUERY
                     |
          +----------+----------+
          |                     |
          v                     v
   Semantic query          Hard constraints
          |                     |
          v                     v
    Vector search          Metadata filter
          |                     |
          +----------+----------+
                     |
                     v
                Candidates
                     |
                     v
                 Reranker
                     |
                     v
              Final results
```

## Hard constraints

Examples:

-   price
-   availability
-   room
-   product category
-   material where explicitly required

## Soft preferences

Examples:

-   warm
-   elegant
-   Scandinavian
-   minimal
-   luxurious
-   cozy
-   natural
-   modern

These should influence ranking rather than always becoming strict
filters.

------------------------------------------------------------------------

# 11. Multimodal Query Fusion

When both image and text are present, support configurable fusion.

Initial implementation:

``` text
query_embedding =
    normalize(
        alpha * text_embedding +
        beta  * image_embedding
    )
```

Where:

-   `alpha` = text weight
-   `beta` = image weight
-   `alpha + beta = 1`

Make these configurable.

Example:

``` text
text_weight = 0.45
image_weight = 0.55
```

Later experiments can determine the optimal weights.

Do not hard-code these values throughout the codebase.

------------------------------------------------------------------------

# 12. Reranking

The first retrieval stage should return a larger candidate pool,
e.g. 30--100 products.

Then rerank candidates using:

-   semantic similarity
-   metadata match
-   budget match
-   room compatibility
-   style match
-   negative preference penalties

Example conceptual score:

``` text
final_score =
    0.45 * semantic_score
  + 0.20 * style_score
  + 0.15 * constraint_score
  + 0.10 * room_score
  + 0.10 * price_score
  - negative_preference_penalty
```

The scoring system must be configurable.

Do not pretend this formula is scientifically optimal. It is an initial
ranking baseline that will later be evaluated.

------------------------------------------------------------------------

# 13. Recommendation Explanation

Every recommendation should have a generated explanation grounded in
actual product metadata and retrieved evidence.

Example:

> **Why this matches**
>
> -   Similar light-oak appearance to your reference.
> -   Matte finish matches your preference.
> -   Suitable for living rooms.
> -   ₹229/sq ft, within your ₹200--250 budget.

Avoid unsupported claims.

The LLM must not invent:

-   materials
-   certifications
-   durability
-   availability
-   dimensions
-   pricing
-   compatibility

Only use catalog fields and explicitly retrieved information.

------------------------------------------------------------------------

# 14. Conversational Agent

The assistant should NOT behave as an unrestricted autonomous agent.

It should have a narrow purpose:

> Understand shopping intent, gather missing preferences, retrieve
> products, rank products, explain recommendations, and refine
> recommendations based on feedback.

Recommended tools/functions:

``` text
search_products()
filter_products()
get_product()
compare_products()
get_user_preferences()
update_user_preferences()
recommend_products()
```

Do not allow arbitrary tool execution in MVP.

------------------------------------------------------------------------

# 15. Preference Memory

Maintain short-lived session preference state.

Example:

``` json
{
  "preferred": {
    "colors": ["light oak"],
    "styles": ["modern", "scandinavian"],
    "finish": ["matte"]
  },
  "constraints": {
    "max_price_per_sqft": 250,
    "room": "living_room"
  },
  "avoid": {
    "colors": ["dark brown"],
    "finish": ["high_gloss"]
  }
}
```

The system should distinguish:

-   explicit user constraints
-   inferred preferences
-   temporary conversational preferences

Do not build long-term personal memory in MVP.

------------------------------------------------------------------------

# 16. Product Comparison

Users should be able to select products and ask:

> "What's the difference?"

Comparison should produce a structured table:

  Attribute   Product A         Product B
  ----------- ----------------- -------------
  Price       ₹229/sq ft        ₹245/sq ft
  Material    Engineered wood   Laminate
  Finish      Matte             Satin
  Style       Scandinavian      Modern
  Color       Light oak         Natural oak

Then provide a concise recommendation relative to the user's stated
preferences.

Do not create an unsupported "best product" claim.

Instead:

> "Given your preference for matte finish and a ₹250 budget, Product A
> matches more of your stated requirements."

------------------------------------------------------------------------

# 17. Cross-Selling

Cross-selling is a later MVP enhancement after core retrieval works.

Example:

User selects flooring.

System may recommend:

-   rugs
-   underlay
-   floor cleaner
-   furniture
-   lighting

But recommendations must be contextually justified.

Bad:

> "People also bought this."

Better:

> "Because you selected a light oak floor for a Scandinavian-style room,
> this neutral rug is visually compatible with the style you described."

Cross-selling should be treated as a separate ranking task.

------------------------------------------------------------------------

# 18. Voice

Voice input is desirable but NOT a blocker for MVP.

Phase 1:

-   text
-   image

Phase 2:

-   browser microphone input
-   speech-to-text
-   feed transcript into the same conversational pipeline

The core agent should remain modality-agnostic:

``` text
Text
Image
Voice transcript
      |
      v
Intent / preference representation
      |
      v
Same retrieval pipeline
```

Do not build a separate voice-specific recommendation architecture.

------------------------------------------------------------------------

# 19. Frontend UX

Recommended stack:

-   Next.js
-   TypeScript
-   React
-   Tailwind CSS
-   component library if useful

Primary screens:

## Home

Minimal, visually polished.

## Shopping Assistant

Chat + product results.

## Product detail

Product information + recommendation explanation.

## Compare

Side-by-side comparison.

## How it works

Visual explanation of:

``` text
Text/Image
    ↓
Multimodal embeddings
    ↓
Vector retrieval
    ↓
Metadata filtering
    ↓
Reranking
    ↓
Recommendation
```

## Evaluation dashboard

Portfolio-facing engineering dashboard.

------------------------------------------------------------------------

# 20. Backend

Recommended initial stack:

-   Python + FastAPI for AI/retrieval services
-   PostgreSQL for product metadata
-   pgvector OR Qdrant for vector search
-   Redis for caching/session state where useful
-   object storage for images
-   background worker for catalog embedding generation

Keep the architecture simple initially.

Do not introduce Kubernetes, Kafka, microservices, or distributed
infrastructure unless there is a concrete need.

------------------------------------------------------------------------

# 21. Initial System Architecture

``` text
                        Browser
                           |
                           v
                    Next.js Frontend
                           |
                           v
                    FastAPI Backend
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     Conversation       Retrieval        Product API
       Service          Service
          |                |
          |       +--------+--------+
          |       |                 |
          |       v                 v
          |    Vector DB        PostgreSQL
          |       |
          |       v
          |  Embedding Model
          |
          v
        LLM
```

------------------------------------------------------------------------

# 22. Data Model

## Product

``` text
id
name
description
image_url
price_per_sqft
currency
brand
material
color_family
finish
style[]
room_types[]
availability
dimensions
created_at
updated_at
```

## ProductEmbedding

``` text
product_id
embedding
model_name
embedding_version
created_at
```

## Conversation

``` text
id
session_id
created_at
```

## Message

``` text
id
conversation_id
role
content
created_at
```

## PreferenceState

``` text
session_id
preferred_attributes
negative_attributes
hard_constraints
inferred_attributes
updated_at
```

## SearchEvent

``` text
session_id
query
filters
candidate_count
latency_ms
model_name
created_at
```

------------------------------------------------------------------------

# 23. Catalog Creation

For the MVP, create a curated synthetic/controlled catalog.

The catalog must be realistic enough to support meaningful retrieval.

Each product should have:

-   high-quality image
-   realistic title
-   description
-   price
-   material
-   color
-   finish
-   style
-   room suitability

Aim for an initial dataset of approximately 1,000 products.

After the system works, expand toward 5,000--20,000 products.

Do not fabricate real brand claims.

Clearly mark the environment as a demo catalog.

------------------------------------------------------------------------

# 24. Embedding Generation Pipeline

Create a reproducible CLI:

``` bash
python -m catalog.ingest
python -m catalog.generate_embeddings
python -m catalog.index
```

Requirements:

-   batch processing
-   progress reporting
-   resumability
-   embedding versioning
-   failure recovery
-   deterministic metadata mapping

Do not regenerate embeddings unnecessarily.

------------------------------------------------------------------------

# 25. Search API

Example:

``` http
POST /api/search
```

Request:

``` json
{
  "query": "warm modern light oak matte floor",
  "filters": {
    "max_price_per_sqft": 250,
    "room": "living_room"
  },
  "image": null,
  "top_k": 10
}
```

Response:

``` json
{
  "results": [
    {
      "product_id": "floor_001",
      "score": 0.91,
      "product": {},
      "match_reasons": [
        "light oak appearance",
        "matte finish",
        "within budget",
        "living room compatible"
      ]
    }
  ]
}
```

------------------------------------------------------------------------

# 26. Recommendation API

``` http
POST /api/recommend
```

Request:

``` json
{
  "session_id": "...",
  "query": "...",
  "image": null
}
```

Response should include:

-   extracted intent
-   active preferences
-   recommendations
-   explanations
-   retrieval metadata
-   request ID

Do not expose internal chain-of-thought.

Only expose concise, user-safe reasoning summaries based on observable
matching factors.

------------------------------------------------------------------------

# 27. Observability

Every AI request should generate:

-   request ID
-   latency
-   model
-   input/output token counts where applicable
-   estimated cost
-   retrieval latency
-   number of candidates
-   reranking latency
-   final result count
-   errors

Example:

``` text
Request: req_123

Intent extraction       140ms
Embedding               62ms
Vector search           18ms
Metadata filtering       4ms
Reranking               93ms
Explanation generation  410ms
--------------------------------
Total                   727ms
```

This becomes part of the portfolio's engineering dashboard.

------------------------------------------------------------------------

# 28. Evaluation Framework

This is a core requirement.

Do NOT judge the system only by whether the UI "looks good."

Create a benchmark dataset.

Each benchmark case should contain:

``` json
{
  "query": "light oak matte flooring for a modern living room under ₹250",
  "required_constraints": {
    "room": "living_room",
    "max_price_per_sqft": 250,
    "finish": "matte"
  },
  "relevant_product_ids": [
    "floor_001",
    "floor_037",
    "floor_112"
  ]
}
```

Initial target:

-   100 benchmark queries.

Expand later.

------------------------------------------------------------------------

# 29. Metrics

Track:

## Retrieval

-   Recall@5
-   Recall@10
-   Precision@5
-   NDCG@5
-   NDCG@10

## Constraint satisfaction

Percentage of returned recommendations satisfying:

-   budget
-   room
-   required material
-   required finish

## Conversational quality

Measure:

-   correct preference extraction
-   correct preference updates
-   unnecessary clarification rate
-   recommendation relevance

## System metrics

-   p50 latency
-   p95 latency
-   embedding latency
-   vector search latency
-   LLM latency
-   estimated cost/request

------------------------------------------------------------------------

# 30. Retrieval Experiments

The project must compare at least three retrieval strategies.

## Experiment A --- Pure multimodal vector search

``` text
query embedding
      ↓
vector search
```

## Experiment B --- Vector search + metadata filters

``` text
vector search
      +
metadata constraints
```

## Experiment C --- Hybrid + reranking

``` text
vector retrieval
      +
metadata filtering
      +
reranker
```

Compare results.

Example report:

``` text
                    Recall@10    NDCG@10

Vector only            62%         0.61
Hybrid                 74%         0.74
Hybrid + reranker      86%         0.83
```

Numbers above are examples only. Never fabricate final results.

------------------------------------------------------------------------

# 31. Multimodal Experiments

Compare:

1.  Text only.
2.  Image only.
3.  Text + image.
4.  Text + image + metadata.
5.  Text + image + metadata + reranking.

Measure retrieval quality.

This creates a strong technical story:

> When does visual similarity help beyond natural-language semantic
> retrieval?

------------------------------------------------------------------------

# 32. Scientific Methodology

For each experiment document:

### Hypothesis

Example:

> Combining text and image embeddings should improve retrieval for
> queries containing visual style preferences.

### Experimental setup

-   model
-   dataset
-   hardware
-   embedding version
-   retrieval configuration
-   ranking configuration

### Controlled variables

Keep constant:

-   catalog
-   benchmark queries
-   top-K
-   evaluation procedure

### Independent variable

Change only:

-   embedding strategy
-   fusion weight
-   reranker
-   retrieval strategy

### Results

Record metrics.

### Analysis

Explain why the results changed.

### Limitations

Explicitly state failure cases.

------------------------------------------------------------------------

# 33. Retrieval Debugger

Build a developer-facing UI.

For a query, show:

``` text
USER QUERY

"Warm Scandinavian light oak matte flooring"

        ↓

TEXT EMBEDDING

        ↓

TOP 20 VECTOR RESULTS

        ↓

METADATA FILTER

12 candidates removed

        ↓

8 candidates

        ↓

RERANKER

        ↓

FINAL 5
```

For each product show:

-   semantic similarity
-   metadata match
-   final score
-   reasons for ranking

This is one of the most important portfolio features.

It makes the AI system inspectable.

------------------------------------------------------------------------

# 34. "Break the System" Demo

Add portfolio-only controlled demonstrations.

Examples:

### Change budget

User:

> "Actually, my budget is ₹150."

System reranks.

### Change aesthetic

> "Make it more rustic."

System changes ranking.

### Reject recommendation

> "I don't like glossy floors."

System adds negative preference.

### Reference image

Upload image and show visual retrieval.

This makes the portfolio interactive rather than a static screenshot.

------------------------------------------------------------------------

# 35. Security and Safety

Implement:

-   file type validation
-   upload size limit
-   image processing isolation
-   prompt injection resistance in product metadata
-   no arbitrary tool execution
-   rate limiting
-   server-side API keys only
-   no client-side model provider credentials

Product descriptions are untrusted input.

Never allow product metadata to override system instructions.

------------------------------------------------------------------------

# 36. Future Browser Extension

Do NOT implement in MVP.

Design the backend so it can eventually accept:

``` json
{
  "external_product": {
    "title": "...",
    "price": "...",
    "image": "...",
    "url": "..."
  }
}
```

Future browser extension flow:

``` text
Any supported e-commerce site
          |
          v
     Browser extension
          |
          v
     Shopping Assistant
          |
          v
   Product extraction
          |
          v
 Recommendation Engine
```

The extension could eventually allow:

> "Find something similar but cheaper."

> "Which of these is best for my requirements?"

> "What accessories go with this?"

But this is explicitly future work.

------------------------------------------------------------------------

# 37. Future Generalization

After flooring works, generalize the catalog schema.

Potential verticals:

-   furniture
-   shoes
-   fashion
-   electronics
-   home decor
-   cosmetics

The core engine should eventually become:

``` text
Conversational Shopping Engine

        ↓

Intent extraction
        ↓
Multimodal retrieval
        ↓
Constraint filtering
        ↓
Reranking
        ↓
Recommendation
        ↓
Explanation
```

Domain-specific schemas can sit above the core.

------------------------------------------------------------------------

# 38. Future AI Runtime

After the product works, optionally extract infrastructure into an AI
Runtime layer.

Potential capabilities:

-   provider abstraction
-   model routing
-   retries
-   fallback
-   rate limiting
-   token accounting
-   cost tracking
-   streaming
-   observability

The product should remain the primary portfolio artifact.

The infrastructure exists to support it.

------------------------------------------------------------------------

# 39. Recommended Repository Structure

``` text
aesthetic/
|
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── lib/
│   |
│   └── api/
│       ├── routes/
│       ├── services/
│       ├── models/
│       └── schemas/
|
├── ai/
│   ├── embeddings/
│   ├── retrieval/
│   ├── reranking/
│   ├── recommendation/
│   ├── intent/
│   └── evaluation/
|
├── catalog/
│   ├── data/
│   ├── ingestion/
│   ├── embeddings/
│   └── scripts/
|
├── evaluation/
│   ├── datasets/
│   ├── runners/
│   ├── metrics/
│   └── reports/
|
├── infrastructure/
│   ├── docker/
│   └── compose/
|
├── docs/
│   ├── architecture.md
│   ├── methodology.md
│   ├── experiments/
│   └── decisions/
|
├── tests/
|
├── docker-compose.yml
├── README.md
└── LICENSE
```

------------------------------------------------------------------------

# 40. Development Phases

## Phase 0 --- Project foundation

Tasks:

-   create repository
-   create frontend
-   create backend
-   create PostgreSQL
-   configure vector DB
-   configure local development
-   establish environment variables
-   create CI
-   add linting
-   add tests

Acceptance:

-   frontend loads
-   backend health endpoint works
-   database connects
-   vector DB connects

------------------------------------------------------------------------

## Phase 1 --- Catalog

Tasks:

-   define Product schema
-   create seed dataset
-   build product API
-   build catalog ingestion
-   store product images
-   implement catalog UI

Acceptance:

-   at least 1,000 products available
-   product metadata searchable
-   product detail page works

------------------------------------------------------------------------

## Phase 2 --- Image embeddings

Tasks:

-   select multimodal embedding model
-   implement image encoder
-   batch-generate embeddings
-   store embedding version
-   index vectors

Acceptance:

-   every catalog product has an embedding
-   indexing is reproducible
-   failed embeddings can be retried

------------------------------------------------------------------------

## Phase 3 --- Text-to-image retrieval

Tasks:

-   implement text encoder
-   implement vector search
-   expose search API
-   create search UI

Acceptance:

A user can type:

> "light warm oak floor"

and receive visually/semantically relevant results.

------------------------------------------------------------------------

## Phase 4 --- Metadata filtering

Tasks:

-   extract structured filters
-   implement PostgreSQL metadata filtering
-   combine with vector search

Acceptance:

Queries with budget and room constraints correctly exclude incompatible
products.

------------------------------------------------------------------------

## Phase 5 --- Conversational agent

Tasks:

-   intent extraction
-   preference state
-   clarification questions
-   conversational refinement
-   recommendation generation

Acceptance:

The user can say:

> "Make it lighter."

and the next results reflect that preference.

------------------------------------------------------------------------

## Phase 6 --- Image + text search

Tasks:

-   image upload
-   image embedding
-   text/image fusion
-   configurable weights

Acceptance:

User can upload an inspiration image and say:

> "Something like this, but lighter."

System returns relevant results.

------------------------------------------------------------------------

## Phase 7 --- Reranking

Tasks:

-   implement candidate scoring
-   add configurable ranking weights
-   optionally add learned/cross-encoder reranker
-   benchmark against baseline

Acceptance:

Reranked results measurably improve benchmark metrics.

------------------------------------------------------------------------

## Phase 8 --- Evaluation

Tasks:

-   create 100-query benchmark
-   define relevance labels
-   implement evaluation runner
-   compute Recall@K
-   compute NDCG@K
-   compute constraint satisfaction
-   create experiment reports

Acceptance:

A reproducible command produces evaluation metrics.

Example:

``` bash
python -m evaluation.run
```

------------------------------------------------------------------------

## Phase 9 --- Portfolio UX

Tasks:

-   polish landing page
-   add live playground
-   add recommendation explanations
-   add retrieval debugger
-   add architecture page
-   add evaluation dashboard
-   add methodology page

Acceptance:

A new visitor can:

1.  understand the product in 10--30 seconds
2.  perform a search
3.  upload an image
4.  refine a recommendation
5.  inspect why a result was chosen
6.  inspect evaluation results

------------------------------------------------------------------------

## Phase 10 --- Voice

Only after all previous phases are stable.

Tasks:

-   browser microphone
-   speech-to-text
-   transcript injection
-   conversational interaction

Acceptance:

User can speak a shopping request and receive the same recommendation
quality as text input.

------------------------------------------------------------------------

# 41. Technical Quality Requirements

The coding agent must:

-   write typed code
-   include unit tests for core logic
-   include integration tests for retrieval
-   validate API inputs
-   handle failures gracefully
-   log request IDs
-   avoid hard-coded secrets
-   document configuration
-   keep model configuration externalized
-   make embedding model configurable
-   make vector DB configurable where practical
-   keep retrieval scoring configurable
-   use deterministic seeds where applicable
-   provide reproducible setup instructions

------------------------------------------------------------------------

# 42. Performance Requirements

Initial targets:

-   catalog search p95 \< 1 second excluding external LLM latency
-   image embedding latency should be measured
-   vector search should remain low-latency at 10k products
-   frontend should stream/appear responsive
-   recommendation generation should not block unnecessarily

Do not optimize prematurely.

Measure before optimizing.

------------------------------------------------------------------------

# 43. Cost Requirements

The public demo must be abuse-resistant.

Implement:

-   per-session request limits
-   rate limiting
-   maximum input size
-   maximum image size
-   maximum conversation length
-   token budget
-   server-side API keys

Use caching wherever appropriate.

Do not expose provider API keys to the browser.

------------------------------------------------------------------------

# 44. Portfolio Metrics

The final portfolio should display actual measured numbers.

Potential metrics:

``` text
Catalog size
1,000+ products

Benchmark queries
100+

Recall@10
XX%

NDCG@10
XX

Constraint satisfaction
XX%

p95 retrieval latency
XX ms

Image + text improvement
XX%

Average recommendation cost
$X.XX
```

Do not manufacture numbers.

Every displayed metric must come from a reproducible experiment.

------------------------------------------------------------------------

# 45. Portfolio Case Study

The final project page should contain:

## Problem

Traditional e-commerce search requires users to translate preferences
into filters.

## Solution

A conversational multimodal shopping assistant.

## Demo

Interactive live experience.

## Architecture

System diagram.

## Retrieval

Explain multimodal embeddings + hybrid search + reranking.

## Experiments

Compare retrieval approaches.

## Results

Show actual benchmark results.

## Failure cases

Show where the system struggles.

## Engineering decisions

Explain why specific components were selected.

## Future roadmap

Explain browser extension and multi-domain expansion.

------------------------------------------------------------------------

# 46. What NOT to Claim

Do not claim:

-   production scale if it is not production scale
-   real commercial conversion improvement
-   real customer revenue
-   real Amazon/Flipkart integration
-   superior recommendation quality without evaluation
-   "AI understands taste" as an absolute claim
-   perfect semantic search
-   autonomous purchasing

Use accurate wording:

> "Prototype"

> "Controlled demo catalog"

> "Benchmark results"

> "Experimental system"

This increases credibility.

------------------------------------------------------------------------

# 47. Product Success Criteria

The MVP is successful when a new visitor can perform this interaction:

### User

> "I want a warm Scandinavian floor for my living room, light oak,
> matte, under ₹250/sq ft."

### System

Returns relevant products.

### User

> "I like the second one, but make it lighter and less yellow."

### System

Updates preferences and reranks.

### User

Uploads a reference image.

### System

Returns visually similar products.

### User

> "Compare the top two."

### System

Shows a grounded comparison.

### User

> "Why did you choose this one?"

### System

Explains the recommendation using observable product attributes.

### Developer/interviewer

Opens:

> **How it works**

and can inspect:

-   embeddings
-   retrieval
-   filtering
-   reranking
-   evaluation

That is the definition of done for the first major version.

------------------------------------------------------------------------

# 48. Definition of Done

The project is NOT considered complete merely because the chat UI works.

It is complete when all of the following exist:

-   [ ] Working web application.
-   [ ] Curated flooring catalog.
-   [ ] Image embeddings.
-   [ ] Text/image shared embedding retrieval.
-   [ ] Vector search.
-   [ ] Metadata filtering.
-   [ ] Hybrid ranking.
-   [ ] Conversational preference state.
-   [ ] Image upload.
-   [ ] Recommendation explanations.
-   [ ] Product comparison.
-   [ ] Evaluation benchmark.
-   [ ] Retrieval metrics.
-   [ ] Reproducible evaluation runner.
-   [ ] Retrieval debugger.
-   [ ] Observability.
-   [ ] Rate limiting.
-   [ ] Tests.
-   [ ] Docker/local setup.
-   [ ] Architecture documentation.
-   [ ] Technical methodology documentation.
-   [ ] Polished portfolio page.
-   [ ] Live demo.

------------------------------------------------------------------------

# 49. Guiding Principle for the Coding Agent

Build this in **vertical slices**.

Do not implement the entire architecture before anything works.

The preferred progression is:

``` text
Catalog
  ↓
Simple search
  ↓
Vector search
  ↓
Conversational search
  ↓
Hybrid retrieval
  ↓
Image search
  ↓
Reranking
  ↓
Evaluation
  ↓
Portfolio polish
```

At every stage:

1.  Build.
2.  Test.
3.  Demonstrate.
4.  Measure.
5.  Document.
6.  Then expand.

Do not introduce infrastructure merely because it is technically
interesting.

Every component must serve the product or provide measurable engineering
value.

------------------------------------------------------------------------

# 50. Long-Term Vision

The flooring application is the first vertical, not the final product.

Long-term:

``` text
                    AESTHETIC
                       |
          Conversational Shopping
                       |
       +---------------+---------------+
       |               |               |
    Flooring        Furniture       Fashion
       |               |               |
       +---------------+---------------+
                       |
                Multimodal Search
                       |
                Recommendation
                       |
                Preference Memory
                       |
                 Agent Runtime
                       |
                Browser Assistant
                       |
              Cross-site shopping
```

The ultimate product vision is:

> **An intelligent shopping layer that lets people interact with the web
> conversationally instead of navigating rigid search interfaces.**

But the implementation must start with one narrow, measurable domain.

------------------------------------------------------------------------

# 51. Final Instruction to the Coding Agent

Treat this document as the product specification.

Do not skip directly to the most sophisticated architecture.

Start with Phase 0.

After completing each phase:

-   run tests
-   verify acceptance criteria
-   update documentation
-   provide a concise implementation summary
-   identify the next phase
-   do not silently expand scope

If a technology choice is ambiguous, prefer:

1.  simplicity,
2.  reproducibility,
3.  local development,
4.  observability,
5.  measurable evaluation,
6.  replaceability.

The primary objective is not to demonstrate the maximum number of AI
technologies.

The primary objective is to create a **beautiful, useful, technically
credible multimodal conversational shopping product whose engineering
can withstand an AI/backend engineering interview.**
