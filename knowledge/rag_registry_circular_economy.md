# Circular Prototype RAG Registry

**Version:** 1.3
**Purpose:** Structured knowledge base for generating circular economy business model prototypes from an organization profile and a stated outcome.
**Source frameworks:** Sitra/Deloitte Circular Economy Playbook, Disrupt Design Circular Economy Workshop Kit, Circular Systems Design Handbook, Board of Innovation Circular Economy Report, Circular Prototype Prompter (Scamahorn)

---

## Section 1: Value Chain Inefficiency Taxonomy

| Inefficiency Type | Description | Circular Signal |
|---|---|---|
| **Wasted end-of-life value** | Products landfilled or incinerated rather than recovered | Take-back programs, deposit-return, resale marketplaces |
| **Unsustainable material use** | Virgin materials consumed with no recovery pathway | Closed-loop material flows, bio-based inputs, industrial symbiosis |
| **Premature product life** | Products discarded before end of functional life | Repair-as-a-service, remanufacturing, design for modularity |
| **Underutilized capacity** | Products, assets, or infrastructure sitting idle | Sharing platforms, pay-per-use, peer access models |
| **Unexploited customer engagement** | Revenue limited to a single transaction rather than ongoing engagement | Product-as-a-service, performance-as-a-service, subscription access |
| **Toxic or non-recoverable material content** | Product design locks in materials that cannot circulate | Total product redesign, design for disassembly, low-impact material substitution |
| **Waste-stream volume with no destination** | Byproducts or offcuts accumulate without a receiving system | Industrial symbiosis, waste-as-resource partnerships |

---

## Section 2: Prototype-Ready Circular Mechanics

| Mechanic | User Interaction | Value Exchange | Closes Which Loop |
|---|---|---|---|
| **Deposit-return** | User pays a deposit at purchase, gets it back on return | Financial incentive drives return behavior; the loop is the value | Material recovery loop |
| **Product as a service (PaaS)** | User pays to access, not own; producer retains the asset | Ongoing revenue replaces one-time sale; producer controls end-of-life | Asset retention loop |
| **Performance as a service** | User pays for an outcome (lumens, not lightbulbs); supplier absorbs product risk | Outcome billing aligns producer incentives with efficiency and longevity | Resource efficiency loop |
| **Remanufacturing** | Producer takes back, restores to original spec, and re-sells at a lower price point | Secondary revenue from refurbished asset; lower-cost entry point for buyers | Technical material loop |
| **Repair as a service** | Producer or third party extends product life through paid servicing | Extended product life generates service revenue; defers replacement cost for user | Product lifespan loop |
| **Take-back / gamified returns** | User returns end-of-life product in exchange for credit, discount, or reward | Behavioral incentive closes the return gap; recovered material re-enters supply chain | Material recovery loop |
| **Sharing platform** | Users access idle assets without owning them; platform captures the transaction | Idle asset utilization converted to revenue; user avoids ownership cost | Utilization loop |
| **Pay-per-use** | User pays only for consumption; removes the ownership burden | Usage-based pricing aligns cost with value; producer retains and manages the asset | Asset retention and utilization loop |
| **Resale / second-hand marketplace** | Producer or platform brokers the product's second life | Extended revenue from the same unit; lower-cost access for secondary buyers | Product lifespan loop |
| **Waste-as-resource (industrial symbiosis)** | One organization's waste stream becomes another's input material | Waste disposal cost eliminated for sender; input cost reduced for receiver | Industrial material loop |

### Extended Design Strategy Reference

The following strategies from the Disrupt Design Circular Economy framework are **upstream design enablers**, not standalone prototype mechanics. Use them to qualify or sharpen a concept that already has a named mechanic, not as replacements for one.

- Closed loop business model / closed loop production model
- Design for disassembly, remanufacture, repair, modularity, recyclability, durability, multifunctionality, dematerialization
- Producer stewardship / extended producer responsibility
- Full life cycle thinking
- Total product redesign / functionality reassessment
- High value recycling / on-site composting / infrastructure development
- Low impact materials

---

## Section 3: Circularity Principles Reference (Design Guardrails)

These principles, drawn from the Circular Systems Design Handbook and Sitra/Deloitte Playbook, inform what "circular" means at the system level. Use them to pressure-test concepts for depth. They are not mechanics: they are the "why" behind every mechanic.

- **Waste equals food:** All material outputs are nutrients to another part of the system.
- **Life cycle thinking:** Value is designed to be captured across the entire product life, not just at point of sale.
- **Extended producer responsibility:** The producer retains accountability for the product through end-of-life.
- **Product-service systems:** The shift from selling products to delivering outcomes through long-term relationships.
- **True cost accounting:** Environmental and social impacts are internalized, not externalized.
- **Industrial ecology:** Industrial systems are modeled on ecological nutrient cycles, not linear extraction flows.
- **Cradle to cradle:** End-of-life is designed at the conception stage, not addressed after the fact.

---

## Section 4: RAG Entry Field Taxonomy (Controlled Vocabulary)

This section is the canonical source for classification field definitions used across all RAG knowledge base files. Update definitions here only. RAG files reference this section rather than duplicating it.

---

### G: Circular Business Model (Primary)

The top-level strategic pattern the case exemplifies. Each entry carries exactly one primary model.

| Value | Definition |
|---|---|
| **Circular Inputs** | Products made from recycled, renewable, or bio-based materials that eliminate the use of virgin or toxic inputs. Includes circular supplies and sustainable product design strategies. |
| **Sharing Platform** | A platform or system that enables users to share, rent, or access products or assets rather than own them outright, increasing utilization rates across the user base. |
| **Product as a Service** | The producer retains ownership of the product and charges customers for the service or performance it delivers (e.g., per use, per outcome, or subscription), creating a financial incentive for durability, efficiency, and end-of-life recovery. |
| **Product Use Extension** | Business models that keep products and components in use for longer through repair, remanufacturing, refurbishment, resale, or upgrading, deferring or avoiding end of life. |
| **Resource Recovery** | Systems that recover energy, materials, or nutrients from products or waste streams at end of life, through recycling, upcycling, anaerobic digestion, composting, or industrial symbiosis. |

---

### H: Circular Sub-Models

One or more sub-models that describe the specific circular mechanisms deployed within the primary model. Entries may carry multiple values.

| Value | Definition |
|---|---|
| **Circular supplies** | Sourcing inputs that are recycled, renewable, or bio-based, replacing virgin or hazardous materials. |
| **Sustainable product design** | Designing products to use fewer materials, last longer, be safer, or be more easily repaired, disassembled, or recycled. |
| **Share** | Enabling multiple users to access the same physical asset sequentially or simultaneously, peer-to-peer or platform-mediated. |
| **Pay-per-use** | Charging customers only for the units of service or output they actually consume rather than for ownership of the product. |
| **Performance as a service** | Charging for a guaranteed outcome or level of service, such as lux of light or degrees of cooling: outcome-based pricing. |
| **Repair and maintain** | Servicing and fixing products to restore function and extend useful life, avoiding premature replacement. |
| **Upgrade** | Improving a product's capability or appearance to extend its relevance and life, avoiding full replacement. |
| **Remanufacture** | Restoring a used product or component to original specification, typically via disassembly, cleaning, inspection, replacement of worn parts, and testing. |
| **Resell** | Selling a product for a second or subsequent time to a new owner through a secondary market, second-hand or pre-owned. |
| **Return** | Bringing nutrients or materials back to the biological or technical cycle after use, through composting, recycling, or soil amendment. |
| **Recycle / upcycle** | Processing end-of-life materials into new raw material inputs, ideally at equal or higher quality (upcycling) rather than lower quality (downcycling). |
| **Deposit-return** | A financial deposit is charged at point of purchase and refunded when the customer returns the product or packaging to a designated collection point, creating a direct monetary incentive for return behavior. |
| **Take-back / gamified returns** | Manufacturer or retailer-operated programs that collect used products or packaging from customers, often with an incentive such as a discount, deposit, or loyalty points. |
| **Waste-as-resource (industrial symbiosis)** | One company's waste or by-product becomes a productive input for another company, eliminating disposal and replacing virgin material. |
| **Product as a service** | A pricing and ownership structure in which the producer retains the physical asset and the customer pays for access, usage, or outcomes, typically via subscription, per-use, or performance billing, rather than purchasing the product outright. |

---

### AC: Inefficiency Type

The underlying linear economy failure the circular model addresses. Entries may carry multiple values.

| Value | Definition |
|---|---|
| **Wasted end-of-life value** | Valuable materials, components, or nutrients are lost at end of product or material life, through landfill, incineration, or unrecovered disposal. |
| **Unsustainable material use** | Products or processes rely on virgin, toxic, non-renewable, or ecologically harmful inputs that deplete natural systems. |
| **Premature product life** | Products are discarded or replaced before their functional life is exhausted, due to design, fashion cycles, or lack of repair options. |
| **Underutilized capacity** | Physical assets (products, equipment, space, vehicles) sit idle for a significant portion of their potential productive life. |
| **Unexploited customer engagement** | Existing customer relationships or touchpoints are not used to create circular value, such as no take-back program, no service model, or no loyalty loop. |
| **Toxic or non-recoverable material content** | Product or material design locks in substances that cannot re-enter biological or technical cycles, making recovery or reuse impossible at end of life. |
| **Waste-stream volume with no destination** | Byproducts, offcuts, or organic outputs accumulate without a receiving system, defaulting to landfill or incineration rather than re-entering a productive cycle. |

---

### AD: Economic / Regulatory Pressure

The primary external or internal driver that motivated the circular initiative. Entries may carry multiple values.

| Value | Definition |
|---|---|
| **Internal mandate or leadership commitment** | A founder's mission, CEO commitment, or board-level strategic decision drove the circular initiative, not primarily external pressure. |
| **Consumer demand shift** | Changing customer preferences, values, or purchasing behavior toward sustainable, ethical, or low-waste options created market pull. |
| **Regulatory / compliance pressure** | Existing or anticipated legislation, standards, or policy requirements made the circular model necessary or commercially advantageous. |
| **Investor or ESG pressure** | Institutional investors, ESG ratings, sustainability disclosure requirements, or capital market expectations drove the circular transition. |
| **Competitor or market pressure** | Competitive dynamics, such as rivals launching circular models, new market entrants, or shifting industry norms, prompted the circular response. |
| **Resource cost or scarcity** | Rising costs, supply volatility, or strategic scarcity of virgin materials, energy, or water made circular inputs or efficiency economically attractive. |

---

### AE: Success Criteria

The primary metric or outcome against which the circular initiative is evaluated. Entries may carry multiple values.

| Value | Definition |
|---|---|
| **Cost reduction** | The circular model reduces input costs, waste disposal costs, energy costs, or total cost of ownership for the organization or its customers. |
| **New revenue or market access** | The circular model opens a new revenue stream, customer segment, or market that the linear model could not access. |
| **Customer retention or deepened relationship** | The circular model creates a longer-term or more frequent relationship with customers, through service contracts, take-back, subscription, or loyalty. |
| **Brand differentiation** | The circular model creates a distinct, credible sustainability positioning that differentiates the organization from linear competitors. |
| **Regulatory compliance** | The circular model enables the organization to meet existing or anticipated legal, policy, or reporting requirements. |
| **Supply chain resilience** | The circular model reduces dependency on volatile, scarce, or geopolitically risky virgin material inputs by closing material loops internally or locally. |
| **Emissions or resource reduction target** | The circular model is primarily evaluated against a quantified environmental goal, such as carbon, waste, water, or material reduction, rather than a financial metric. |

---

### AH: Prototype Readiness Statement (Classification)

Indicates how fully the case supports a user-facing circular prototype. Used to assess which entries can be directly adapted for concept generation.

| Value | Definition |
|---|---|
| **Prototype-ready (complete sentence)** | A complete sentence following the pattern: "The user [does X], and in return receives [Y], while the producer closes the [loop name] loop by [doing Z]." All three elements are present and specific enough to prototype a user interaction. |
| **Mechanic present but not prototype-ready** | The circular mechanic is identifiable (e.g., take-back exists, service model exists) but the case lacks sufficient detail on the user interaction, incentive structure, or return exchange to draft a complete prototype sentence. |
| **Design principle only** | The case describes a design philosophy, material choice, or policy framework rather than a discrete product-user interaction. No testable circular exchange between a user and a producer is described. Applies to most policy/governance cases, research projects, and supply-chain-only interventions. |

---

### AM: Maturity Stage

The lifecycle stage of the circular initiative at the time of documentation. Each entry carries exactly one value.

| Value | Definition |
|---|---|
| **Pilot** | Model under active testing at limited scale; not yet commercially launched or self-sustaining. |
| **Early Growth** | Past initial validation; generating early commercial activity but not yet established at scale. |
| **Growth** | Commercially active, scaling, and generating revenue; not yet at full national or sector-wide scale. |
| **Operating at scale** | Mature system operating at full commercial, national, or sector-wide scale with proven unit economics. |

---

## Section 5: Confidence and Data Quality

All entries in RAG knowledge base files carry a `confidence_score` of **High**, sourced directly from the circular examples database. Field values marked "Not stated" in the source have been omitted rather than interpolated. Do not treat omitted fields as negative evidence: they reflect source limitations, not model failure.
