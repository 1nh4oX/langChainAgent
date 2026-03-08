import asyncio
from api.main import _run_single_analysis_for_compare, EnhancedMultiAgentSystem
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_compare():
    system = EnhancedMultiAgentSystem(
        model="Qwen/Qwen2.5-7B-Instruct",
        api_key=os.getenv("api-key") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("base-url") or "https://api.siliconflow.cn/v1",
        debate_threshold=3.0,
        max_debate_rounds=1
    )
    res = await asyncio.to_thread(_run_single_analysis_for_compare, "600519", system)
    print("Compare Result:")
    if res.get("success"):
        print("Success!")
    else:
        print("Failed:", res.get("error"))
        print(res.get("traceback"))

if __name__ == "__main__":
    asyncio.run(debug_compare())
