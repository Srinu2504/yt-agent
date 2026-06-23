import json
from agents.publisher_agent import PublisherAgent

SAMPLE_CONTENT = {
    "linkedin_post": """I just wasted 6 months building a product nobody wanted.

I assumed I knew what the market needed. I never asked a single customer.

Talk to customers BEFORE writing code.

What is the biggest assumption you made that turned out wrong?

#startuplessons #entrepreneurship #productmarket""",

    "twitter_thread": """1/ I built 10 startups over 15 years.
3 lessons that actually mattered. 🧵 Thread:

2/ Talk to customers before writing a single line of code.
I wasted 6 months on a product nobody wanted.

3/ Hire for attitude not just skill.
Engineers who care about the problem are worth 10x.

4/ Launch embarrassingly early.
Every day you wait your competitor learns from real users.

5/ Follow me for more startup lessons.""",
}


def main():
    print(f"\n{'='*55}")
    print("Testing PublisherAgent")
    print(f"{'='*55}\n")

    agent  = PublisherAgent(verbose=True)
    result = agent.run(
        video_id         = "test_video_123",
        youtube_url      = "https://www.youtube.com/watch?v=test123",
        title            = "3 Startup Lessons I Learned the Hard Way",
        channel          = "Test Channel",
        duration_sec     = 480,
        transcript       = "Sample transcript for testing...",
        approved_content = SAMPLE_CONTENT,
    )

    print(f"\n{'='*55}")
    print(f"STATUS: {result.status.upper()}")
    print(f"{'='*55}")
    print(f"DB ID:   {result.video_db_id}")
    print(f"Exports: {list(result.exports.keys())}")

    for fmt, files in result.exports.items():
        print(f"\n{fmt}:")
        for ext, path in files.items():
            exists = "✅" if __import__("os").path.exists(path) else "❌"
            print(f"  {exists} {ext}: {path}")

    print(f"\nLogs:")
    for log in result.logs:
        icon = "OK" if log.outcome == "success" else "X"
        print(f"  [{icon}] {log.step} | {log.detail} | {log.message}")

    with open("test_publisher_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "status":     result.status,
            "video_db_id": result.video_db_id,
            "exports":    result.exports,
            "logs":       [vars(l) for l in result.logs],
        }, f, indent=2)

    print(f"\nResult saved to test_publisher_result.json")


if __name__ == "__main__":
    main()
