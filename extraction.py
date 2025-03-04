import logging
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from urllib3.util.retry import Retry

# --- Setup Three Loggers ---
# General extraction logger
logger_extraction = logging.getLogger("extraction")
logger_extraction.setLevel(logging.DEBUG)
fh_extraction = logging.FileHandler("extraction.log")
fh_extraction.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger_extraction.addHandler(fh_extraction)

# Failures logger
logger_failures = logging.getLogger("failures")
logger_failures.setLevel(logging.ERROR)
fh_failures = logging.FileHandler("extraction_failures.log")
fh_failures.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger_failures.addHandler(fh_failures)

# Statistics logger
logger_stats = logging.getLogger("stats")
logger_stats.setLevel(logging.INFO)
fh_stats = logging.FileHandler("extraction_stats.log")
fh_stats.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger_stats.addHandler(fh_stats)

# --- Global Extraction Statistics (Thread-Safe) ---
extraction_stats = {"total": 0, "success": 0, "fail": 0, "fail_types": {}}
stats_lock = threading.Lock()


def update_stats(success: bool, error_type: str = None):
    with stats_lock:
        extraction_stats["total"] += 1
        if success:
            extraction_stats["success"] += 1
        else:
            extraction_stats["fail"] += 1
            if error_type:
                extraction_stats["fail_types"][error_type] = (
                    extraction_stats["fail_types"].get(error_type, 0) + 1
                )


def clean_text(text: str) -> str:
    """Improve text cleaning by removing extra whitespace and boilerplate phrases."""
    text = re.sub(r"\s+", " ", text)  # collapse whitespace
    boilerplate = ["Read more", "Sponsored", "Copyright", "Follow us", "Learn more"]
    for phrase in boilerplate:
        text = text.replace(phrase, "")
    return text.strip()


def create_session():
    """Create a requests session with custom headers and retry logic."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[403, 404, 406, 429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0 Safari/537.36"
            )
        }
    )
    return session


def should_ignore(url: str, ignore_domains: list[str]) -> bool:
    """Return True if the URL should be ignored based on its domain."""
    return any(domain.lower() in url.lower() for domain in ignore_domains)


def extract_text(
    url: str,
    session: requests.Session,
    rate_limiting_domains: list[str],
    ignore_domains: list[str] = [],
) -> str:
    # Check if URL is in ignore list
    if should_ignore(url, ignore_domains):
        logger_extraction.info(f"Ignoring URL (in ignore list): {url}")
        update_stats(
            False, error_type="Ignoring URL"
        )  # Consider it "failed" if url ignored
        return ""  # return the URL itself as a fallback
    logger_extraction.info(f"Fetching URL: {url}")
    try:
        # Custom preprocessing: delay if URL matches any rate-limited domain
        if any(domain in url for domain in rate_limiting_domains):
            time.sleep(2)
        response = session.get(url, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)
            if not text.strip():
                text = soup.get_text(separator=" ", strip=True)
            text = clean_text(text)
            update_stats(True)
            logger_extraction.info(f"Successfully extracted HTML text for URL: {url}")
            return text
        elif "application/pdf" in content_type:
            try:
                from pdfminer.high_level import extract_text as pdf_extract_text

                # Limit PDF extraction to 10 pages
                pdf_text = pdf_extract_text(BytesIO(response.content), maxpages=10)
                pdf_text = clean_text(pdf_text)
                update_stats(True)
                logger_extraction.info(
                    f"Successfully extracted PDF text for URL: {url}"
                )
                return pdf_text
            except Exception as e:
                error_msg = f"PDF extraction error: {str(e)}"
                update_stats(False, error_type=error_msg)
                logger_failures.error(
                    f"Error extracting PDF text from {url}: {error_msg}"
                )
                return f"PDF content from {url} (extraction failed)"
        else:
            update_stats(True)
            logger_extraction.info(
                f"Non-HTML/PDF content for URL: {url}. Using URL as fallback."
            )
            return url
    except Exception as e:
        error_msg = str(e)
        update_stats(False, error_type=error_msg)
        logger_failures.error(f"Error fetching {url}: {error_msg}")
        return ""


def parallel_extraction(
    urls: list[str],
    max_workers: int,
    rate_limiting_domains: list[str],
    ignore_domains: list[str] = [],
) -> list[str]:
    """Extract texts from URLs in parallel with progress indication."""
    texts = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                extract_text,
                url,
                create_session(),
                rate_limiting_domains,
                ignore_domains,
            ): url
            for url in urls
        }
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Extracting texts"
        ):
            texts.append(future.result())
    texts = [txt if txt and len(txt) > 50 else url for txt, url in zip(texts, urls)]
    return texts


def get_embeddings(
    urls: list[str],
    model_name: str = "all-MiniLM-L6-v2",
    max_workers: int = 10,
    rate_limiting_domains: list[str] = [],
    ignore_domains: list[str] = [],
):
    """Extract texts in parallel and compute embeddings."""
    texts = parallel_extraction(
        urls,
        max_workers=max_workers,
        rate_limiting_domains=rate_limiting_domains,
        ignore_domains=ignore_domains,
    )
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings, texts


def log_extraction_stats():
    """Log and print summary statistics about extraction results."""
    total = extraction_stats["total"]
    success = extraction_stats["success"]
    fail = extraction_stats["fail"]
    percent_success = (success / total * 100) if total > 0 else 0
    percent_fail = (fail / total * 100) if total > 0 else 0
    logger_stats.info("Extraction Stats Summary:")
    logger_stats.info(f"Total URLs processed: {total}")
    logger_stats.info(f"Success: {success} ({percent_success:.2f}%)")
    logger_stats.info(f"Failures: {fail} ({percent_fail:.2f}%)")
    for err_type, count in extraction_stats["fail_types"].items():
        logger_stats.info(f"  {err_type}: {count}")
    print("Extraction Stats Summary:")
    print(f"Total URLs processed: {total}")
    print(f"Success: {success} ({percent_success:.2f}%)")
    print(f"Failures: {fail} ({percent_fail:.2f}%)")
    print("Failures by type:")
    for err_type, count in extraction_stats["fail_types"].items():
        print(f"  {err_type}: {count}")
