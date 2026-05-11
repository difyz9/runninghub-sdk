from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def find_repo_root() -> Path:
    current = SCRIPT_DIR
    for candidate in (current, *current.parents):
        if (candidate / "src" / "runninghub_sdk" / "__init__.py").exists():
            return candidate
    raise RuntimeError("Could not locate repository root containing src/runninghub_sdk")


REPO_ROOT = find_repo_root()


DEFAULT_SYSTEM_PROMPT = """You are a senior storyboard designer for comic and anime previsualization.
Return valid JSON only.

Create a production-ready storyboard prompt payload. The JSON schema must be:
{
  "title": "short title",
  "global_style": "one concise global style line in Chinese",
  "story_summary": "2-4 sentences summarizing the scene progression in Chinese",
  "storyboard_prompt": "multi-line Chinese storyboard prompt using Slot format",
  "negative_prompt": "one concise negative prompt in Chinese"
}

Rules:
- Return JSON only, no markdown fences.
- storyboard_prompt must use this exact structure:
  Slot 1 (缓冲帧):
  ...

  Slot 2 (剧情帧):
  ...

  Slot 3 (剧情帧):
  ...
- There must be a blank line between every Slot block.
- Include exactly 6 slots total: Slot 1 is a pure black buffer frame, Slots 2-6 are story frames.
- The storyboard_prompt must be directly usable as input for a storyboard image workflow.
- Each story frame should mention environment, subject, action, mood, and camera shot.
"""

DEFAULT_NEGATIVE_PROMPT = "低质量，模糊，错误透视，人物崩坏，手部异常，额外肢体，画面拥挤，构图混乱，风格漂移"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Use DeepSeek to generate storyboard prompts.")
    parser.add_argument(
        "--idea",
        default="主角深夜误入荒废寺庙，在恐惧中逐步发现庙内异样，气氛持续升级。",
        help="High-level story idea.",
    )
    parser.add_argument(
        "--style",
        default="国漫分镜，电影感构图，悬疑惊悚，强氛围光影",
        help="Visual style guidance.",
    )
    parser.add_argument(
        "--characters",
        default="主角：年轻男性，谨慎、紧张、易受惊。",
        help="Character and cast description.",
    )
    parser.add_argument(
        "--output",
        default=str(SCRIPT_DIR / "outputs" / "deepseek_fenjing_storyboard_prompt.json"),
        help="Path to save the generated prompt JSON.",
    )
    parser.add_argument(
        "--model",
        default="deepseek-chat",
        help="DeepSeek model name.",
    )
    return parser.parse_args()


def build_user_prompt(args: argparse.Namespace) -> str:
    return (
        f"Generate a storyboard payload with these constraints:\n"
        f"- Core story idea: {args.idea}\n"
        f"- Visual style: {args.style}\n"
        f"- Characters: {args.characters}\n"
        f"- Output language: Chinese\n"
        f"- The storyboard_prompt must be directly usable for a RunningHub storyboard workflow\n"
        f"- Keep the scene progression coherent and cinematic\n"
    )


def bootstrap_env() -> list[Path]:
    loaded_paths: list[Path] = []
    for env_path in (SCRIPT_DIR / ".env", REPO_ROOT / ".env"):
        if env_path.exists():
            loaded_paths.append(env_path)
            with open(env_path, "r", encoding="utf-8") as file_obj:
                for line in file_obj:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    if key and value and key not in os.environ:
                        os.environ[key] = value
    return loaded_paths


def load_openai_client():
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: openai. Install it with 'pip install openai'."
        ) from exc

    loaded_paths = bootstrap_env()
    if loaded_paths:
        print(f"deepseek_env_source: {loaded_paths[0]}")
    else:
        print("deepseek_env_source: <none>")

    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "Missing API key. Set DEEPSEEK_API_KEY or OPENAI_API_KEY before running this script."
        )

    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def request_prompt_payload(args: argparse.Namespace) -> dict:
    client = load_openai_client()
    try:
        response = client.chat.completions.create(
            model=args.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(args)},
            ],
            temperature=0.9,
        )
    except Exception as exc:
        error_name = exc.__class__.__name__
        error_text = str(exc)

        if error_name == "AuthenticationError":
            raise SystemExit(
                "DeepSeek authentication failed. Check DEEPSEEK_API_KEY / OPENAI_API_KEY.\n"
                f"Original error: {error_text}"
            ) from exc

        raise SystemExit(
            "DeepSeek request failed.\n"
            f"Original error: {error_text}"
        ) from exc

    content = response.choices[0].message.content
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"DeepSeek returned invalid JSON: {content}") from exc

    required_keys = {
        "title",
        "global_style",
        "story_summary",
        "storyboard_prompt",
    }
    missing_keys = required_keys.difference(data)
    if missing_keys:
        raise SystemExit(f"DeepSeek response missing keys: {sorted(missing_keys)}")

    negative_prompt = str(data.get("negative_prompt", "")).strip()
    if not negative_prompt:
        data["negative_prompt"] = DEFAULT_NEGATIVE_PROMPT

    return data


def save_output(data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def print_result(data: dict, output_path: Path) -> None:
    print(f"title: {data['title']}")
    print()
    print("global_style:")
    print(data["global_style"])
    print()
    print("story_summary:")
    print(data["story_summary"])
    print()
    print("storyboard_prompt:")
    print(data["storyboard_prompt"])
    print()
    print("negative_prompt:")
    print(data["negative_prompt"])
    print()
    print(f"saved prompt json to: {output_path.resolve()}")


def main() -> None:
    loaded_paths = bootstrap_env()
    if loaded_paths:
        print(f"loaded_env: {loaded_paths[0]}")
    else:
        print("loaded_env: <none>")
    args = parse_args()
    data = request_prompt_payload(args)
    output_path = Path(args.output)
    save_output(data, output_path)
    print_result(data, output_path)


if __name__ == "__main__":
    main()