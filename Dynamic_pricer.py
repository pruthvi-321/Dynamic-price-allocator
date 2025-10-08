import os, json
from datetime import datetime
from pathlib import Path
import nbformat as nbf
import pandas as pd
from textwrap import dedent

# This script creates:
#   - pricing_engine_starter.ipynb  (the full step-by-step notebook)
#   - sample_offers.csv             (fake competitor data to test logic)
#   - requirements.txt              (packages you may want to install)

BASE = Path.cwd()
BASE.mkdir(parents=True, exist_ok=True)

# --- requirements.txt ---
req = dedent("""
pandas
numpy
requests
beautifulsoup4
tldextract
python-whois
requests-cache
playwright
scipy
""").strip() + "\n"
(Path("requirements.txt")).write_text(req, encoding="utf-8")

# --- sample_offers.csv ---
sample = [
    {"source":"amazon","product_title":"Dettol Liquid Handwash Refill 750ml","base_price":112.0,"shipping_fee":0.0,"cod_fee":0.0,"coupon_value":0.0,"in_stock":True,"url":"https://www.example.com/amazon-d","timestamp":datetime.utcnow().isoformat(),"pincode":"","rating":4.4,"rating_count":2200,"https":True,"domain_age_years":28,"has_policy_pages":True},
    {"source":"flipkart","product_title":"Dettol Liquid Handwash Refill 750 ml","base_price":115.0,"shipping_fee":0.0,"cod_fee":0.0,"coupon_value":0.0,"in_stock":True,"url":"https://www.example.com/flipkart-d","timestamp":datetime.utcnow().isoformat(),"pincode":"","rating":4.3,"rating_count":1500,"https":True,"domain_age_years":17,"has_policy_pages":True},
    {"source":"dmart","product_title":"Dettol Liquid Handwash Refill 750ml","base_price":98.0,"shipping_fee":0.0,"cod_fee":0.0,"coupon_value":0.0,"in_stock":True,"url":"https://www.example.com/dmart-d","timestamp":datetime.utcnow().isoformat(),"pincode":"","rating":4.1,"rating_count":300,"https":True,"domain_age_years":10,"has_policy_pages":True},
    {"source":"bigbasket","product_title":"Dettol Liquid Handwash Refill 750ml","base_price":118.0,"shipping_fee":0.0,"cod_fee":0.0,"coupon_value":5.0,"in_stock":False,"url":"https://www.example.com/bigbasket-d","timestamp":datetime.utcnow().isoformat(),"pincode":"","rating":4.2,"rating_count":900,"https":True,"domain_age_years":15,"has_policy_pages":True},
]
pd.DataFrame(sample).to_csv("sample_offers.csv", index=False)

# --- notebook: pricing_engine_starter.ipynb ---
def md(s): return nbf.v4.new_markdown_cell(dedent(s))
def code(s): return nbf.v4.new_code_cell(dedent(s))

nb = nbf.v4.new_notebook()
cells = []

cells += [
md("# E-commerce Pricing Assistant — Step-by-Step Build\nRun each section; debug before moving on."),
md("## Step 0 — Environment check"),
code("""
import sys, platform, pandas as pd, numpy as np
print("Python:", sys.version)
print("Platform:", platform.platform())
print("Pandas:", pd.__version__)
print("Numpy:", np.__version__)
"""),

md("## Step 1 — Folders & constants"),
code("""
from pathlib import Path
BASE_DIR = Path.cwd()
RUNS_DIR = BASE_DIR / "runs"
RUNS_DIR.mkdir(exist_ok=True, parents=True)

LEGIT_THRESHOLD = 60
TOP_N_FOR_ENVELOPE = 3
print("BASE_DIR:", BASE_DIR)
"""),

md("## Step 2 — User input (edit me per product)"),
code("""
user_input = dict(
    product_id="SKU123",
    product_name="Dettol Liquid Handwash Refill 750ml",
    brand="Dettol",
    location="Bidar, KA, IN",
    cost_price=92.0,
    min_margin_pct=15,
    target_position="within_top3",  # match_lowest | beat_lowest_by_pct | within_top3 | margin_first
    beat_pct=2.0,
    channels_to_consider=["amazon","flipkart","dmart","bigbasket","local"],
    tax_rate_pct=18,
    shipping_policy={"base": 0.0, "cod_fee": 0.0, "free_threshold": 0.0},
    competitor_blacklist=[],
    competitor_whitelist=[],
    currency="INR"
)
user_input
"""),

md("## Step 3 — Helpers: margin floor, rounding"),
code("""
from datetime import datetime

def margin_floor(cost_price: float, min_margin_pct: float) -> float:
    return cost_price * (1 + min_margin_pct/100.0)

def psychological_round(price: float) -> float:
    p = round(price)
    return float(p-1) if p >= 100 else float(p)

def now_iso(): return datetime.utcnow().isoformat()
"""),

md("## Step 4 — Legitimacy scoring (simple heuristic)"),
code("""
def score_legitimacy(row) -> int:
    score = 0
    if str(row.get("source","")).lower() in {"amazon","flipkart","bigbasket","reliance","dmart"}:
        score += 20
    if row.get("https", True): score += 5
    age = row.get("domain_age_years", 0) or 0
    if age >= 1: score += 10
    if age >= 5: score += 5
    rating = row.get("rating", None); rating_count = row.get("rating_count", 0) or 0
    if rating is not None and rating_count:
        if rating >= 4.0 and rating_count >= 100: score += 10
        elif rating >= 3.5 and rating_count >= 20: score += 5
    if row.get("has_policy_pages", True): score += 5
    if row.get("in_stock", False): score += 10
    return int(score)
"""),

md("## Step 5 — Delivery reach checker (placeholder)"),
code("""
def check_delivery(source: str, location: str, pincode: str = "") -> bool:
    s = (source or "").lower()
    if "dmart" in s and "bidar" in (location or "").lower():
        return False
    return True
"""),

md("## Step 6 — Comparable price"),
code("""
def comparable_price(row) -> float:
    base = float(row.get("base_price", 0) or 0)
    shipping = float(row.get("shipping_fee", 0) or 0)
    cod = float(row.get("cod_fee", 0) or 0)
    coupon = float(row.get("coupon_value", 0) or 0)
    return max(base + shipping + cod - coupon, 0.0)
"""),

md("## Step 7 — Pricing engine core"),
code("""
import pandas as pd
SMALL_DELTA = 1.0

def choose_price(offers: pd.DataFrame, inp: dict, LEGIT_THRESHOLD=60, TOP_N_FOR_ENVELOPE=3) -> dict:
    mfloor = margin_floor(inp["cost_price"], inp["min_margin_pct"])
    eligible = offers[(offers["delivers_to_location"]==True) & (offers["legitimacy_score"]>=LEGIT_THRESHOLD) & (offers["in_stock"]==True)].copy()
    notes = []
    if eligible.empty:
        rec = psychological_round(max(mfloor, inp["cost_price"]))
        notes.append("No eligible competitor anchors; used margin floor / cost.")
        return dict(recommended_price=rec, margin_floor=mfloor, notes=notes, anchors=[])
    ps = sorted(eligible["comparable_price"].tolist())
    P_lowest = ps[0]; P_top3 = ps[min(len(ps)-1, TOP_N_FOR_ENVELOPE-1)]
    tp = inp.get("target_position","within_top3")
    if tp=="match_lowest":
        candidate = max(mfloor, P_lowest); notes.append("Strategy: match_lowest")
    elif tp=="beat_lowest_by_pct":
        beat_pct = float(inp.get("beat_pct",1.0))
        candidate = max(mfloor, P_lowest*(1-beat_pct/100.0)); notes.append(f"Strategy: beat_lowest_by_pct ({beat_pct}%)")
    elif tp=="within_top3":
        candidate = max(mfloor, P_top3); notes.append("Strategy: within_top3 (upper bound)")
    else:
        candidate = max(mfloor, min(P_lowest + SMALL_DELTA, P_top3)); notes.append("Strategy: margin_first")
    rec = psychological_round(candidate)
    anchors = eligible.sort_values("comparable_price")[["source","comparable_price","url"]].to_dict(orient="records")
    return dict(recommended_price=rec, margin_floor=mfloor, P_lowest=P_lowest, P_top3=P_top3, notes=notes, anchors=anchors)
"""),

md("## Step 8 — Dry run using sample_offers.csv"),
code("""
import pandas as pd, json
offers = pd.read_csv("sample_offers.csv")
offers["delivers_to_location"] = offers.apply(lambda r: check_delivery(r["source"], user_input["location"], r.get("pincode","")), axis=1)
offers["legitimacy_score"] = offers.apply(score_legitimacy, axis=1)
offers["comparable_price"] = offers.apply(comparable_price, axis=1)
display(offers)

result = choose_price(offers, user_input, LEGIT_THRESHOLD=LEGIT_THRESHOLD, TOP_N_FOR_ENVELOPE=TOP_N_FOR_ENVELOPE)
print(json.dumps(result, indent=2))
from pathlib import Path
run_dir = Path("runs")/user_input["product_id"]; run_dir.mkdir(exist_ok=True, parents=True)
offers.to_csv(run_dir/f"{user_input['product_id']}_offers.csv", index=False)
(run_dir/f"{user_input['product_id']}_decision.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print("Saved in:", run_dir)
"""),

md("## Step 9 — Fetcher stubs (to fill later)"),
code("""
import pandas as pd
def fetch_amazon_offers(query: str, brand: str|None=None) -> pd.DataFrame: return pd.DataFrame()
def fetch_flipkart_offers(query: str, brand: str|None=None) -> pd.DataFrame: return pd.DataFrame()
def fetch_dmart_offers(query: str, brand: str|None=None) -> pd.DataFrame: return pd.DataFrame()
CHANNEL_FETCHERS = {"amazon":fetch_amazon_offers,"flipkart":fetch_flipkart_offers,"dmart":fetch_dmart_offers}
"""),

md("## Step 10 — Pipeline function"),
code("""
def run_pipeline(inp: dict, local_csv: str|None=None):
    frames = []
    for ch in inp["channels_to_consider"]:
        f = CHANNEL_FETCHERS.get(ch)
        if f is not None:
            try:
                df = f(inp["product_name"], inp.get("brand"))
                if df is not None and not df.empty: frames.append(df)
            except Exception as e:
                print(f"[WARN] fetch {ch}: {e}")
    if local_csv:
        try:
            import pandas as pd
            frames.append(pd.read_csv(local_csv))
        except Exception as e:
            print("[WARN] could not read local_csv:", e)
    import pandas as pd
    offers = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["source","product_title","base_price","shipping_fee","cod_fee","coupon_value","in_stock","url","timestamp","pincode","rating","rating_count","https","domain_age_years","has_policy_pages"])
    offers["delivers_to_location"] = offers.apply(lambda r: check_delivery(r.get("source",""), inp["location"], r.get("pincode","")), axis=1)
    offers["legitimacy_score"] = offers.apply(score_legitimacy, axis=1)
    offers["comparable_price"] = offers.apply(comparable_price, axis=1)
    decision = choose_price(offers, inp)
    return {"offers": offers, "decision": decision}
"""),

md("## Step 11 — End-to-end test (using the local CSV)"),
code("""
out = run_pipeline(user_input, local_csv="sample_offers.csv")
display(out["offers"])
import json; print("\\nDecision:"); print(json.dumps(out["decision"], indent=2))
"""),
]

nb["cells"] = cells
with open("pricing_engine_starter.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Created files:")
for p in ["pricing_engine_starter.ipynb", "sample_offers.csv", "requirements.txt"]:
    print(" -", p)
