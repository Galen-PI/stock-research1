"""
test_pattern_significance.py

For every tag in the taxonomy (except reaction_character itself and
chain_position, which is tested separately below), pulls its
rewarded/punished/muted breakdown and runs a chi-square goodness-of-fit
test against an even 1/3-1/3-1/3 null hypothesis. Persists the result
into pattern_significance_tests so every future query can filter to
"only genuinely significant findings" instead of re-deriving this by
hand each time.

This directly answers: "is this pattern real, or could it plausibly be
random noise given the sample size?" A small n with a dramatic-looking
percentage split is exactly the case this catches -- e.g. 47.6% vs 33.3%
on n=21 LOOKS meaningful but is not statistically distinguishable from
chance (p=0.28).

Usage:
    python test_pattern_significance.py              # test every tag
    python test_pattern_significance.py TAG_NAME      # test one tag
"""

import os
import sys
from scipy import stats
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Tags we do NOT test this way: reaction_character tags are the outcome
# being measured, not a category to test; chain_position is tested
# separately (pairwise, not vs-even) since "opening vs closing" is the
# real comparison, not "is opening different from an even 3-way split".
EXCLUDED_TAGS = {"rewarded", "punished", "muted", "diverged_from_fundamentals",
                  "chain_position_opening", "chain_position_middle", "chain_position_closing",
                  "sentiment_confirms_confound", "sentiment_reveals_distinct_driver"}


def get_all_taggable_tags() -> list[str]:
    rows = supabase.table("tags").select("name").execute().data
    return [r["name"] for r in rows if r["name"] not in EXCLUDED_TAGS]


def get_reaction_counts(tag_name: str) -> dict:
    tag_row = supabase.table("tags").select("id").eq("name", tag_name).execute().data
    if not tag_row:
        return {}
    tag_id = tag_row[0]["id"]

    reaction_tags = {
        r["name"]: r["id"] for r in supabase.table("tags")
        .select("id,name").in_("name", ["rewarded", "punished", "muted"]).execute().data
    }

    def all_event_ids_for_tag(t_id: str) -> set:
        """Fully paginated fetch -- avoids silent truncation on large tag sets."""
        ids = set()
        offset = 0
        page_size = 1000
        while True:
            page = supabase.table("event_tags").select("event_id") \
                .eq("tag_id", t_id).range(offset, offset + page_size - 1).execute().data
            if not page:
                break
            ids.update(r["event_id"] for r in page)
            if len(page) < page_size:
                break
            offset += page_size
        return ids

    tagged_event_ids = all_event_ids_for_tag(tag_id)
    if not tagged_event_ids:
        return {}

    # For each reaction tag, fetch its full (paginated) event set and
    # intersect with tagged_event_ids -- exact, no truncation risk,
    # unlike filtering a mixed-tag page by tag_id client-side.
    counts = {"muted": 0, "punished": 0, "rewarded": 0}
    for name, rid in reaction_tags.items():
        reaction_event_ids = all_event_ids_for_tag(rid)
        counts[name] = len(tagged_event_ids & reaction_event_ids)
    return counts


def run_test(tag_name: str, dry_run: bool = False):
    counts = get_reaction_counts(tag_name)
    n = sum(counts.values())
    if n < 5:
        print(f"  SKIP  {tag_name:35s} n={n} (too small to test meaningfully)")
        return

    observed = [counts["muted"], counts["punished"], counts["rewarded"]]
    expected = [n / 3] * 3
    chi2, p = stats.chisquare(observed, expected)
    significant = bool(p < 0.05)
    dominant = max(counts, key=counts.get)

    flag = "SIGNIFICANT" if significant else "not significant"
    print(f"  {tag_name:35s} n={n:4d}  chi2={chi2:5.2f}  p={p:.4f}  {flag:16s} dominant={dominant}")

    if not dry_run:
        supabase.table("pattern_significance_tests").upsert({
            "tag_name": tag_name,
            "n": int(n),
            "muted_count": int(counts["muted"]),
            "punished_count": int(counts["punished"]),
            "rewarded_count": int(counts["rewarded"]),
            "chi2_statistic": float(chi2),
            "p_value": float(p),
            "is_significant": significant,
            "dominant_reaction": dominant,
        }, on_conflict="tag_name").execute()


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    if args:
        tags = [args[0]]
    else:
        tags = get_all_taggable_tags()

    print(f"Testing {len(tags)} tag(s) for statistical significance vs an even 1/3-1/3-1/3 null.\n")
    for t in tags:
        run_test(t, dry_run)

    if not dry_run:
        print("\nResults saved to pattern_significance_tests.")


if __name__ == "__main__":
    main()