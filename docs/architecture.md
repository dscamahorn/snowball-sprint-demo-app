# Architecture

## Sequence diagram

```mermaid
sequenceDiagram
    actor User
    participant B  as Browser (Alpine.js)
    participant F  as Flask (app/routes_*.py)
    participant RA as research_agent.py
    participant T  as Tavily API
    participant S  as claude-sonnet-4-6
    participant R  as RAG files
    participant G  as gemini-3.1-flash-image-preview

    alt Research path
        User->>B: Enter org name + industry, click Research
        B->>F: POST /research-stream
        F-->>B: SSE stream opens
        F->>RA: stream_research_org(org, industry)

        Note over RA,S: Phase 1: plan queries
        RA->>S: query_planner_prompt.md + org/industry
        S-->>RA: JSON with brand_queries, parent, parent_queries

        Note over RA,T: Phase 2: round 1 search (brand, then parent)
        loop For each query (up to 5 brand, up to 4 parent)
            RA-->>B: SSE type:search
            RA->>T: search(query, advanced, 5 results)
            T-->>RA: results, deduplicated by URL
        end

        Note over RA,S: Phase 3: reflect (MAX_SEARCH_ROUNDS = 2, so at most once)
        RA->>S: reflector_prompt.md + first 20 results
        S-->>RA: JSON done, or search_again with up to 3 queries
        opt search_again
            loop For each follow-up query
                RA-->>B: SSE type:search
                RA->>T: search(query)
                T-->>RA: new results merged in
            end
        end

        Note over RA,S: Phase 4: interpret
        RA->>S: interpreter_prompt.md + all results
        S-->>RA: research XML: 5 answers with confidence
        RA->>F: store in research_result_cache
        F-->>B: SSE type:done

        B->>F: GET /review
        F->>F: take from research_result_cache, write session
        F-->>B: review.html (answers + confidence badges)

    else Survey path
        User->>B: Click Begin survey, answer 5 questions
        B->>F: POST /submit
        F->>F: session["answers"] = answers
        F-->>B: redirect to GET /review
        F-->>B: review.html
    end

    Note over User,B: User edits answers, sets concept count
    User->>B: Click Generate concepts
    B->>F: POST /generate-stream
    F->>R: load_rag_context()
    R-->>F: three knowledge files as one string
    F-->>B: SSE stream opens
    F->>S: system_prompt.md + answers + RAG (streaming)
    loop Streamed text chunks
        S-->>F: text delta
        F-->>B: SSE concept_start / concept_end
    end
    F->>F: parse_concept_output(), store in concept_result_cache
    F-->>B: SSE type:done

    B->>F: GET /concepts
    F->>F: take from concept_result_cache
    F-->>B: concepts.html (accordion cards)

    opt Visualize Prototype
        User->>B: Click Visualize Prototype
        B->>F: POST /visualize with image_fields JSON
        F->>F: build_image_prompt()
        F->>G: generate_content(reference image + prompt)
        G-->>F: PNG bytes
        F-->>B: base64 data URL
        B->>B: show image in the card
    end
```

## Model interactions

```mermaid
flowchart TB
    classDef llm      fill:#e9d5ff,stroke:#7c3aed,color:#1a1a1a,font-weight:bold
    classDef ext      fill:#bfdbfe,stroke:#1d4ed8,color:#1a1a1a
    classDef artifact fill:#fef9c3,stroke:#92400e,color:#1a1a1a
    classDef ui       fill:#bbf7d0,stroke:#15803d,color:#1a1a1a

    OrgInput(["Org name + industry"]):::ui
    SurveyInput(["5 survey answers"]):::ui

    subgraph Research["Research agent (app/research_agent.py)"]
        direction TB
        Planner["claude-sonnet-4-6\nQuery planner\nquery_planner_prompt.md"]:::llm
        Queries[/"brand_queries + parent + parent_queries"/]:::artifact
        Tavily["Tavily search API\nadvanced depth, 5 results per query"]:::ext
        Results[/"Round 1 results, URL-deduplicated"/]:::artifact
        Reflector["claude-sonnet-4-6\nReflector\nreflector_prompt.md"]:::llm
        Decision{{"done or search_again"}}:::artifact
        FollowUp["Tavily search API\nup to 3 follow-up queries"]:::ext
        Interp["claude-sonnet-4-6\nInterpreter\ninterpreter_prompt.md"]:::llm
        ResearchXML[/"research XML\n5 answers with confidence"/]:::artifact
        Planner --> Queries --> Tavily --> Results --> Reflector --> Decision
        Decision -->|done| Interp
        Decision -->|search_again| FollowUp --> Results
        Interp --> ResearchXML
    end

    Review(["Review page\neditable answers, confidence badges"]):::ui

    subgraph ConceptGen["Concept generation (app/llm.py)"]
        direction TB
        RAG["RAG context (app/rag.py)\nConsumer packaging reuse\nFood waste and upcycling\nB2B asset sharing"]:::artifact
        Generator["claude-sonnet-4-6\nConcept generator\nsystem_prompt.md\nstreaming, 8192 max tokens"]:::llm
        ConceptXML[/"response XML\n1 to 8 concepts"/]:::artifact
        RAG --> Generator --> ConceptXML
    end

    subgraph Viz["Visualization (app/image_gen.py)"]
        direction TB
        ImagePrompt["Image prompt builder\nimage_prompt.md with fields filled in"]:::artifact
        RefImage["Style reference\nknowledge/image_reference.jpg"]:::artifact
        Gemini["gemini-3.1-flash-image-preview\nresponse_modalities: IMAGE"]:::llm
        PNG[/"16:9 PNG as base64 data URL"/]:::artifact
        ImagePrompt --> Gemini
        RefImage --> Gemini
        Gemini --> PNG
    end

    Concepts(["Concepts page\naccordion cards, favorites"]):::ui

    OrgInput --> Research
    ResearchXML --> Review
    SurveyInput --> Review
    Review --> Generator
    ConceptXML --> Concepts
    Concepts -->|image_fields| ImagePrompt
```

## Model summary

| Model | Role | Prompt file | Max tokens (constant) |
|---|---|---|---|
| `claude-sonnet-4-6` | Query planner | `query_planner_prompt.md` | 768 (`QUERY_PLANNER_MAX_TOKENS`) |
| `claude-sonnet-4-6` | Research reflector | `reflector_prompt.md` | 256 (`REFLECTOR_MAX_TOKENS`) |
| `claude-sonnet-4-6` | Research interpreter | `interpreter_prompt.md` | 2048 (`INTERPRETER_MAX_TOKENS`) |
| `claude-sonnet-4-6` | Concept generator | `system_prompt.md` | 8192 (`CONCEPT_GENERATION_MAX_TOKENS`) |
| `gemini-3.1-flash-image-preview` | Prototype visualizer | `image_prompt.md` | not applicable |

Model names are set once in `config.py` (`CLAUDE_MODEL`, `GEMINI_IMAGE_MODEL`). The token limits and search caps are named constants at the top of the module that uses them.

## External APIs

| Service | Used by | Purpose |
|---|---|---|
| Anthropic | `llm.py`, `research_agent.py` | All Claude calls |
| Tavily | `research_agent.py` | Web search, advanced depth, 5 results per query |
| Google AI | `image_gen.py` | Gemini image generation |
| PostHog (optional) | `analytics.py`, `base.html` | Product analytics and AI observability |
