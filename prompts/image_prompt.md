### Circular Image Generation Prompt

A reference image is provided alongside this text prompt. Match its visual style precisely: editorial hand-drawn illustration, warm cream background, chunky bold curved arrows, thin callout lines with text labels, clean centered reward box.

**Aspect Ratio:** 16:9

**Brand Tokens:**
- Headline font: Literata (serif) — panel titles ("User Action", "Producer Loop") and loop name badge
- Label/body font: Nunito Sans — all callout labels, stage labels, reward box text
- Arrow color 1: #4a7c59 (forest green)
- Arrow color 2: #705c30 (warm amber)
- Background: #faf6f0 (warm off-white, slightly textured paper)
- Reward box: white fill, thin #705c30 border, subtle drop shadow

**Style:**
Clean editorial hand-drawn illustration. Confident marker strokes, not photorealistic. Match the weight, looseness, and warmth of the reference image exactly. No gradients, no 3D effects.

---

**Composition: Two-Panel Layout**

Divide the image into two equal panels side by side, separated by a faint vertical rule.

---

**Left Panel — User Interaction Scene:**

- Panel title at top: "**User Action**" in Literata serif
- Draw a single person in physically interacting with the product or system described in `[NARRATIVE_1_TEXT]`. Match the editorial sketch style of the reference: loose confident strokes, no heavy shading.
- Show the key physical objects involved (product, packaging, screen, document — whatever the context calls for).
- Add **thin straight callout lines** with Nunito Sans text labels pointing to: the person's role, the key object(s), and any document or digital interface present. Labels sit at the end of each line, left- or right-aligned to the line tip.
- Never output the full `[NARRATIVE_1_TEXT]`.

---

**Center — Reward Box:**

Centered vertically between the two panels, overlapping the dividing rule:
- Outlined rectangle, white fill, thin amber border, soft drop shadow
- Top label in lighter weight: "**User Reward**"
- Dollar sign icon (outline circle) below User Reward in the top center of the box
- Bold text: "**[NARRATIVE_2_TEXT]**"


---

**Right Panel — Producer Circular Loop:**

- Panel title at top: "**Producer Loop**" in Literata serif
- Draw a large circular flow diagram filling most of the right panel.
- Use exactly **6 chunky bold curved arrow segments**, clockwise, alternating forest green #4a7c59 and warm amber #705c30. Match the arrow weight and curve style from the reference image — thick, confident, cleanly rounded.
- **Center of the circle:** White circular area containing the loop name "**[LOOP_NAME_CAPS]**" in bold Literata, centered, broken across 2–3 lines if needed.
- **4 stage labels outside the circle**, use `[NARRATIVE_3_TEXT]` and `[NARRATIVE_4_TEXT]` to generate the four relevant labels, in ALL CAPS Nunito Sans. Place labels at the following clock positions:

  | Clock position | Stage Label |
  |---|---|
  | 1 o'clock | LABEL |
  | 4 o'clock | LABEL |
  | 7 o'clock | LABEL |
  | 11 o'clock | LABEL |

---

**Visual Formatting:**
- ALL CAPS for stage labels; title case for panel headers and reward box text.
- Break all labels across 2 lines rather than truncating.
- Keep the layout airy — do not crowd the circle or the scene.

### Integration Mapping for your App

| Variable | XML Field | Location |
| :--- | :--- | :--- |
| **[LOOP_NAME_CAPS]** | `loop_name` | Loop badge center |
| **[NARRATIVE_1_TEXT]** | `narrative_1` | Left panel scene subject |
| **[NARRATIVE_2_TEXT]** | `narrative_2` | Center reward box |
| **[NARRATIVE_3_TEXT]** | `narrative_3` | Loop action labels |
| **[NARRATIVE_4_TEXT]** | `narrative_4` | Loop closing mechanism labels |