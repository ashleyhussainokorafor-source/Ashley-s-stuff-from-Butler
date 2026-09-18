#!/usr/bin/env python3
"""HCA Daily — reply to YouTube comments with a RELEVANT link.

Every reply matches the commenter's actual situation to something of Ashley's:
a video that answers it, a paid product, or the free scorecard.

Design rules (deliberate — do not "simplify" them away):

  * DETECT THE COMMENT TYPE FIRST. A reply that opens "Great question" on a
    comment that isn't a question is the single fastest way to look like a bot.
    Types: question | help | praise | story | opinion.
  * ONE link per reply, and ONLY when it genuinely answers them. Product links
    go only to people actively asking about interviews/resumes/getting hired.
  * Word-boundary matching for risky keywords. Substring matching once sent a
    medical-coding video to someone switching off a computer-science degree,
    because "coding" appears inside "Computer Science" talk.
  * Quota: commentThreads.insert = 50 units, ~10,000/day -> stop at ~170 and
    resume next run. Never hammer it.
  * Templates vary so hundreds of replies don't read as copy-paste.

Usage:
  reply_to_comments.py --dry-run --limit 15
  reply_to_comments.py --limit 25          # pilot batch
  reply_to_comments.py --type question     # only real questions
"""
import argparse
import json
import os
import random
import re
import sys
import time
from collections import Counter

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CACHE = "/data/business/hca-daily/ops/comments_cache.json"
STATE = "/data/business/hca-daily/ops/reply_state.json"
LOG = "/data/business/hca-daily/ops/OPS_LOG.md"
TOKEN = "/data/youtube_token.json"

QUOTA_SAFE_BATCH = 170
SITE = "https://thehcadaily.com"

VIDEOS = {
    "_2oxkikIX5c": "I Wish I Knew This Before",
    "VBpe6A337kM": "Degree in Health Science",
    "h6c_YZMfaJI": "What Does a Healthcare Administrator Do?",
    "u7yaSUU3cHE": "Health Management vs Healthcare Management",
    "3VFounyMwzE": "Hospital Administration vs Healthcare Administration",
    "7I8BojfeeN0": "Do you NEED to be a nurse?",
    "2cz7ZaU9umA": "How I Got a Healthcare Administration Job",
    "8tagUtXCMwU": "Studying Business? Get an MHA",
    "99NqhMYJZLc": "Healthcare Administration vs Healthcare Leadership",
    "1IYTe45i8Zk": "Is it Hard to Get a Job?",
    "FPp4Avmu_aI": "So You're Doing an MPA?",
    "h_VjpTxgNZE": "A Guide to Careers in Healthcare Administration",
    "u4Rz-um5rA0": "Start Working in Health Insurance",
    "YwUElzkTuSc": "Should I Get an MBA for Healthcare Administration",
    "D4wxSPhNvOI": "Why I Got an MHA",
    "E6v8hZxw9Ko": "MHA vs MPH: Salary Showdown",
    "XdM_V8OTYqc": "5 Secrets to Getting a Job",
    "2HNtjcxQfq0": "How To Start a Healthcare Admin Career With Zero Experience",
    "ZiVgcU4Msx4": "Use Networking to get your next job",
    "IMtDWbyfFCY": "How to find a Mentor in Healthcare Administration",
    "T9hXaz1kOLs": "HOW to Network as an UNDERGRAD",
    "WL7P6Ke3nVs": "It's Never TOO Late",
    "oZaw3GB4HAA": "Is Healthcare Administration WORTH it?",
    "XmbO9_R_9Po": "Can You Get into HCA with a Business Degree?",
    "aYj1BKYDD4Y": "Do you need clinical experience?",
    "uk2MP143goM": "Nailing Your HCA Interview",
    "WzblFFIuoyM": "The Most Significant Interview Skill You Need",
    "49uPHjg8sXU": "The Top 3 Things You NEED to Share in an Interview",
    "8Luijnbwux4": "Interviews with Healthcare Administrators",
    "UlQNKkTLnaE": "Build a Career in Health Insurance",
    "_UouZ5NhjJY": "Medical Coders WATCH THIS",
    "4WBcemXx7xc": "Job Posting Keywords",
    "RTtxtGhZeo0": "GET A JOB",
    "VQija_9sUeM": "Get That Job You Want",
    "8oWjNa6HbUc": "The Ultimate Guide to a Master's in HCA",
    "N5Mq2pwzfHA": "Applying to an MHA program",
    "xqbo_TiEkkw": "MHA. No science required",
    "Kd6rv1a_qXI": "Unlocking Your Dream Job in Hospital Administration Overseas",
    "WF1ZdbFBH10": "Data Science to Healthcare Leadership",
    "ELyj199xlpM": "How to GET YOUR FOOT IN THE DOOR",
    "2sZe0qqDDYg": "How to Start a Healthcare Business",
    "4--uy17smLQ": "10 Things YOU Need to Know",
}


def yt(vid):
    return f"https://youtu.be/{vid}"


# --------------------------------------------------------------- comment type
PRAISE = ["thank you", "thanks", "thankyou", "thx", "great video", "so helpful",
          "very helpful", "informative", "i appreciate", "god bless", "love this",
          "amazing", "awesome", "excellent", "best video", "well explained",
          "you explained", "found this", "just found", "glad i found"]
HELP = ["how do i", "how can i", "how do you", "any advice", "need help", "what should i",
        "can someone", "please help", "any tips", "i need guidance", "guide me",
        "where do i start", "how would you", "any suggestions", "looking for advice"]
QUESTION_WORDS = re.compile(
    r"^\s*(how|what|which|where|when|why|who|can|do|does|did|is|are|should|would|will|"
    r"any|anyone|am i|has anyone|does anyone)\b", re.I)


def detect_type(text):
    raw = text.strip()
    low = raw.lower()
    if any(p in low for p in PRAISE):
        # "...thanks, but how do I X?" is still a question
        if "?" in raw and QUESTION_WORDS.match(raw.split("?")[0].strip() or "x"):
            return "question"
        return "praise" if not any(h in low for h in HELP) else "help"
    if "?" in raw or QUESTION_WORDS.match(raw):
        return "help" if any(h in low for h in HELP) else "question"
    if any(h in low for h in HELP):
        return "help"
    # long personal narrative = a story; short assertion = an opinion
    if len(raw) > 200 and re.search(r"\bi (am|was|have|had|'m|'ve)\b", low):
        return "story"
    return "opinion"


# --------------------------------------------------------------- topic rules
# (topic, [regexes]) — regex with word boundaries; FIRST match wins.
TOPICS = [
    ("_skip_negative", [r"\b(scam|ripoff|ripped off|useless degree|worthless)\b"]),
    ("too_late", [r"\btoo late\b", r"\btoo old\b", r"\bat my age\b", r"\bi'?m (4|5|6)\d\b",
                  r"\b(late 3|late 4|late 5)0s\b", r"\bsecond career\b", r"\b2nd career\b",
                  r"\bstarting over\b"]),
    ("zero_exp", [r"\bno experience\b", r"\bzero experience\b", r"\bwithout experience\b",
                  r"\bno (healthcare|clinical|medical) (experience|background)\b",
                  r"\bcareer (change|changer|switch)", r"\bswitching careers?\b",
                  r"\btransition(ing)? (in|into|to)\b", r"\bno background in\b"]),
    ("mentor_network", [r"\bmentor", r"\bnetwork(ing)?\b", r"\bno one in the (field|industry)\b",
                        r"\bconnect with (people|someone|professionals)\b"]),
    ("interview", [r"\binterview", r"\btell me about yourself\b", r"\bstar method\b"]),
    ("resume_job", [r"\bresume\b", r"\bcv\b", r"\bapplying for\b", r"\bjob (search|market|hunt)\b",
                    r"\bget (a )?(job|hired)\b", r"\bfind a job\b", r"\bland a job\b",
                    r"\bentry[ -]level\b", r"\bfoot in the door\b", r"\bhard to get a job\b"]),
    ("jobs_with_degree", [r"\bwhat jobs\b", r"\bwhich jobs\b", r"\bwhat (kind of )?(jobs|work|roles?|positions?)\b",
                          r"\bjob options\b", r"\bcareer options\b", r"\bwhat can i do with\b",
                          r"\bafter (the|my) degree\b", r"\bafter (i )?graduat"]),
    ("mha_mba", [r"\bmha vs mba\b", r"\bmba (vs|or) mha\b", r"\bshould i get an mba\b"]),
    ("mph", [r"\bmph\b", r"\bmaster'?s in public health\b"]),
    ("mha", [r"\bmha\b", r"\bmaster'?s in healthcare admin", r"\bmasters in healthcare"]),
    ("business_degree", [r"\bbusiness (degree|admin|major)\b", r"\bstudying business\b", r"\bbba\b"]),
    ("nurse_clinical", [r"\bnurse\b", r"\bnursing\b", r"\bclinical (background|experience)\b",
                        r"\bradiology\b", r"\bmedical assistant\b", r"\bdo i need clinical\b"]),
    ("mgmt_vs_admin", [r"\bdifference between\b", r"\bmanagement vs\b", r"\bvs (administration|management)\b"]),
    ("hospital_vs_hca", [r"\bhospital admin", r"\bhospital administration\b"]),
    ("leadership", [r"\bleadership\b", r"\bdirector\b", r"\bexecutive\b", r"\bc-suite\b"]),
    ("salary", [r"\bsalar", r"\bhow much (do|does|can)\b", r"\bpay\b", r"\bcompensation\b"]),
    ("worth_it", [r"\bworth it\b", r"\bworth the\b"]),
    ("day_in_life", [r"\bday in the life\b", r"\bstress(ful| level)?\b",
                     r"\bwhat does (a|an) .{0,25}(administrator|admin)\b"]),
    ("insurance", [r"\binsurance\b", r"\brevenue cycle\b", r"\bclaims\b"]),
    ("coding", [r"\bmedical cod(er|ing)\b", r"\bcpc\b", r"\bicd-?10\b"]),
    ("degree_choice", [r"\bhealth science\b", r"\bhsci\b", r"\bwhich degree\b",
                       r"\bwhat degree\b", r"\bcomputer science\b", r"\bswitch(ing)? (my )?(major|degree)\b"]),
    ("overseas", [r"\boverseas\b", r"\babroad\b", r"\bvisa\b", r"\bmalayalam\b", r"\bnigeria\b"]),
    ("mpa", [r"\bmpa\b", r"\bpublic administration\b"]),
]
COMPILED = [(t, [re.compile(p, re.I) for p in pats]) for t, pats in TOPICS]

RESOURCE = {
    "too_late":         (["WL7P6Ke3nVs", "2HNtjcxQfq0"], None),
    "zero_exp":         (["2HNtjcxQfq0", "ELyj199xlpM", "WL7P6Ke3nVs"], None),
    "mentor_network":   (["IMtDWbyfFCY", "T9hXaz1kOLs", "ZiVgcU4Msx4"], None),
    "interview":        (["uk2MP143goM", "49uPHjg8sXU", "WzblFFIuoyM"], "vault"),
    "resume_job":       (["XdM_V8OTYqc", "1IYTe45i8Zk", "2cz7ZaU9umA"], "vault"),
    "jobs_with_degree": (["h_VjpTxgNZE", "1IYTe45i8Zk", "RTtxtGhZeo0"], "vault"),
    "mha_mba":          (["YwUElzkTuSc", "D4wxSPhNvOI"], None),
    "mph":              (["E6v8hZxw9Ko"], None),
    "mha":              (["D4wxSPhNvOI", "8oWjNa6HbUc", "N5Mq2pwzfHA"], None),
    "business_degree":  (["XmbO9_R_9Po", "8tagUtXCMwU"], None),
    "nurse_clinical":   (["7I8BojfeeN0", "aYj1BKYDD4Y"], None),
    "mgmt_vs_admin":    (["u7yaSUU3cHE", "h6c_YZMfaJI"], None),
    "hospital_vs_hca":  (["3VFounyMwzE", "u7yaSUU3cHE"], None),
    "leadership":       (["99NqhMYJZLc", "WF1ZdbFBH10"], None),
    "salary":           (["E6v8hZxw9Ko", "h6c_YZMfaJI"], None),
    "worth_it":         (["oZaw3GB4HAA", "4--uy17smLQ"], None),
    "day_in_life":      (["h6c_YZMfaJI", "8Luijnbwux4"], None),
    "insurance":        (["u4Rz-um5rA0", "UlQNKkTLnaE"], None),
    "coding":           (["_UouZ5NhjJY"], None),
    "degree_choice":    (["VBpe6A337kM", "XmbO9_R_9Po"], None),
    "overseas":         (["Kd6rv1a_qXI"], None),
    "mpa":              (["FPp4Avmu_aI"], None),
}
VAULT = (f"the Interview Answer Vault has 156 real questions with the exact answer "
         f"scripts if you want the deeper version — {SITE}/vault")


def classify(text):
    for topic, pats in COMPILED:
        for p in pats:
            if p.search(text):
                return topic
    return None


# --------------------------------------------------------------- reply copy
Q_OPEN = ["Great question.", "Really good question.", "This comes up a lot.",
          "Good question — and a common one.", "I get asked this a lot."]
Q_CLOSE = ["Hope that helps!", "Good luck with it.", "Wishing you the best.",
           "Happy to help."]
STORY_OPEN = ["Thanks for sharing this.", "Appreciate you sharing your experience.",
              "This is a really useful perspective.", "Love hearing this."]
OPINION_OPEN = ["Solid point.", "Good perspective.", "You're right about this.",
                "Really good point."]
PRAISE_OPEN = ["Thank you so much!", "This made my day — thank you.", "So glad it helped!",
               "Thank you, that means a lot."]
PRAISE_CLOSE = ["Best of luck with everything.", "Wishing you the best with your studies.",
                "Rooting for you.", "Keep going — you've got this."]


def build_reply(kind, topic, text):
    vids, product = RESOURCE.get(topic, (None, None))
    vid = random.choice(vids) if vids else None

    if kind == "praise":
        out = f"{random.choice(PRAISE_OPEN)} {random.choice(PRAISE_CLOSE)}"
        # a light pointer only if they asked for more in a praise-style comment
        if vid and re.search(r"\b(where|how|more|next)\b", text, re.I):
            out = (f'{random.choice(PRAISE_OPEN)} If it helps, I go deeper on this in '
                   f'"{VIDEOS[vid]}": {yt(vid)} {random.choice(PRAISE_CLOSE)}')
        return out

    if kind in ("story", "opinion"):
        open_ = random.choice(STORY_OPEN if kind == "story" else OPINION_OPEN)
        if vid:
            return (f'{open_} For anyone reading who\'s in the same spot, I covered this in '
                    f'"{VIDEOS[vid]}": {yt(vid)}')
        return f"{open_} Thanks for adding this to the conversation."

    # question / help -> actually answer with a pointer
    parts = [random.choice(Q_OPEN),
             f'I actually made a video on this — "{VIDEOS[vid]}": {yt(vid)}' if vid
             else f"I'd say start with the free scorecard — it'll tell you where you stand: {SITE}/scorecard"]
    if product == "vault":
        parts.append(VAULT)
    else:
        parts.append(random.choice(Q_CLOSE))
    return " ".join(parts)


SPAM = ["check out my channel", "sub4sub", "sub 4 sub", "free followers", "http://",
        "https://", "t.me", "whatsapp me", "earn money", "work from home job", "crypto",
        "click here", "telegram"]


def is_spam(t):
    low = t.lower()
    return len(t.strip()) < 6 or any(s in low for s in SPAM)


def load_state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {"replied": {}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--type", dest="kind")
    ap.add_argument("--topic")
    ap.add_argument("--min-likes", type=int, default=0)
    args = ap.parse_args()

    rows = json.load(open(CACHE))["comments"]
    state = load_state()
    done = set(state["replied"])

    cands = []
    for r in rows:
        if r["ownerReplied"] or r["commentId"] in done or is_spam(r["text"]):
            continue
        if r["likes"] < args.min_likes:
            continue
        kind = detect_type(r["text"])
        topic = classify(r["text"])
        if topic == "_skip_negative":
            continue
        # only link a video for the kinds where a pointer is appropriate
        if kind in ("question", "help") and not topic:
            topic = "general"
        if kind in ("story", "opinion") and not topic:
            topic = None
        if args.kind and kind != args.kind:
            continue
        if args.topic and topic != args.topic:
            continue
        cands.append((r, kind, topic))

    cands.sort(key=lambda c: -c[0]["likes"])
    limit = args.limit or (15 if args.dry_run else QUOTA_SAFE_BATCH)
    batch = cands[:limit]

    print(f"cached {len(rows)} | eligible {len(cands)} | this run {len(batch)}")
    print("by type  :", dict(Counter(k for _, k, _ in batch)))
    print("by topic :", dict(Counter(t for _, _, t in batch)))
    print()

    if args.dry_run:
        for r, kind, topic in batch:
            print(f"--- [{kind}/{topic}] {r['likes']}👍  {r['videoTitle'][:38]}")
            print(f"    THEIRS: {' '.join(r['text'].split())[:135]}")
            print(f"    REPLY : {build_reply(kind, topic, r['text'])}")
            print()
        print(f"(dry run — {len(batch)} would post, nothing sent)")
        return 0

    api = build("youtube", "v3",
                credentials=Credentials.from_authorized_user_file(TOKEN))
    posted = failed = 0
    for r, kind, topic in batch:
        body = {"snippet": {"parentId": r["commentId"],
                            "textOriginal": build_reply(kind, topic, r["text"])}}
        try:
            api.comments().insert(part="snippet", body=body).execute()
            state["replied"][r["commentId"]] = {
                "kind": kind, "topic": topic, "videoId": r["videoId"],
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            posted += 1
            if posted % 10 == 0:
                json.dump(state, open(STATE, "w"), indent=1)
                print(f"  posted {posted}...")
        except HttpError as e:
            m = str(e)
            if "quota" in m.lower():
                print(f"  QUOTA after {posted} — resuming next run")
                break
            failed += 1
            print(f"  ! {r['commentId']}: {m[:80]}")
        time.sleep(1.2)

    json.dump(state, open(STATE, "w"), indent=1)
    try:
        with open(LOG, "a") as fh:
            fh.write(f"- **{time.strftime('%Y-%m-%d %H:%M')} UTC** | `COMMENT-REPLY` | "
                     f"replied to {posted} (failed {failed}); types {dict(Counter(k for _, k, _ in batch))}\n")
    except OSError:
        pass
    print(f"\nDONE: posted {posted}, failed {failed}, ~{len(cands) - posted} still eligible")
    return 0


if __name__ == "__main__":
    sys.exit(main())