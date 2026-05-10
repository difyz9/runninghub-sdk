from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent


DEFAULT_SYSTEM_PROMPT = """You are a senior storyboard writer for text-to-video generation.
Return valid JSON only.

Create a short cinematic concept for video generation. The JSON schema must be:
{
  "title": "short title",
  "story_prompt": "2-4 sentences describing the full story arc",
  "scene_prompts": [
    "scene 1 prompt",
    "scene 2 prompt",
    "scene 3 prompt"
  ],
  "video_prompt": "one final production-ready text-to-video prompt in English"
}

Rules:
- Keep the style visual, concrete, and cinematic.
- scene_prompts must contain exactly 3 items.
- video_prompt must be optimized for a video diffusion model.
- Avoid markdown fences and explanations outside JSON.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Use DeepSeek to generate video prompts.")
    parser.add_argument(
        "--idea",
        default="A lone explorer discovers a glowing ancient city under the desert at dusk.",
        help="High-level idea or theme for the video.",
    )
    parser.add_argument(
        "--style",
        default="cinematic, realistic, high detail, smooth camera movement",
        help="Visual style guidance.",
    )
    parser.add_argument(
        "--duration",
        default="6-8 seconds",
        help="Target duration for the generated video concept.",
    )
    parser.add_argument(
        "--output",
        default="outputs/deepseek_video_prompt.json",
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
        f"Generate a video concept with these constraints:\n"
        f"- Core idea: {args.idea}\n"
        f"- Visual style: {args.style}\n"
        f"- Duration target: {args.duration}\n"
        f"- Output language: English for the final video_prompt, Chinese or English is acceptable for other fields\n"
        f"- Make the final video_prompt directly usable for a text-to-video model such as CogVideoX\n"
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
    print(" >>> ", api_key)
    if not api_key:
        raise SystemExit(
            "Missing API key. Set DEEPSEEK_API_KEY or OPENAI_API_KEY before running this script."
        )

    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


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

    required_keys = {"title", "story_prompt", "scene_prompts", "video_prompt"}
    missing_keys = required_keys.difference(data)
    if missing_keys:
        raise SystemExit(f"DeepSeek response missing keys: {sorted(missing_keys)}")
    if not isinstance(data["scene_prompts"], list) or len(data["scene_prompts"]) != 3:
        raise SystemExit("DeepSeek response must contain exactly 3 scene_prompts.")
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
    print("scene_prompts:")
    for index, prompt in enumerate(data["scene_prompts"], start=1):
        print(f"{index}. {prompt}")
    print()
    print("video_prompt:")
    print(data["video_prompt"])
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