import xml.etree.ElementTree as ET


def _parse_llm_output(text):
    start = text.find("<response>")
    end = text.find("</response>")
    if start == -1 or end == -1:
        return "Could not locate <response> block in LLM output.", "", []

    try:
        root = ET.fromstring(text[start:end + len("</response>")])
    except ET.ParseError as e:
        return f"XML parse error: {e}", "", []

    def t(el, tag):
        val = el.findtext(tag)
        return val.strip() if val else ""

    profile = t(root, "profile_analysis")
    themes  = t(root, "summary")

    concepts = []
    for el in root.findall("concepts/concept"):
        assumptions = [
            a.text.strip()
            for a in el.findall("assumptions/assumption")
            if a.text
        ]
        analogues = [
            {
                "company":   t(c, "company"),
                "case_id":   t(c, "case_id"),
                "rationale": t(c, "rationale"),
            }
            for c in el.findall("citations/citation")
        ]
        img = el.find("prototype_image")
        image_fields = {
            "loop_name_caps": t(img, "loop_name")    if img is not None else "",
            "narrative_1":    t(img, "narrative_1")  if img is not None else "",
            "narrative_2":    t(img, "narrative_2")  if img is not None else "",
            "narrative_3":    t(img, "narrative_3")  if img is not None else "",
            "narrative_4":    t(img, "narrative_4")  if img is not None else "",
        }
        concepts.append({
            "number":       int(el.get("number", 0)),
            "title":        t(el, "title"),
            "mechanic":     t(el, "mechanic"),
            "user":         t(el, "target_user"),
            "value_chain":  t(el, "value_chain_inefficiency"),
            "pressure":     t(el, "pressure_addressed"),
            "description":  t(el, "description"),
            "prototype":    t(el, "prototype_sentence"),
            "image_fields": image_fields,
            "verdict":      t(el, "prototype_verdict"),
            "alignment":    t(el, "outcome_alignment"),
            "assumptions":  assumptions,
            "analogues":    analogues,
        })

    return profile, themes, sorted(concepts, key=lambda c: c["number"])