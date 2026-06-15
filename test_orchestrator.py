import json
import sys
from agents.orchestrator import Orchestrator


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else (
        "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    )

    print(f"\n{'='*55}")
    print(f"Testing Orchestrator (Agents 1 + 2)")
    print(f"URL: {url}")
    print(f"{'='*55}\n")

    orch   = Orchestrator(verbose=True)
    result = orch.run(url)

    print(f"\n{'='*55}")
    print(f"FINAL STATUS: {result.status.upper()}")
    print(f"Duration:     {result.duration_sec:.1f}s")
    print(f"{'='*55}")

    if result.transcript_result:
        t = result.transcript_result
        print(f"\nTranscript Agent:")
        print(f"  Title:    {t.title}")
        print(f"  Channel:  {t.channel}")
        print(f"  Duration: {t.duration_sec}s")
        print(f"  Words:    {t.word_count}")
        print(f"  Status:   {t.status}")

    if result.planner_result:
        p = result.planner_result
        print(f"\nPlanner Agent:")
        print(f"  Formats:  {p.formats_chosen}")
        print(f"  Reason:   {p.reasoning}")
        print(f"  Status:   {p.status}")

    print(f"\nFull log ({len(result.full_log)} steps):")
    for i, log in enumerate(result.full_log, 1):
        icon = "OK" if log.outcome == "success" else "X"
        print(f"  {i}. [{icon}] [{log.agent}] {log.step} | {log.outcome}")

    if result.failed_at_stage:
        print(f"\nFailed at: {result.failed_at_stage}")

    with open("test_orchestrator_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "status":       result.status,
            "duration_sec": result.duration_sec,
            "failed_at":    result.failed_at_stage,
            "transcript": {
                "title":      result.transcript_result.title if result.transcript_result else None,
                "word_count": result.transcript_result.word_count if result.transcript_result else 0,
                "status":     result.transcript_result.status if result.transcript_result else None,
            },
            "planner": {
                "formats_chosen": result.planner_result.formats_chosen if result.planner_result else [],
                "reasoning":      result.planner_result.reasoning if result.planner_result else None,
                "status":         result.planner_result.status if result.planner_result else None,
            },
            "full_log": [vars(l) for l in result.full_log],
        }, f, indent=2)

    print(f"\nFull result saved to test_orchestrator_result.json")


if __name__ == "__main__":
    main()
