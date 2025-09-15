import re
import json
import time
import csv
import queue
import urllib.parse as up
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser as robotparser

# ──────────────────────────────────────────────────────────────────────────────
# Repo layout anchors (based on your project structure)
# GEO/
#   client docs/
#     client_input_template.json  (INTAKE JSON)
#     crawl_outputs/
#   geo-platform/
#     crawler/
#       crawl_site.py  (this file)
# ──────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parent.parent
CLIENT_DOCS_DIR = REPO_ROOT / "client docs"
INTAKE_PATH  = CLIENT_DOCS_DIR / "client_input_template.json"
OUTPUT_ROOT = CLIENT_DOCS_DIR / "crawl_outputs"

# ──────────────────────────────────────────────────────────────────────────────
# Intake helpers (JSON-first, tolerant to fenced blocks)
# ──────────────────────────────────────────────────────────────────────────────

def load_intake_json(filepath: Path) -> Dict[str, Any]:
    """
    Load the intake JSON from file.

    Supports:
      1) File is pure JSON.
      2) File contains a fenced code block ```json ... ``` with JSON.
      3) Last {...} JSON object in file.
    """
    raw = filepath.read_text(encoding="utf-8").strip()

    # Try direct JSON
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Fenced block
    m = re.search(r"```json\s*([\s\S]*?)\s*```", raw, flags=re.IGNORECASE)
    if m:
        block = m.group(1).strip()
        return json.loads(block)

    # Trailing object
    m2 = re.search(r"\{[\s\S]*\}\s*$", raw)
    if m2:
        return json.loads(m2.group(0))

    raise ValueError("No valid JSON found in intake file.")

def extract_domain_from_ctx(ctx: Dict[str, Any]) -> Optional[str]:
    # Prefer schema: website_details.primary_domain, fallback to 'domain'
    return ((ctx.get("website_details") or {}).get("primary_domain")
            or ctx.get("domain"))

def extract_cms_from_ctx(ctx: Dict[str, Any]) -> Optional[str]:
    cms = ((ctx.get("website_details") or {}).get("cms_platform")
           or ctx.get("cms_provided"))
    return cms.strip() if isinstance(cms, str) else None

def extract_priority_paths_from_ctx(ctx: Dict[str, Any]) -> List[str]:
    """
    Convert JSON 'content_priorities.most_important_pages' into site paths.

    Recognizes common keys like:
      - homepage -> "/"
      - apply_page -> "/apply"
      - client_interest_page -> "/client-interest"
      - about_page -> "/about"
      - projects_page -> "/projects"
      - people_page -> "/people"

    If intake includes explicit paths under:
      - content_priorities.priority_paths OR top-level priority_paths
    prefer that list.
    """
    cp = (ctx.get("content_priorities") or {})
    explicit = ctx.get("priority_paths") or cp.get("priority_paths")
    if isinstance(explicit, list) and all(isinstance(x, str) for x in explicit):
        paths = explicit
    else:
        names = cp.get("most_important_pages") or []
        if not isinstance(names, list):
            names = []
        mapping = {
            "homepage": "/",
            "apply_page": "/apply",
            "client_interest_page": "/client-interest",
            "about_page": "/about",
            "projects_page": "/projects",
            "people_page": "/people",
            "donate_page": "/donate",
            "contact_page": "/contact",
            "recruitment_page": "/recruitment",
            "interview_process_page": "/interview-process",
            "services_page": "/consulting",
        }
        paths: List[str] = []
        for name in names:
            if not isinstance(name, str):
                continue
            key = name.strip().lower()
            if key in mapping:
                paths.append(mapping[key])
            elif key.startswith("/"):
                paths.append(key)
    # de-dup while preserving order
    seen = set()
    dedup = []
    for p in paths:
        if p not in seen:
            dedup.append(p); seen.add(p)
    return dedup

# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────

def slugify_domain(url: str) -> str:
    s = url.replace("https://", "").replace("http://", "")
    return "".join(ch if ch.isalnum() or ch in "-._" else "_" for ch in s)

def same_host(a: str, b: str) -> bool:
    return urlparse(a).netloc.lower() == urlparse(b).netloc.lower()

def norm_url(base: str, href: str) -> Optional[str]:
    if not href:
        return None
    u = urljoin(base, href)
    pr = urlparse(u)
    pr = pr._replace(fragment="")
    return up.urlunparse(pr)

def fetch(url: str, timeout=15):
    try:
        t0 = time.time()
        resp = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "GEO-Crawler/1.0"}
        )
        ms = int((time.time() - t0) * 1000)
        return resp, None, ms
    except Exception as e:
        return None, str(e), None

def parse_sitemaps(sitemap_urls: List[str]) -> Set[str]:
    urls = set()
    for sm in sitemap_urls:
        resp, _, _ = fetch(sm)
        if not resp or resp.status_code != 200:
            continue
        try:
            root = ET.fromstring(resp.text)
        except Exception:
            continue
        tag = root.tag.lower()
        if tag.endswith("sitemapindex"):
            for loc in root.iter():
                if loc.tag.lower().endswith("loc") and loc.text:
                    urls.update(parse_sitemaps([loc.text.strip()]))
        elif tag.endswith("urlset"):
            for loc in root.iter():
                if loc.tag.lower().endswith("loc") and loc.text:
                    urls.add(loc.text.strip())
    return urls

def read_robots(domain: str):
    """
    Returns: (RobotFileParser, sitemap_urls: list[str], robots_ok: bool)
    """
    rp = robotparser.RobotFileParser()
    robots_url = urljoin(domain, "/robots.txt")
    resp, _, _ = fetch(robots_url, timeout=10)
    sitemap_urls, robots_ok = [], False
    if resp and resp.status_code == 200:
        robots_ok = True
        text = resp.text
        rp.parse(text.splitlines())
        for line in text.splitlines():
            if line.lower().startswith("sitemap:"):
                sitemap_urls.append(line.split(":", 1)[1].strip())
    else:
        rp.set_url(robots_url)
        try:
            rp.read()
            robots_ok = True  # if we didn't error, consider it found/readable
        except Exception:
            robots_ok = False
    return rp, sitemap_urls, robots_ok

# ──────────────────────────────────────────────────────────────────────────────
# Extraction helpers (per page)
# ──────────────────────────────────────────────────────────────────────────────

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\(?\+?1?\)?[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{4}")
DATE_RE  = re.compile(r"(?i)(?:updated|last\s*updated|published)\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}|\d{4}-\d{2}-\d{2})")

def collect_meta(soup: BeautifulSoup) -> Tuple[Dict, Optional[str], Optional[str]]:
    og = {}
    for m in soup.select('meta[property^="og:"]'):
        prop = (m.get("property") or "").replace("og:", "").strip()
        if prop:
            og[prop] = m.get("content", "")
    desc = soup.find("meta", attrs={"name": "description"})
    canonical = soup.find("link", rel=lambda v: v and "canonical" in v)
    return og, (desc.get("content", "") if desc else None), (canonical.get("href") if canonical else None)

def headings_map(soup: BeautifulSoup) -> Dict[str, List[str]]:
    return {
        "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
        "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
    }

def nav_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    urls = []
    for a in soup.select("nav a[href]"):
        u = norm_url(base_url, a.get("href"))
        if u:
            urls.append(u)
    return list(dict.fromkeys(urls))

def breadcrumb_labels(soup: BeautifulSoup) -> List[str]:
    crumbs = []
    for ol in soup.select('ol.breadcrumb, nav[aria-label="breadcrumb"] ol'):
        for a in ol.select("a, li"):
            t = a.get_text(" ", strip=True)
            if t:
                crumbs.append(t)
    return [c for c in crumbs if c]

def ld_json_blocks(soup: BeautifulSoup) -> List[Dict]:
    data = []
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            txt = s.get_text(strip=True)
            if not txt:
                continue
            obj = json.loads(txt)
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict):
                        data.append({"schema_type": item.get("@type"), "raw_json": item})
            elif isinstance(obj, dict):
                data.append({"schema_type": obj.get("@type"), "raw_json": obj})
        except Exception:
            continue
    return data

def detect_faq(soup: BeautifulSoup, text: str) -> Tuple[bool, List[Dict]]:
    # Prefer schema.org FAQPage
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            obj = json.loads(s.get_text(strip=True))
            items = obj if isinstance(obj, list) else [obj]
            for it in items:
                if isinstance(it, dict) and it.get("@type") == "FAQPage":
                    qas = []
                    for q in it.get("mainEntity", []) or []:
                        qq = (q.get("name") or "").strip()
                        aa = ""
                        ans = q.get("acceptedAnswer")
                        if isinstance(ans, dict):
                            aa = (ans.get("text") or "").strip()
                        qas.append({"q": qq, "a": aa})
                    return True, qas
        except Exception:
            pass
    # Fallback: crude Q/A regex proximity in visible text
    snips = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for i, ln in enumerate(lines):
        if re.match(r"(?i)^(q|question)\s*[:\-]", ln):
            for j in range(i + 1, min(i + 6, len(lines))):
                if re.match(r"(?i)^(a|answer)\s*[:\-]", lines[j]):
                    qtxt = re.sub(r"(?i)^(q|question)\s*[:\-]\s*", "", ln).strip()
                    atxt = re.sub(r"(?i)^(a|answer)\s*[:\-]\s*", "", lines[j]).strip()
                    if qtxt and atxt:
                        snips.append({"q": qtxt, "a": atxt})
                    break
    return (len(snips) > 0), snips

def extract_business_info(soup: BeautifulSoup, text: str) -> Dict[str, Optional[str]]:
    email = None
    m = EMAIL_RE.search(text)
    if m:
        email = m.group(0)

    phone = None
    p = PHONE_RE.search(text)
    if p:
        phone = p.group(0)

    addr = None
    adr_tag = soup.find("address")
    if adr_tag:
        t = adr_tag.get_text(" ", strip=True)
        if t:
            addr = t

    if not addr:
        footer = soup.find("footer")
        if footer:
            ft = footer.get_text(" ", strip=True)
            if "IN" in ft or "Indiana" in ft or re.search(r"\d{5}", ft):
                addr = ft

    return {"email": email, "phone": phone, "address": addr}

def extract_dates(soup: BeautifulSoup, text: str) -> Dict[str, Optional[str]]:
    pub = None
    upd = None
    for t in soup.find_all("time"):
        dt = t.get("datetime") or t.get_text(strip=True)
        if dt and not pub:
            pub = dt
        elif dt and not upd:
            upd = dt
    for m in DATE_RE.finditer(text):
        val = m.group(1)
        if not upd:
            upd = val
        else:
            pub = pub or val
    return {"published": pub, "updated": upd}

def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))

def find_links(soup: BeautifulSoup, base_url: str) -> Tuple[List[str], List[str], List[Tuple[str, str]]]:
    internal, external, rel_edges = [], [], []
    base_host = urlparse(base_url).netloc.lower()
    for a in soup.find_all("a", href=True):
        u = norm_url(base_url, a["href"])
        if not u:
            continue
        host = urlparse(u).netloc.lower()
        if host == base_host or host == "":
            internal.append(u)
            rel_edges.append((base_url, u))
        else:
            external.append(u)
            rel_edges.append((base_url, u))
    return list(dict.fromkeys(internal)), list(dict.fromkeys(external)), rel_edges

def extract_forms(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    forms = []
    for frm in soup.find_all("form"):
        action = norm_url(base_url, frm.get("action") or base_url)
        method = (frm.get("method") or "GET").upper()
        inputs = []
        for inp in frm.find_all(["input", "select", "textarea"]):
            inputs.append({
                "name": inp.get("name"),
                "type": inp.name if inp.name != "input" else (inp.get("type") or "text"),
                "required": inp.has_attr("required")
            })
        validation_attrs = []
        for attr in ["required", "pattern", "minlength", "maxlength", "step", "min", "max"]:
            if any(i.get("required") if attr == "required" else inp.has_attr(attr)
                   for inp in frm.find_all(["input", "select", "textarea"])):
                validation_attrs.append(attr)
        honeypot = any(inp for inp in frm.find_all("input")
                       if inp.get("type") == "text" and "honeypot" in (inp.get("name", "") + inp.get("id", "")).lower())
        captcha = any("captcha" in (c.get("class") or []) for c in frm.find_all(True))
        forms.append({
            "page_url": base_url,
            "action": action,
            "method": method,
            "inputs": inputs,
            "validation_attrs": validation_attrs,
            "honeypot_present": honeypot,
            "captcha_present": captcha
        })
    return forms

def script_hints_and_endpoints(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    hints = []
    # External scripts
    for s in soup.find_all("script", src=True):
        src = norm_url(base_url, s["src"])
        if src:
            hints.append({"source_url": base_url, "type": "script_hint", "endpoint": src, "method": "GET"})
    # Inline fetch/XHR hints (very simple)
    for s in soup.find_all("script"):
        txt = (s.get_text() or "")
        for m in re.finditer(r"""fetch\((['"])(https?://[^'"]+)\1""", txt):
            hints.append({"source_url": base_url, "type": "xhr", "endpoint": m.group(2), "method": "GET"})
        for m in re.finditer(r"""['"](/api/[^'"]+)['"]""", txt):
            ep = norm_url(base_url, m.group(1))
            if ep:
                hints.append({"source_url": base_url, "type": "xhr", "endpoint": ep, "method": "GET"})
    return hints

# ──────────────────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PageRecord:
    url: str
    status: Optional[int]
    fetch_ms: Optional[int]
    content_bytes: Optional[int]
    title: Optional[str]
    meta_description: Optional[str]
    og: Dict
    canonical: Optional[str]
    headings: Dict[str, List[str]]
    nav: List[str]
    breadcrumbs: List[str]
    word_count: int
    structured_data: List[Dict]
    faq_detected: bool
    faq_snippets: List[Dict]
    dates: Dict[str, Optional[str]]
    business_info: Dict[str, Optional[str]]
    internal_links: List[str]
    external_links: List[str]
    categories: List[str]
    priority_page: bool
    conversion_elements: Dict[str, bool]
    cms: Optional[str]
    extraction_notes: List[str]

# ──────────────────────────────────────────────────────────────────────────────
# Readiness scoring helpers
# ──────────────────────────────────────────────────────────────────────────────

def score_api_testing(api_inventory: Dict[str, list], forms_count: int) -> Dict:
    """
    API Testing = 'Can AI interact with this site dynamically?'
    Heuristics:
      + JSON/XHR endpoints discovered
      + # of distinct endpoints
      + presence of form POST actions
    """
    discovered = api_inventory.get("discovered", [])
    endpoints = {d.get("endpoint") for d in discovered if d.get("endpoint")}
    json_like = [d for d in discovered if str(d.get("content_type","")).lower().startswith("application/json")]
    xhr_like = [d for d in discovered if d.get("type") in ("xhr", "script_hint")]

    # crude scoring (0–100)
    score = 0
    score += min(len(endpoints), 20) * 3                  # up to 60 pts
    score += min(len(json_like), 10) * 3                  # up to 30 pts
    score += min(forms_count, 5) * 2                      # up to 10 pts
    score = max(0, min(score, 100))

    ready = score >= 40  # threshold for “AI can likely interact”

    signals = {
        "distinct_endpoints": len(endpoints),
        "json_endpoints": len(json_like),
        "xhr_or_script_hints": len(xhr_like),
        "forms_detected": forms_count,
    }
    notes = []
    if not endpoints:
        notes.append("No endpoints discovered from scripts/XHR.")
    if not json_like:
        notes.append("No JSON content types observed during sampling.")
    if forms_count == 0:
        notes.append("No forms detected for structured submissions.")
    if ready:
        notes.append("Basic API signals present for programmatic interaction.")
    else:
        notes.append("Insufficient dynamic endpoints for AI interaction.")

    return {
        "ai_interaction_ready": bool(ready),
        "score": int(score),
        "signals": signals,
        "notes": notes,
    }

def score_industry_comparison(pages_sample: list, perf_rows: list, sitemap_found: bool, robots_found: bool) -> Dict:
    """
    Industry Comparison = 'Is this site optimized for search engines and AI discovery?'
    Heuristics:
      + title & meta description presence
      + og tags presence
      + structured data blocks (ld+json)
      + mobile viewport present
      + sitemap & robots
      + response time baseline
    """
    n = len(pages_sample) or 1
    title_ok = sum(1 for p in pages_sample if p.get("title"))
    desc_ok  = sum(1 for p in pages_sample if p.get("meta_description"))
    og_ok    = sum(1 for p in pages_sample if p.get("og"))
    ld_ok    = sum(1 for p in pages_sample if p.get("structured_data"))

    mv_ok = 0
    for (_url, _ms, _bytes, mobile_viewport) in perf_rows:
        if str(mobile_viewport).lower() in ("true", "1"):
            mv_ok += 1

    fast_ok = 0
    for (_url, fetch_ms, *_rest) in perf_rows:
        try:
            if fetch_ms != "" and int(fetch_ms) <= 2000:
                fast_ok += 1
        except Exception:
            pass

    score = 0
    score += round((title_ok / n) * 15)
    score += round((desc_ok / n) * 15)
    score += round((og_ok / n) * 10)
    score += round((ld_ok / n) * 25)
    score += round((mv_ok / max(len(perf_rows), 1)) * 15)
    score += 10 if sitemap_found else 0
    score += 5  if robots_found  else 0
    score += round((fast_ok / max(len(perf_rows), 1)) * 10)
    score = max(0, min(score, 100))

    ready = score >= 60

    signals = {
        "pct_title": round((title_ok / n) * 100, 1),
        "pct_meta_description": round((desc_ok / n) * 100, 1),
        "pct_og_tags": round((og_ok / n) * 100, 1),
        "pct_structured_data": round((ld_ok / n) * 100, 1),
        "pct_mobile_viewport": round((mv_ok / max(len(perf_rows), 1)) * 100, 1),
        "pct_fast_fetch_ms": round((fast_ok / max(len(perf_rows), 1)) * 100, 1),
        "sitemap_present": bool(sitemap_found),
        "robots_present": bool(robots_found),
    }

    notes = []
    if signals["pct_structured_data"] < 30:
        notes.append("Low structured data coverage; add schema.org for key pages.")
    if signals["pct_meta_description"] < 60:
        notes.append("Many pages missing meta descriptions.")
    if signals["pct_mobile_viewport"] < 80:
        notes.append("Mobile viewport tag missing on many pages.")
    if signals["pct_fast_fetch_ms"] < 70:
        notes.append("Performance baseline is slower than recommended (<=2s).")
    if ready:
        notes.append("On par with common SEO/AI discovery expectations.")
    else:
        notes.append("Not yet competitive on core SEO/AI discovery signals.")

    return {
        "seo_ai_discovery_ready": bool(ready),
        "score": int(score),
        "signals": signals,
        "notes": notes,
    }

# ──────────────────────────────────────────────────────────────────────────────
# Priority & CTA helpers
# ──────────────────────────────────────────────────────────────────────────────

def is_priority_url(url: str, domain: str, priority_paths: List[str]) -> bool:
    base = domain.rstrip("/").lower()
    u = url.rstrip("/").lower()
    for p in priority_paths:
        p_norm = (p or "").strip().lower()
        if p_norm in ("", "/"):
            if u == base:
                return True
        else:
            if u.endswith(p_norm.strip("/")):
                return True
    return False

def derive_cta_keywords(ctx: Dict[str, Any]) -> List[str]:
    objs = (ctx.get("optimization_goals") or {}).get("primary_objectives", [])
    acts = (ctx.get("content_priorities") or {}).get("key_conversion_actions", [])
    seeds = ["apply", "apply now", "join us", "contact", "inquire", "get in touch"]
    joined = " ".join(objs + acts).lower()
    if "application" in joined or "apply" in joined:
        seeds += ["student application", "submit application"]
    if "inquir" in joined or "client" in joined or "project" in joined:
        seeds += ["client interest", "project inquiry", "request project", "work with us"]
    # unique + lower
    return sorted({s.lower() for s in seeds})

def has_any_cta(soup: BeautifulSoup, keywords: List[str]) -> bool:
    for el in soup.find_all(["a","button"]):
        t = (el.get_text(" ", strip=True) or "").lower()
        if any(k in t for k in keywords):
            return True
    return False

# ──────────────────────────────────────────────────────────────────────────────
# Crawl
# ──────────────────────────────────────────────────────────────────────────────

def crawl_site(ctx: Dict[str, Any],
               domain: str,
               cms: Optional[str],
               priority_paths: List[str],
               max_pages: int = 200,
               max_depth: int = 3) -> Dict[str, Path]:

    out_dir = OUTPUT_ROOT / slugify_domain(domain)
    out_dir.mkdir(parents=True, exist_ok=True)

    # robots & sitemaps
    rp, robots_sitemaps, robots_found = read_robots(domain)
    sitemap_urls: Set[str] = set(robots_sitemaps)
    # If intake provides sitemaps, merge them
    provided_sitemaps = ctx.get("sitemap_urls") or []
    if provided_sitemaps:
        sitemap_urls |= set(provided_sitemaps)
    if not sitemap_urls:
        sitemap_urls.add(urljoin(domain, "/sitemap.xml"))

    # Build seed set
    seed_urls = set()
    if sitemap_urls:
        seed_urls |= parse_sitemaps(list(sitemap_urls))

    # priority URLs
    for p in priority_paths:
        seed_urls.add(urljoin(domain, p))

    # ensure homepage is included
    seed_urls.add(domain.rstrip("/") + "/")

    # BFS crawl with robots & same-host constraint
    q = queue.Queue()
    seen: Set[str] = set()
    depth_map: Dict[str, int] = {}

    # prime queue
    for u in seed_urls:
        if same_host(u, domain):
            q.put(u)
            depth_map[u] = 0

    pages_path = out_dir / "pages.jsonl"
    edges_path = out_dir / "edges.csv"
    forms_path = out_dir / "forms.jsonl"
    perf_path  = out_dir / "performance.csv"
    api_path   = out_dir / "api_endpoints.json"
    summary_path = out_dir / "summary.json"

    # writers
    pages_f = open(pages_path, "w", encoding="utf-8")
    forms_f = open(forms_path, "w", encoding="utf-8")
    edges_f = open(edges_path, "w", newline="", encoding="utf-8")
    perf_f  = open(perf_path, "w", newline="", encoding="utf-8")
    edges_writer = csv.writer(edges_f); edges_writer.writerow(["from_url","to_url","rel"])
    perf_writer  = csv.writer(perf_f);  perf_writer.writerow(["url","fetch_ms","content_bytes","mobile_viewport"])

    api_inventory: Dict[str, List[Dict]] = {"discovered": []}

    # accumulators for scoring
    forms_detected_total = 0
    perf_rows_for_scoring: List[Tuple[str, Optional[int], Optional[int], bool]] = []
    pages_for_scoring: List[Dict] = []

    cta_keywords = derive_cta_keywords(ctx)

    count = 0

    while not q.empty() and count < max_pages:
        url = q.get()
        if url in seen:
            continue
        depth = depth_map.get(url, 0)
        if depth > max_depth:
            continue

        # robots
        try:
            if not rp.can_fetch("*", url):
                continue
        except Exception:
            pass

        resp, err, ms = fetch(url, timeout=15)
        status = resp.status_code if resp else None
        html = resp.text if (resp and resp.text) else ""
        size = len(html.encode("utf-8")) if html else 0

        # politeness: small sleep after requests to avoid hammering
        time.sleep(0.15)

        mobile_viewport = False
        title = meta_desc = canonical = None
        og = {}
        headings = {"h1": [], "h2": []}
        nav = []
        breadcrumbs = []
        sdata = []
        faq_detected = False
        faq_snippets = []
        dates = {"published": None, "updated": None}
        biz = {"email": None, "phone": None, "address": None}
        internal_links: List[str] = []
        external_links: List[str] = []
        categories: List[str] = []
        conversion = {"has_apply_cta": False, "forms_present": False}
        extraction_notes: List[str] = []
        wc = 0

        if resp and resp.ok and ("text/html" in (resp.headers.get("Content-Type", "")) or html):
            soup = BeautifulSoup(html, "html.parser")
            # title
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            # meta/og/canonical
            og, meta_desc, canonical = collect_meta(soup)
            # viewport
            mobile_viewport = soup.find("meta", attrs={"name": "viewport"}) is not None
            # headings
            headings = headings_map(soup)
            # nav & breadcrumbs
            nav = nav_links(soup, url)
            breadcrumbs = breadcrumb_labels(soup)
            # ld+json
            sdata = ld_json_blocks(soup)
            # faq
            faq_detected, faq_snippets = detect_faq(soup, soup.get_text(" ", strip=True))
            # dates
            page_text = soup.get_text(" ", strip=True)
            dates = extract_dates(soup, page_text)
            # business info
            biz = extract_business_info(soup, page_text)
            # word count
            wc = word_count(page_text)
            # links
            internal_links, external_links, rel_edges = find_links(soup, url)
            # write edges
            for to in internal_links:
                edges_writer.writerow([url, to, "internal"])
            for to in external_links:
                edges_writer.writerow([url, to, "external"])
            # forms
            forms = extract_forms(soup, url)
            for f in forms:
                forms_f.write(json.dumps(f, ensure_ascii=False) + "\n")
            conversion["forms_present"] = len(forms) > 0
            forms_detected_total += len(forms)
            # CTA detection (intake-guided)
            if has_any_cta(soup, cta_keywords):
                conversion["has_apply_cta"] = True
            # api/script hints
            hints = script_hints_and_endpoints(soup, url)
            if hints:
                api_inventory["discovered"].extend(hints)

            # queue internal links
            for nxt in internal_links:
                if nxt not in seen and same_host(nxt, domain):
                    if nxt not in depth_map:
                        depth_map[nxt] = depth + 1
                    q.put(nxt)

            # page record
            rec = PageRecord(
                url=url, status=status, fetch_ms=ms, content_bytes=size,
                title=title, meta_description=meta_desc, og=og, canonical=canonical,
                headings=headings, nav=nav, breadcrumbs=breadcrumbs, word_count=wc,
                structured_data=sdata, faq_detected=faq_detected, faq_snippets=faq_snippets,
                dates=dates, business_info=biz, internal_links=internal_links,
                external_links=external_links, categories=categories,
                priority_page=is_priority_url(url, domain, priority_paths),
                conversion_elements=conversion, cms=cms, extraction_notes=extraction_notes
            )
        else:
            # non-HTML or error
            rec = PageRecord(
                url=url, status=status, fetch_ms=ms, content_bytes=size,
                title=None, meta_description=None, og={}, canonical=None,
                headings={"h1": [], "h2": []}, nav=[], breadcrumbs=[], word_count=0,
                structured_data=[], faq_detected=False, faq_snippets=[],
                dates={"published": None, "updated": None},
                business_info={"email": None, "phone": None, "address": None},
                internal_links=[], external_links=[], categories=[],
                priority_page=is_priority_url(url, domain, priority_paths),
                conversion_elements={"has_apply_cta": False, "forms_present": False},
                cms=cms, extraction_notes=[f"non_html_or_error: {err or status}"]
            )

        # write pages
        pages_f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
        # write perf (and keep for scoring)
        perf_writer.writerow([url, ms or "", size or "", mobile_viewport])
        perf_rows_for_scoring.append((url, ms or "", size or "", mobile_viewport))

        # minimal signals for industry comparison scoring
        pages_for_scoring.append({
            "title": rec.title,
            "meta_description": rec.meta_description,
            "og": rec.og,
            "structured_data": rec.structured_data,
        })

        seen.add(url)
        count += 1

    pages_f.close(); forms_f.close(); edges_f.close(); perf_f.close()

    # de-duplicate api endpoints and optionally probe some
    dedup = {}
    for item in api_inventory["discovered"]:
        key = (item.get("source_url"), item.get("type"), item.get("endpoint"))
        if key not in dedup:
            dedup[key] = item
    api_inventory["discovered"] = list(dedup.values())

    # lightweight sampling (HEAD/GET) for JSON detection
    for entry in api_inventory["discovered"][:30]:  # cap sampling
        ep = entry.get("endpoint")
        if not ep:
            continue
        try:
            r = requests.head(ep, timeout=6, allow_redirects=True)
            if r.status_code == 405:
                r = requests.get(ep, timeout=6, allow_redirects=True)
            ct = r.headers.get("Content-Type", "")
            entry["status_sample"] = r.status_code
            entry["content_type"] = ct
            if "application/json" in ct.lower():
                try:
                    r2 = requests.get(ep, timeout=6)
                    entry["status_sample"] = r2.status_code
                    entry["content_type"] = r2.headers.get("Content-Type", "")
                    j = r2.json()
                    if isinstance(j, dict):
                        entry["sample_keys"] = list(j.keys())[:10]
                except Exception:
                    pass
        except Exception:
            pass

    (out_dir / "api_endpoints.json").write_text(json.dumps(api_inventory, indent=2, ensure_ascii=False), encoding="utf-8")

    # compute readiness sections
    api_section = score_api_testing(api_inventory, forms_detected_total)
    industry_section = score_industry_comparison(
        pages_sample=pages_for_scoring,
        perf_rows=perf_rows_for_scoring,
        sitemap_found=bool(sitemap_urls),
        robots_found=robots_found
    )

    # quick roll-ups
    fast_pct = industry_section["signals"]["pct_fast_fetch_ms"]
    viewport_pct = industry_section["signals"]["pct_mobile_viewport"]

    # warning if many sitemap URLs are off-host
    offhost_in_sitemap = 0
    for u in list(seed_urls):
        if not same_host(u, domain):
            offhost_in_sitemap += 1

    notes = []
    if offhost_in_sitemap > 0:
        notes.append(f"{offhost_in_sitemap} sitemap URL(s) are off-host; possible external blog/CDN or misconfigured sitemap.")

    # If intake contact info exists but not found on pages, flag it for discoverability
    intake_contact = (ctx.get("contact_information") or {})
    if intake_contact.get("primary_email"):
        if not any("@" in (p.get("business_info", {}) or {}).get("email", "") for p in []):
            # we didn't aggregate page records here; leave as general hint
            notes.append("Intake provides a primary email, but pages may not expose it consistently.")

    # summary
    summary = {
        "domain": domain,
        "cms": cms,
        "client_project": ctx.get("client_project"),
        "optimization_goals": ctx.get("optimization_goals"),
        "pages_crawled": count,
        "output_dir": str(out_dir),
        "limits": {"max_pages": max_pages, "max_depth": max_depth},
        "assessments": {
            "api_testing": {
                "label": "Can AI interact with this site dynamically?",
                **api_section
            },
            "industry_comparison": {
                "label": "Is this site optimized for search engines and AI discovery?",
                **industry_section
            },
            "missing_consequences": [
                "Dynamic AI capabilities (API testing)",
                "Static SEO optimization (industry comparison)"
            ]
        },
        "fast_fetch_pct": fast_pct,
        "mobile_viewport_coverage_pct": viewport_pct,
        "robots_txt_exists": bool(robots_found),
        "sitemaps_discovered_count": len(sitemap_urls),
        "notes": notes
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "pages": pages_path,
        "edges": edges_path,
        "forms": forms_path,
        "performance": perf_path,
        "api": api_path,
        "summary": summary_path,
    }

# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not INTAKE_PATH.exists():
        raise FileNotFoundError(f"Intake file not found: {INTAKE_PATH}")

    ctx = load_intake_json(INTAKE_PATH)

    # Optionally adjust crawl limits for low budget/short timeline projects
    tech = ctx.get("technical_constraints") or {}
    budget = (tech.get("budget_level") or "").lower()
    max_pages_default = 120 if budget == "low" else 200
    max_depth_default = 3

    domain = extract_domain_from_ctx(ctx)
    cms = extract_cms_from_ctx(ctx) or None
    priority = extract_priority_paths_from_ctx(ctx)

    if not domain:
        raise RuntimeError("No primary_domain found in intake JSON (website_details.primary_domain).")

    print(f"[crawl] Domain: {domain}")
    print(f"[crawl] CMS: {cms}")
    print(f"[crawl] Priority pages: {priority}")

    outputs = crawl_site(
        ctx=ctx,
        domain=domain,
        cms=cms,
        priority_paths=priority,
        max_pages=max_pages_default,
        max_depth=max_depth_default
    )

    print("[crawl] Done. Outputs:")
    for k, v in outputs.items():
        print(f"  - {k}: {v}")
