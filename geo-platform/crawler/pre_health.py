import re
import requests
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Optional, Dict, Any

# ──────────────────────────────────────────────────────────────────────────────
# Paths anchored to your repo layout
# GEO/
#   client docs/
#     context.md   (now contains JSON)
#     health_checks/
#   geo-platform/
#     crawler/
#       pre_health.py  (this file)
# ──────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent                  # .../GEO/geo-platform/crawler
REPO_ROOT  = SCRIPT_DIR.parent.parent                         # .../GEO
CLIENT_DOCS_DIR = REPO_ROOT / "client docs"                   # .../GEO/client docs
INTAKE_PATH  = CLIENT_DOCS_DIR / "client_input_template.json"  # JSON content
OUTPUT_DIR = CLIENT_DOCS_DIR / "health_checks"                # .../GEO/client docs/health_checks


# ──────────────────────────────────────────────────────────────────────────────
# Intake loading (JSON-first, with a tolerant fallback)
# ──────────────────────────────────────────────────────────────────────────────

def load_intake_json(filepath: Path) -> Dict[str, Any]:
    """
    Load the intake JSON from context.md.

    Supports:
      1) File is pure JSON.
      2) File contains a fenced code block ```json ... ``` with JSON.
    Raises ValueError if JSON cannot be parsed.
    """
    raw = filepath.read_text(encoding="utf-8").strip()

    # Try direct JSON first
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Try to locate a fenced ```json ... ``` block
    m = re.search(
        r"```json\s*([\s\S]*?)\s*```",
        raw,
        flags=re.IGNORECASE
    )
    if m:
        block = m.group(1).strip()
        try:
            return json.loads(block)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON from fenced block: {e}") from e

    # As a last resort, try to find the first {...} block and parse it
    m2 = re.search(r"\{[\s\S]*\}\s*$", raw)
    if m2:
        try:
            return json.loads(m2.group(0))
        except Exception as e:
            raise ValueError(f"Failed to parse JSON from trailing object: {e}") from e

    raise ValueError("No valid JSON found in intake file.")


def extract_domain_from_ctx(ctx: Dict[str, Any]) -> Optional[str]:
    """
    Pull primary domain from intake JSON:
      website_details.primary_domain
    """
    return (ctx.get("website_details") or {}).get("primary_domain")


def extract_cms_from_ctx(ctx: Dict[str, Any]) -> Optional[str]:
    """
    Pull CMS platform from intake JSON:
      website_details.cms_platform
    """
    cms = (ctx.get("website_details") or {}).get("cms_platform")
    if isinstance(cms, str):
        return cms.strip()
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Pre-health check
# ──────────────────────────────────────────────────────────────────────────────

def pre_health_check(domain_url: str, cms_provided: Optional[str] = None) -> dict:
    """
    Run a pre-health check on a given domain URL.
    Assumes CMS is provided by the intake JSON (no detection/verification).
    """
    results = {
        "domain": domain_url,
        "ssl_valid": domain_url.startswith("https"),
        "response_time_ms": None,
        "mobile_friendly": False,
        "robots_txt_exists": False,
        "sitemap_urls": [],
        "cms_provided": cms_provided
    }

    try:
        # Reachability & latency
        resp = requests.get(domain_url, timeout=10, allow_redirects=True, headers={"User-Agent": "GEO-PreHealth/1.0"})
        results["response_time_ms"] = int(resp.elapsed.total_seconds() * 1000)

        # robots.txt & sitemaps from robots
        robots_url = urljoin(domain_url, "/robots.txt")
        robots_resp = requests.get(robots_url, timeout=5, headers={"User-Agent": "GEO-PreHealth/1.0"})
        results["robots_txt_exists"] = robots_resp.status_code == 200

        if results["robots_txt_exists"]:
            for line in robots_resp.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    results["sitemap_urls"].append(line.split(":", 1)[1].strip())

        # fallback to /sitemap.xml
        if not results["sitemap_urls"]:
            sitemap_url = urljoin(domain_url, "/sitemap.xml")
            sitemap_resp = requests.get(sitemap_url, timeout=5, headers={"User-Agent": "GEO-PreHealth/1.0"})
            if sitemap_resp.status_code == 200:
                results["sitemap_urls"].append(sitemap_url)

        # basic mobile check via viewport meta
        soup = BeautifulSoup(resp.text, "html.parser")
        results["mobile_friendly"] = soup.find("meta", attrs={"name": "viewport"}) is not None

    except Exception as e:
        results["error"] = str(e)

    return results


# ──────────────────────────────────────────────────────────────────────────────
# Persistence
# ──────────────────────────────────────────────────────────────────────────────

def slugify_domain(url: str) -> str:
    """Create a safe filename from a domain URL."""
    s = url.replace("https://", "").replace("http://", "")
    return "".join(ch if ch.isalnum() or ch in "-._" else "_" for ch in s)

def save_results(results: dict, outdir: Path = OUTPUT_DIR) -> Path:
    """Save health check results to JSON under GEO/client docs/health_checks/"""
    outdir.mkdir(parents=True, exist_ok=True)
    domain_slug = slugify_domain(results["domain"])
    path = outdir / f"{domain_slug}_health.json"
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[pre-health] Saved results to: {path}")
    return path


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not INTAKE_PATH.exists():
        raise FileNotFoundError(f"Intake file not found at: {INTAKE_PATH}")

    # Load intake JSON (from context.md)
    ctx = load_intake_json(INTAKE_PATH)

    domain = extract_domain_from_ctx(ctx)
    cms = extract_cms_from_ctx(ctx)

    if not domain:
        raise RuntimeError("No primary_domain found in intake JSON (website_details.primary_domain).")

    print(f"Running pre-health check for: {domain}")
    print(f"Using intake (JSON): {INTAKE_PATH}")
    results = pre_health_check(domain_url=domain, cms_provided=cms)
    print(results)
    save_results(results)  # -> GEO/client docs/health_checks/<domain>_health.json
