# Architecture Diagram

## UML Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant B  as Browser (Alpine.js)
    participant F  as Flask (routes.py)
    participant RA as research_agent.py
    participant H  as claude-sonnet-4-6 (planner)
    participant T  as Tavily API
    participant S  as claude-sonnet-4-6
    participant R  as RAG files
    participant G  as gemini-2.5-flash-image

    %% ── Entry: two paths ────────────────────────────────────
    alt Research path
        User->>B: Enter org name + industry, click Research
        B->>F: POST /research-stream
        F-->>B: SSE stream opens

        F->>RA: stream_research_org(org, industry)

        Note over RA,H: Phase 1 — Query Planning
        RA->>H: query_planner_prompt.md + org/industry
        H-->>RA: JSON object with brand_queries + parent + parent_queries

        Note over RA,T: Phase 2 — Round 1 Search (brand)
        loop For each brand query (3–5)
            RA-->>B: SSE type:search query string
            RA->>T: search query · advanced · max 5 results
            T-->>RA: results deduplicated by URL
        end

        opt Parent company identified
            Note over RA,T: Phase 2b — Round 1 Search (parent)
            loop For each parent query (2–4)
                RA-->>B: SSE type:search query string
                RA->>T: search query · advanced · max 5 results
                T-->>RA: results deduplicated by URL
            end
        end

        Note over RA,S: Phase 3 — Reflect (up to 2 times)
        RA->>S: reflector_prompt.md + all round 1 results
        S-->>RA: JSON done or search_again with queries

        opt search_again
            loop For each follow-up query (2–3)
                RA-->>B: SSE type:search query string
                RA->>T: targeted query · advanced · max 5 results
                T-->>RA: results deduplicated against prior rounds
            end
            RA->>S: reflector_prompt.md + updated results
            S-->>RA: JSON done or search_again
        end

        Note over RA,S: Phase 4 — Interpretation
        RA-->>B: SSE type:status Synthesizing findings
        RA->>S: interpreter_prompt.md + all search results
        S-->>RA: research XML with 5 answers and confidence
        RA->>F: store parsed result in _research_cache
        RA-->>B: SSE type:done

        B->>F: GET /review
        F->>F: pop _research_cache → write session
        F-->>B: review.html (answers + confidence badges)

    else Survey path
        User->>B: Click Begin survey, complete 5 questions
        B->>F: POST /submit (form answers)
        F->>F: session["answers"] = answers
        F-->>B: redirect → GET /review
        F-->>B: review.html (blank confidence badges)
    end

    %% ── Review (common) ─────────────────────────────────────
    Note over User,B: User edits answers, sets concept count
    User->>B: Click Generate concepts

    %% ── Concept Generation ──────────────────────────────────
    B->>F: POST /generate-stream (answers + n_concepts)
    F->>R: load_rag_context() — CPR + FWU + BAS XML files
    R-->>F: concatenated RAG context string
    F-->>B: SSE stream opens

    F->>S: system_prompt.md + answers + RAG  [streaming]
    loop Streaming response chunks
        S-->>F: text delta
        F-->>B: SSE type:concept_start number N
        F-->>B: SSE type:concept_end number N
    end
    S-->>F: complete response XML
    F->>F: _parse_llm_output() into concepts list
    F->>F: store in _concept_cache
    F-->>B: SSE type:done

    B->>F: GET /concepts
    F->>F: pop _concept_cache
    F-->>B: concepts.html (accordion cards)

    %% ── Visualization (optional, per concept) ───────────────
    opt User clicks Visualize Prototype
        User->>B: Click Visualize Prototype
        B->>F: POST /visualize with image_fields JSON
        F->>F: build_image_prompt() — inject fields into image_prompt.md
        F->>G: generate_content with IMAGE + TEXT modalities
        G-->>F: PNG bytes via inline_data
        F-->>B: base64 data URI
        B->>B: Render image in concept card
    end
```

---

## LLM Model Interactions

```mermaid
flowchart TB
    classDef llm      fill:#e9d5ff,stroke:#7c3aed,color:#1a1a1a,font-weight:bold
    classDef ext      fill:#bfdbfe,stroke:#1d4ed8,color:#1a1a1a
    classDef artifact fill:#fef9c3,stroke:#92400e,color:#1a1a1a
    classDef ui       fill:#bbf7d0,stroke:#15803d,color:#1a1a1a

    %% ── Inputs ──────────────────────────────────────────────
    OrgInput(["① Org name + industry"]):::ui
    SurveyInput(["① 5 survey answers"]):::ui

    %% ── Research Agent Pipeline ──────────────────────────────
    subgraph Research["Research Agent  ·  app/research_agent.py"]
        direction TB
        Planner["claude-sonnet-4-6\nQuery Planner\nprompts/query_planner_prompt.md"]:::llm
        Queries[/"brand_queries + parent + parent_queries\nJSON object"/]:::artifact
        TavilyBrand["Tavily Search API\nbrand queries · 3-5 · advanced depth"]:::ext
        TavilyParent["Tavily Search API\nparent queries · 2-4 · advanced depth"]:::ext
        Results[/"Round 1 results\nbrand + parent · URL-deduplicated"/]:::artifact
        Reflector["claude-sonnet-4-6\nReflector\nprompts/reflector_prompt.md\nfires up to 2 times"]:::llm
        Decision{{"done or search_again"}}:::artifact
        TavilyFollowUp["Tavily Search API\n2-3 targeted follow-up queries"]:::ext
        Results2[/"Follow-up results\nmerged and deduplicated"/]:::artifact
        Interp["claude-sonnet-4-6\nInterpreter\nprompts/interpreter_prompt.md\nparent company context injected"]:::llm
        ResearchXML[/"&lt;research&gt; XML\n5 answers · confidence ratings"/]:::artifact
        Planner --> Queries --> TavilyBrand --> Results
        Queries --> TavilyParent --> Results
        Results --> Reflector --> Decision
        Decision -->|done| Interp
        Decision -->|search_again| TavilyFollowUp --> Results2 --> Reflector
        Interp --> ResearchXML
    end

    %% ── Review ───────────────────────────────────────────────
    Review(["② Review page\nEditable answers · Confidence badges"]):::ui

    %% ── Concept Generation Pipeline ──────────────────────────
    subgraph ConceptGen["Concept Generation  ·  app/llm.py"]
        direction TB
        RAG["RAG Context  ·  app/rag.py\nConsumer Packaging Reuse\nFood Waste & Upcycling\nB2B Asset Sharing\n3 XML knowledge bases"]:::artifact
        Generator["claude-sonnet-4-6\nConcept Generator\nprompts/system_prompt.md\nstreaming · 8 192 tokens"]:::llm
        ConceptXML[/"&lt;response&gt; XML\n3–8 concepts with fields:\ntitle · mechanic · description\nprototype_sentence · prototype_image\nassumptions · citations"/]:::artifact
        RAG --> Generator --> ConceptXML
    end

    %% ── Visualization ────────────────────────────────────────
    subgraph Viz["Visualization  ·  app/image_gen.py"]
        direction TB
        ImagePrompt["Image prompt builder\nprompts/image_prompt.md\nInjects loop_name · narrative 1–4"]:::artifact
        RefImage["Style reference\nknowledge/image_reference.jpg"]:::artifact
        Gemini["gemini-3.1-flash-image-preview\nVisualize Prototype\nresponse_modalities: IMAGE\nhigh thinking"]:::llm
        PNG[/"16 : 9 PNG\nbase64 data URI\nreturned to browser"/]:::artifact
        ImagePrompt --> Gemini
        RefImage --> Gemini
        Gemini --> PNG
    end

    %% ── Outputs ──────────────────────────────────────────────
    Concepts(["③ Concepts page\nAccordion cards · Favourites"]):::ui

    %% ── Connections ──────────────────────────────────────────
    OrgInput      --> Research
    ResearchXML   --> Review
    SurveyInput   --> Review
    Review        --> Generator
    ConceptXML    --> Concepts
    Concepts      -->|"image_fields from\nprototype_image XML"| ImagePrompt
```

## Model summary

| Model | Role | Prompt file | Max tokens |
|---|---|---|---|
| `claude-sonnet-4-6` | Query planner | `query_planner_prompt.md` | 768 |
| `claude-sonnet-4-6` | Research reflector | `reflector_prompt.md` | 256 |
| `claude-sonnet-4-6` | Research interpreter | `interpreter_prompt.md` | 2 048 |
| `claude-sonnet-4-6` | Concept generator | `system_prompt.md` | 8 192 |
| `gemini-3.1-flash-image-preview` | Prototype visualizer | `image_prompt.md` | — |

## External APIs

| Service | Used by | Purpose |
|---|---|---|
| Tavily | Research agent | Web search · advanced depth · 5 results/query |
| Anthropic | llm.py · research_agent.py | All Claude calls |
| Google AI | image_gen.py | Gemini image generation |