import json
import sys
from agents.transcript_agent import TranscriptAgent

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else (
        "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    )

    print(f"\n{'='*55}")
    print(f"Testing TranscriptAgent")
    print(f"URL: {url}")
    print(f"{'='*55}\n")

    agent  = TranscriptAgent(verbose=True)
    result = agent.run(url)

    print(f"\n{'='*55}")
    print(f"STATUS: {result.status.upper()}")
    print(f"{'='*55}")

    if result.status == "success":
        print(f"Title:    {result.title}")
        print(f"Channel:  {result.channel}")
        print(f"Duration: {result.duration_sec}s")
        print(f"Words:    {result.word_count}")
        print(f"\nTranscript preview:")
        print(result.transcript[:400] + "...")
    else:
        print(f"Error: {result.error}")

    print(f"\nAttempts log:")
    for i, log in enumerate(result.logs, 1):
        icon = "OK" if log.outcome == "success" else "X"
        print(f"  {i}. [{icon}] {log.step} | {log.detail} | {log.outcome}")
        if log.error_type:
            print(f"       error_type: {log.error_type}")

    with open("test_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "status":       result.status,
            "title":        result.title,
            "word_count":   result.word_count,
            "error":        result.error,
            "logs":         [vars(l) for l in result.logs],
            "transcript":   result.transcript,
        }, f, indent=2, ensure_ascii=False)

    print(f"\nFull result saved to test_result.json")

if __name__ == "__main__":
    main()
