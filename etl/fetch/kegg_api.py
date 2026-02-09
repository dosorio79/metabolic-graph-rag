import re
import time
import requests
from typing import Optional

BASE_URL = "https://rest.kegg.jp"


# ============================================================
# KEGG FETCH LAYER
# ============================================================
def fetch_kegg_data(
    endpoint: str,
    entries: str,
    *,
    timeout: int = 20,
    retries: int = 3,
    session: Optional[requests.Session] = None,
    backoff: float = 1.5,
) -> str:
    """
    Generic KEGG REST API fetcher.
    """

    entries = entries.strip()
    url = f"{BASE_URL}/{endpoint}/{entries}"

    sess = session or requests.Session()

    for attempt in range(1, retries + 1):
        try:
            response = sess.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            if attempt == retries:
                print(f"[KEGG ERROR] {url} -> {e}")
                return ""

            sleep_time = backoff * attempt
            print(f"[KEGG RETRY {attempt}/{retries}] waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)

    return ""


# ============================================================
# MODULE EXTRACTION
# ============================================================
def extract_kegg_modules(text: str) -> list[str]:
    """
    Extract module IDs (Mxxxxx) from pathway entry.
    """
    return sorted(set(re.findall(r'M\d{5}', text)))


# ============================================================
# REACTION EXTRACTION
# ============================================================
def extract_kegg_reactions(text: str) -> list[str]:
    """
    Extract reaction IDs (Rxxxxx) from module entry.
    """
    return sorted(set(re.findall(r'R\d{5}', text)))


# ============================================================
# REACTION PARSER
# ============================================================
def parse_reaction_entry(text: str) -> dict:
    """
    Parse KEGG reaction entry into substrates/products/enzymes.
    """

    equation = ""
    enzymes = []

    capture_equation = False
    capture_enzyme = False

    for line in text.splitlines():

        # ---- EQUATION ----
        if line.startswith("EQUATION"):
            capture_equation = True
            capture_enzyme = False
            equation = line.replace("EQUATION", "").strip()
            continue

        if capture_equation:
            if line.startswith(" "):
                equation += " " + line.strip()
            else:
                capture_equation = False

        # ---- ENZYME ----
        if line.startswith("ENZYME"):
            capture_enzyme = True
            enzymes.extend(line.replace("ENZYME", "").split())
            continue

        if capture_enzyme:
            if line.startswith(" "):
                enzymes.extend(line.strip().split())
            else:
                capture_enzyme = False

    if "=" not in equation:
        return {"substrates": [], "products": [], "enzymes": enzymes}

    left, right = equation.split("=")

    substrates = re.findall(r'C\d{5}', left)
    products = re.findall(r'C\d{5}', right)

    return {
        "substrates": sorted(set(substrates)),
        "products": sorted(set(products)),
        "enzymes": sorted(set(enzymes)),
    }


# ============================================================
# FULL INGESTION PIPELINE
# ============================================================
def ingest_pathway(pathway_id: str) -> list[dict]:
    """
    Pipeline:
        Pathway -> Modules -> Reactions -> Parsed reactions
    """

    session = requests.Session()

    print(f"\nFetching pathway: {pathway_id}")
    pathway_text = fetch_kegg_data("get", pathway_id, session=session)

    modules = extract_kegg_modules(pathway_text)
    print(f"Modules discovered: {len(modules)}")

    all_reactions = set()

    for module in modules:
        module_text = fetch_kegg_data("get", module, session=session)
        reactions = extract_kegg_reactions(module_text)
        all_reactions.update(reactions)

    print(f"Total reactions collected: {len(all_reactions)}")

    parsed_reactions = []

    for reaction_id in sorted(all_reactions):
        reaction_text = fetch_kegg_data("get", reaction_id, session=session)

        parsed = parse_reaction_entry(reaction_text)
        parsed["reaction_id"] = reaction_id

        parsed_reactions.append(parsed)

    print(f"Parsed reactions: {len(parsed_reactions)}")

    return parsed_reactions


# ============================================================
# TEST EXECUTION
# ============================================================
if __name__ == "__main__":
    reactions = ingest_pathway("hsa00010")

    if reactions:
        print("\nExample reaction:")
        print(reactions[0])
