import json
import sys
from agents.planner_agent import PlannerAgent

SAMPLE_TRANSCRIPT = """
In this video I want to share the three most important lessons 
I learned after building 10 startups over 15 years. 

First, talk to your customers before writing a single line of code. 
I wasted 6 months building a product nobody wanted because I assumed 
I knew what the market needed.

Second, hire for attitude not just skill. The best engineers I worked 
with were the ones who cared deeply about the problem, not just the 
technology.

Third, launch early and iterate fast. Your first version will be 
embarrassing. Ship it anyway. Every day you wait is a day your 
competitor is learning from real users.

These three lessons saved my last company and I wish someone had 
told me this 15 years ago.
"""

def main():
    title        = sys.argv[1] if len(sys.argv) > 1 else "3 Startup Lessons I Learned the Hard Way"
    duration_sec = int(sys.argv[2]) if len(sys.argv) > 2 else 480

    print(f"\n{'='*55}")
    print(f"Testing PlannerAgent")
    print(f"Title:    {title}")
    print(f"Duration: {duration_sec}s ({duration_sec/60:.1f} min)")
    print(f"{'='*55}\n")

    agent  = PlannerAgent(verbose=True)
    result = agent.run(SAMPLE_TRANSCRIPT, title, duration_sec)

    print(f"\n{'='*55}")
    print(f"STATUS: {result.status.upper()}")
    print(f"{'='*55}")

    if result.status == "success":
        print(f"Formats chosen: {result.formats_chosen}")
        print(f"Reasoning:      {result.reasoning}")
    else:
        print(f"Error: {result.error}")

    print(f"\nAttempts log:")
    for i, log in enumerate(result.logs, 1):
        icon = "OK" if log.outcome == "success" else "X"
        print(f"  {i}. [{icon}] {log.step} | {log.outcome} | {log.message}")

    with open("test_planner_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "status":         result.status,
            "formats_chosen": result.formats_chosen,
            "reasoning":      result.reasoning,
            "error":          result.error,
            "logs":           [vars(l) for l in result.logs],
        }, f, indent=2)

    print(f"\nFull result saved to test_planner_result.json")

if __name__ == "__main__":
    main()
