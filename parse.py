import mailbox
import tldextract
from collections import defaultdict
from email.utils import parseaddr
import email.utils
import os

MBOX_PATH = "mb"

ACCOUNT_KEYWORDS_FILE = "account_keywords.txt"
NEWSLETTER_KEYWORDS_FILE = "newsletter_keywords.txt"
IGNORE_DOMAINS_FILE = "ignore_domains.txt"

def load_list(path):
    with open(path, "r", encoding="utf-8") as f:
        return {
            line.strip().lower()
            for line in f
            if line.strip() and not line.startswith("#")
        }

ACCOUNT_KEYWORDS = load_list(ACCOUNT_KEYWORDS_FILE)
NEWSLETTER_KEYWORDS = load_list(NEWSLETTER_KEYWORDS_FILE)
IGNORE_DOMAINS = load_list(IGNORE_DOMAINS_FILE)

stats = defaultdict(lambda: {
    "count": 0,
    "score": 0,
    "first_seen": None,
    "last_seen": None
})

def parse_date(msg):
    date_str = msg.get("Date")
    if not date_str:
        return None
    try:
        return email.utils.parsedate_to_datetime(date_str)
    except Exception:
        return None

def score_message(msg):
    subject = (msg.get("Subject", "") or "").lower()
    score = 0

    for kw in ACCOUNT_KEYWORDS:
        if kw in subject:
            if kw == "welcome":
                score += 100  # just override 
            else:
                score += 3

    for kw in NEWSLETTER_KEYWORDS:
        if kw in subject:
            score -= 2

    return score

def process_mbox(path):
    mbox = mailbox.mbox(path)

    for msg in mbox:
        _, addr = parseaddr(msg.get("From", ""))
        if "@" not in addr:
            continue

        ext = tldextract.extract(addr)
        if not ext.domain or not ext.suffix:
            continue

        domain = f"{ext.domain}.{ext.suffix}".lower()

        # Ignore domains 
        if any(domain.endswith(d) for d in IGNORE_DOMAINS):
            continue

        date = parse_date(msg)
        score = score_message(msg)

        s = stats[domain]
        s["count"] += 1
        s["score"] += score

        if date:
            if not s["first_seen"] or date < s["first_seen"]:
                s["first_seen"] = date
            if not s["last_seen"] or date > s["last_seen"]:
                s["last_seen"] = date

process_mbox(MBOX_PATH)

def confidence(s):
    if s["score"] >= 10:
        return "HIGH"
    elif s["score"] >= 3:
        return "MEDIUM"
    else:
        return "LOW"

print(f"{'DOMAIN':30} {'CONF':6} {'COUNT':5} {'FIRST SEEN':12} {'LAST SEEN':12}")
print("-" * 75)

for domain, s in sorted(
    stats.items(),
    key=lambda x: x[1]["score"],
    reverse=True
):
    first = s["first_seen"].date().isoformat() if s["first_seen"] else "-"
    last = s["last_seen"].date().isoformat() if s["last_seen"] else "-"
    print(
        f"{domain:30} "
        f"{confidence(s):6} "
        f"{s['count']:5} "
        f"{first:12} "
        f"{last:12}"
    )

