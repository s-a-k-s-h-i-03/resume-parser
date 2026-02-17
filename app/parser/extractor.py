import re
from app.parser.keywords import (
    SKILLS_KEYWORDS
)
def confidence_from_text(text):
    if not text:
        return 0.0
    length = len(text.split())
    return min(length / 50.0, 1.0)

# -------------------------------------------------
# SECTION HEADERS (FOR FUTURE USE: EXPERIENCE, ETC.)
# -------------------------------------------------

SECTION_HEADERS = {
    "experience": [
        "experience", "work experience", "professional experience"
    ],
    "projects": [
        "projects", "academic projects"
    ],
    "awards": [
    "activities & achievements",
    "activities and achievements",
    "achievements",
    "awards",
    "honors"],
    

    "publications": [
        "publications", "books", "research"
    ],

    "certifications": [
    "certifications",
    "certification",
    "certificate",
    "certificates",
    "courses","Coursework","COURSEWORK",
    "professional courses", 
    "professional certifications",
    "training & certifications",
    "courses & certifications",
    "courses",
    "training"
]

}
# -----------------------------
# AWARDS / ACTIVITIES FILTERING
# -----------------------------

AWARD_POSITIVE_WORDS = {
    "winner", "rank", "award", "prize", "honor", "honours",
    "first", "second", "third"
}

ACTIVITY_NEGATIVE_WORDS = {
    "volunteer", "member", "participant",
    "organizer", "organised", "organized",
    "lead", "leadership", "representative"
}

# -------------------------------------------------
# COMMON UTILITIES
# -------------------------------------------------

def safe_value(value):
    if value is None:
        return ""
    value = str(value).strip()
    if value.lower() == "nan":
        return ""
    return value


def split_sections(text: str) -> dict:
    """
    Rule-based section splitter.
    Currently used only to PREPARE for experience / AI.
    Does NOT affect existing extraction.
    """
    text_lower = text.lower()
    matches = []

    for section, keywords in SECTION_HEADERS.items():
        for kw in keywords:
            m = re.search(rf"(?:\n|^)\s*{kw}\s*(?:\n|:)", text_lower)
            if m:
                matches.append((m.start(), section))
                break

    matches.sort(key=lambda x: x[0])

    sections = {k: "" for k in SECTION_HEADERS.keys()}

    for i, (start, section) in enumerate(matches):
        end = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        sections[section] = text[start:end].strip()

    # fallback if no headers found
    if not any(sections.values()):
        sections["experience"] = text

    return sections
def clean_achievements(text):
    if not text:
        return ""

    stop_headers = [
        "personal details",
        "languages",
        "date of birth",
        "dob",
        "address"
    ]

    lines = []

    for line in text.split("\n"):
        l = line.strip()

        if not l:
            continue

        # stop if personal info section starts
        l_lower = l.lower()

# reject activities
        if any(w in l_lower for w in ACTIVITY_NEGATIVE_WORDS):
            continue

# keep only awards
        if not any(w in l_lower for w in AWARD_POSITIVE_WORDS):
            continue


        # normalize formatting
        l = l.replace("|", " | ")
        l = re.sub(r"\s+", " ", l)

        # remove bullets
        l = l.lstrip("•-* ")

        lines.append(l)

    return "\n".join(lines)

# -------------------------------------------------
# FIELD EXTRACTION (RULE-BASED)
# -------------------------------------------------

def extract_email(text):
    match = re.search(
        r"[a-zA-Z0-9._%+-]+@(gmail|hotmail|yahoo)\.com",
        text,
        re.IGNORECASE
    )
    return safe_value(match.group() if match else "")


def extract_mobile(text):
    candidates = re.findall(r"\+?\d[\d\s\-]{8,14}\d", text)

    for c in candidates:
        digits = re.sub(r"\D", "", c)

        if len(digits) == 10:
            return digits
        if len(digits) > 10 and digits[-10:].startswith(tuple("6789")):
            return digits[-10:]

    return ""


def extract_name(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        if 2 <= len(line.split()) <= 4:
            return line.title()
    return ""


def extract_skills(text):
    text_lower = text.lower()
    found = []

    for skill in SKILLS_KEYWORDS:
        if re.search(rf"\b{re.escape(skill)}\b", text_lower):
            found.append(skill)

    return ", ".join(sorted(set(found)))

DEGREE_DEFINITIONS = {
    "10th": {
        "patterns": [
            r"\b10th\b",
            r"\bclass 10\b",
            r"\bssc\b",
            r"\bsecondary school\b"
        ]
    },
    "12th": {
        "patterns": [
            r"\b12th\b",
            r"\bclass 12\b",
            r"\bhsc\b",
            r"\bhigher secondary\b",
            r"\bhigher school certificate\b"
        ]
    },
    "BCA": {
        "patterns": [
            r"\bbca\b",
            r"\bbachelor of computer applications\b"
        ]
    },
    "BTECH": {
        "patterns": [
            r"\bbtech\b",
            r"\bbachelor of technology\b"
        ]
    },
    "BE": {
        "patterns": [
            r"\bbe\b",
            r"\bbachelor of engineering\b"
        ]
    },
    "MCA": {
        "patterns": [
            r"\bmca\b",
            r"\bmaster of computer applications\b"
        ]
    },
    "MTECH": {
        "patterns": [
            r"\bmtech\b",
            r"\bmaster of technology\b"
        ]
    }
}

def extract_education(text):
    if not text:
        return "No education data available"

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    lower = [l.lower() for l in lines]

    STOP_SECTIONS = [
        "skills", "experience", "projects",
        "certifications", "awards", "activities"
    ]

    DEGREE_RULES = [
        ("10th", [r"\b10th\b", r"\bssc\b"]),
        ("12th", [r"\b12th\b", r"\bhsc\b"]),
        ("BCA", [r"\bbca\b"]),
        ("BSC", [r"\bbsc\b", r"\bbcs\b"]),
        ("BTECH", [r"\bbtech\b"]),
        ("BE", [r"\bb\.e\b", r"\bbachelor of engineering\b"]),
        ("MCA", [r"\bmca\b"]),
        ("MSC", [r"\bmsc\b"]),
        ("MTECH", [r"\bmtech\b"]),
    ]

    percent_pattern = re.compile(r"\b\d{2,3}(?:\.\d{1,2})?%")
    cgpa_pattern = re.compile(r"\b([5-9]\.\d{1,2}|10(?:\.0{1,2})?)\s*cgpa\b", re.I)



    results = {}
    has_score = False

    for i, line in enumerate(lower):

        if any(re.search(rf"^{stop}\b", line) for stop in STOP_SECTIONS):
            break

        for degree, patterns in DEGREE_RULES:

            if degree in results:
                continue

            if any(re.search(p, line) for p in patterns):

                score = None

                for j in range(i, min(i + 3, len(lines))):

                    # check on ORIGINAL line (not lower)
                    original = re.sub(r"\b20\d{2}\b", "", lines[j])

                    m = percent_pattern.search(original)
                    if m:
                        score = m.group()
                        has_score = True
                        break

                    m = cgpa_pattern.search(original)
                    if m:
                        score = m.group().upper()
                        has_score = True
                        break

                results[degree] = score
                break

    if not results:
        return "No education data available"

    order = ["10th", "12th", "BCA", "BSC", "BTECH", "BE",
             "MCA", "MSC", "MTECH"]

    output = []

    if has_score:
        for d in order:
            if d in results and results[d]:
                output.append(f"{d} {results[d]}")
    else:
        for d in order:
            if d in results:
                output.append(d)

    return "\n".join(output)


CERT_ISSUER_HINTS = [
    "ibm", "google", "microsoft", "amazon", "aws",
    "coursera", "udemy", "edx", "simplilearn",
    "nasscom", "tcs", "ion", "infosys",
    "oracle", "cisco", "meta", "skillup",
    "smartbridge", "accenture"
]
EDUCATION_BLOCK_WORDS = {
    "mca", "bca", "ssc", "hsc",
    "school", "college", "university"
}

ACTIVITY_BLOCK_WORDS = {
    "volunteer", "hackathon", "fest",
    "competition", "winner", "representative"
}

CERT_TITLE_HINTS = {
    "certification", "certified", "course",
    "training", "cloud", "django",
    "analytics", "computing"
}

def extract_certifications(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    results = []

    for line in lines:
        clean = line.lstrip("•-* ").strip()

        # Must be structured
        if clean.count("|") < 2:
            continue

        parts = [p.strip() for p in clean.split("|")]
        if len(parts) < 3:
            continue

        title, issuer, year = parts[0], parts[1], parts[2]
        title_l = title.lower()

        # Year must be valid
        if not re.search(r"\b(19|20)\d{2}\b", year):
            continue

        # ❌ Reject education
        if any(w in title_l for w in EDUCATION_BLOCK_WORDS):
            continue

        # ❌ Reject activities / achievements
        if any(w in title_l for w in ACTIVITY_BLOCK_WORDS):
            continue

        # ❌ Reject non-certification titles
        # must not look like a skill-only line
        if re.fullmatch(r"[a-zA-Z\s]+", title) and len(title.split()) <= 2:
            continue


        # ❌ Reject short / skill-only titles
        if len(title.split()) < 3:
            continue

        results.append(f"{title} | {issuer} | {year}")

    if not results:
        return "No certification data available"

    return "\n".join(results)

# -------------------------------------------------
# MAIN ROW EXTRACTION (CALLED BY PIPELINE)
# -------------------------------------------------
    AWARD_POSITIVE_WORDS = {
    "winner", "rank", "award", "prize", "honor", "honours",
    "first", "second", "third" }

    ACTIVITY_NEGATIVE_WORDS = {
    "volunteer", "member", "participant",
    "organizer", "organised", "organized",
    "lead", "leadership", "representative"
    }

def extract_row(text):
    # section split prepared (not yet used)
    sections = split_sections(text)

    

    education_text = extract_education(text)
    certifications_text = extract_certifications(text)
    experience_text = sections.get("experience", "")
    publications_text = sections.get("publications", "")
    raw_achievements = sections.get("awards", "")
    cleaned_achievements = clean_achievements(raw_achievements)

    return {
    "Name": extract_name(text),
    "Email": extract_email(text),
    "Mobile": extract_mobile(text),
    "Skills": extract_skills(text),

    "Education": education_text,
    "Certifications": certifications_text,
    "Experience": experience_text,
    "Publications": publications_text,
    "Awards": cleaned_achievements,

}


    # confidence values (NOT shown in UI yet)
    confidence_from_text(experience_text),
    confidence_from_text(projects_text),
    confidence_from_text(awards_text),
    confidence_from_text(publications_text),



