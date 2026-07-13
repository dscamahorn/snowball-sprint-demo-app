import config


def load_rag_context() -> str:
    cpr = config.load_file(config.CPR_RAG)
    fwu = config.load_file(config.FWU_RAG)
    bas = config.load_file(config.BAS_RAG)
    return (
        f"[Consumer Packaging Reuse]\n{cpr}\n\n"
        f"[Food Waste and Upcycling]\n{fwu}\n\n"
        f"[B2B Asset Sharing Platforms]\n{bas}"
    )