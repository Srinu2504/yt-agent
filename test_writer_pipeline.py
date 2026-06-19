import json
import sys
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
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

TITLE    = "3 Startup Lessons I Learned the Hard Way"
DURATION = 480

def main():
    print(f"\n{'='*55}")
    print("Testing Research + Writer Pipeline")
    print(f"{'='*55}\n")

    # Step 1 - Plan
    print("--- PlannerAgent ---")
    planner = PlannerAgent(verbose=True)
    plan    = planner.run(SAMPLE_TRANSCRIPT, TITLE, DURATION)
    print(f"Formats chosen: {plan.formats_chosen}\n")

    # Step 2 - Research
    print("--- ResearchAgent ---")
    researcher = ResearchAgent(verbose=True)
    research   = researcher.run(SAMPLE_TRANSCRIPT, plan.formats_chosen)
    print(f"Briefs ready: {list(research.briefs.keys())}\n")

    # Step 3 - Write
    print("--- WriterAgent ---")
    writer = WriterAgent(verbose=True)
    drafts = writer.run(
        transcript     = SAMPLE_TRANSCRIPT,
        title          = TITLE,
        formats_chosen = plan.formats_chosen,
        briefs         = research.briefs,
    )

    print(f"\n{'='*55}")
    print(f"RESULTS")
    print(f"{'='*55}")
    print(f"Status:          {drafts.status}")
    print(f"Drafts ready:    {list(drafts.drafts.keys())}")
    print(f"Failed formats:  {list(drafts.failed_formats.keys())}")

    for fmt, draft in drafts.drafts.items():
        print(f"\n--- {fmt.upper()} ({len(draft.split())} words) ---")
        print(draft[:300] + "..." if len(draft) > 300 else draft)

    with open("test_writer_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "plan":           plan.formats_chosen,
            "briefs":         research.briefs,
            "drafts":         {k: v[:500] for k, v in drafts.drafts.items()},
            "failed_formats": drafts.failed_formats,
            "logs":           [vars(l) for l in drafts.logs],
        }, f, indent=2, ensure_ascii=False)

    print(f"\nFull result saved to test_writer_result.json")

if __name__ == "__main__":
    main()
