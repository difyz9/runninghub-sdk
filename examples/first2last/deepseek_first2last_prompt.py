from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "src" / "runninghub_sdk" / "__init__.py").exists():
            return candidate
    raise RuntimeError("Could not locate repository root containing src/runninghub_sdk")


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = find_repo_root()


DEFAULT_SYSTEM_PROMPT = """You are a senior prompt designer for first-frame/last-frame video generation.
Return valid JSON only.

Create prompts for a first-to-last-frame video workflow. The JSON schema must be:
{
  "title": "short title",
  "story_prompt": "2-4 sentences describing the full story arc",
  "first_frame_prompt": "image-generation prompt describing the opening frame in detail",
  "last_frame_prompt": "image-generation prompt describing the ending frame in detail",
  "transition_prompt": "2-4 sentences describing how the motion evolves from first frame to last frame",
  "positive_prompt": "one final production-ready prompt for a first-to-last-frame image-to-video workflow in English",
  "negative_prompt": "one negative prompt in English"
}

Rules:
- Keep the style visual, concrete, and cinematic.
- The first_frame_prompt and last_frame_prompt must describe the same subject with strong continuity.
- The last frame must feel like a believable result of the first frame after motion or story progression.
- positive_prompt must be optimized for an image-to-video model that interpolates from a first frame to a last frame.
- negative_prompt should be concise and practical.
- Avoid markdown fences and explanations outside JSON.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Use DeepSeek to generate first-frame/last-frame video prompts."
    )
    parser.add_argument(
        "--idea",
        default="A young swordswoman stands in a bamboo forest before drawing her blade and leaping toward the moonlit clearing.",
        help="High-level idea or theme for the first-to-last-frame video.",
    )
    parser.add_argument(
        "--style",
        default="cinematic, realistic, high detail, dynamic composition, strong subject continuity",
        help="Visual style guidance.",
    )
    parser.add_argument(
        "--duration",
        default="5 seconds",
        help="Target duration for the first-to-last-frame video.",
    )
    parser.add_argument(
        "--camera",
        default="medium shot with a subtle forward push-in",
        help="Camera language to preserve across the shot.",
    )
    parser.add_argument(
        "--output",
        default="outputs/deepseek_first2last_prompt.json",
        help="Path to save the generated prompt JSON.",
    )
    parser.add_argument(
        "--model",
        default="deepseek-chat",
        help="DeepSeek model name.",
    )
    return parser.parse_args()


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


def build_user_prompt(args: argparse.Namespace) -> str:
    return (
        "Generate prompts for a first-frame/last-frame video workflow with these constraints:\n"
        f"- Core idea: {args.idea}\n"
        f"- Visual style: {args.style}\n"
        f"- Duration target: {args.duration}\n"
        f"- Camera language: {args.camera}\n"
        "- Output language: English for first_frame_prompt, last_frame_prompt, positive_prompt, and negative_prompt; Chinese or English is acceptable for story_prompt and transition_prompt\n"
        "- The first_frame_prompt and last_frame_prompt should each be directly usable as image-generation prompts\n"
        "- The positive_prompt should directly describe the motion evolution between the two frames for a first-to-last-frame workflow\n"
    )


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
        "story_prompt",
        "first_frame_prompt",
        "last_frame_prompt",
        "transition_prompt",
        "positive_prompt",
        "negative_prompt",
    }
    missing_keys = required_keys.difference(data)
    if missing_keys:
        raise SystemExit(f"DeepSeek response missing keys: {sorted(missing_keys)}")
    return data


def save_output(data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def print_result(data: dict, output_path: Path) -> None:
    print(f"title: {data['title']}")
    print()
    print("story_prompt:")
    print(data["story_prompt"])
    print()
    print("first_frame_prompt:")
    print(data["first_frame_prompt"])
    print()
    print("last_frame_prompt:")
    print(data["last_frame_prompt"])
    print()
    print("transition_prompt:")
    print(data["transition_prompt"])
    print()
    print("positive_prompt:")
    print(data["positive_prompt"])
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
    output_path = REPO_ROOT / args.output
    save_output(data, output_path)
    print_result(data, output_path)


if __name__ == "__main__":
    main()