import json
from agents.reviewer_agent import ReviewerAgent

SAMPLE_DRAFTS = {
    "linkedin_post": """I just wasted 6 months building a product nobody wanted.

I assumed I knew what the market needed. I never asked a single customer.

Here is what I learned the hard way:

Talk to customers BEFORE writing code. Every day you skip this step 
is a day you might be building the wrong thing.

What is the biggest assumption you made that turned out to be wrong?

#startuplessons #entrepreneurship #productmarket""",

    "twitter_thread": """1/ I built 10 startups over 15 years.
Here are the 3 lessons that actually mattered. 🧵 Thread:

2/ Talk to customers before writing a single line of code.
I wasted 6 months on a product nobody wanted.

3/ Hire for attitude, not just skill.
Engineers who care about the problem are worth 10x those who don't.

4/ Launch embarrassingly early.
Every day you wait, your competitor learns from real users.

5/ The uncomfortable truth:
Most startup failures are caused by building things people don't want.

6/ Follow me for more hard-won startup lessons.""",
}

FORMATS = ["linkedin_post", "twitter_thread"]


def main():
    print(f"\n{'='*55}")
    print("Testing ReviewerAgent")
    print(f"{'='*55}\n")

    agent  = ReviewerAgent(verbose=True)
    result = agent.run(SAMPLE_DRAFTS, FORMATS)

    print(f"\n{'='*55}")
    print(f"STATUS: {result.status.upper()}")
    print(f"{'='*55}")
    print(f"Approved formats:  {list(result.approved.keys())}")
    print(f"Revision counts:   {result.revision_counts}")
    print(f"Warnings:          {result.warnings}")

    for fmt, content in result.approved.items():
        print(f"\n--- {fmt.upper()} ---")
        print(content[:300] + "..." if len(content) > 300 else content)

    print(f"\nLogs:")
    for log in result.logs:
        icon = "OK" if log.outcome == "success" else "X"
        print(f"  [{icon}] {log.step} | {log.detail} | {log.message}")

    with open("test_reviewer_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "status":          result.status,
            "approved":        {k: v[:300] for k, v in result.approved.items()},
            "revision_counts": result.revision_counts,
            "warnings":        result.warnings,
            "logs":            [vars(l) for l in result.logs],
        }, f, indent=2, ensure_ascii=False)

    print(f"\nResult saved to test_reviewer_result.json")


if __name__ == "__main__":
    main()
