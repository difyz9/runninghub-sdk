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


DEFAULT_SYSTEM_PROMPT = """You are a senior character designer for anime, comic, and game pre-production.
Return valid JSON only.

Create a production-ready character design payload. The JSON schema must be:
{
  "name": "character name",
  "core_concept": "1-2 sentence character concept",
  "character_card_input": "multi-line Chinese character sheet using fields like 姓名 / 年龄 / 性别 / 风格 / 外貌 / 气质 / 服装",
  "visual_prompt": "one polished character design prompt in Chinese",
  "color_palette_prompt": "one polished color, lighting, and material prompt in Chinese",
  "negative_prompt": "one concise negative prompt in Chinese"
}

Rules:
- Return JSON only, no markdown fences.
- character_card_input must be directly usable as the role description input for a character card workflow.
- visual_prompt should focus on silhouette, face, hair, costume, pose, and atmosphere.
- color_palette_prompt should focus on palette, contrast, lighting, and material finish.
- negative_prompt should focus on bad anatomy, low quality, broken hands, clutter, extra limbs, and style drift.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Use DeepSeek to generate character design prompts.")
    parser.add_argument(
        "--idea",
        default="设计一位冷艳、克制、具有强烈记忆点的国漫女性角色，用于角色卡首版设定。",
        help="High-level character idea.",
    )
    parser.add_argument(
        "--style",
        default="国漫，精致角色设计，电影感光影，适合角色卡立绘",
        help="Visual style guidance.",
    )
    parser.add_argument(
        "--world",
        default="都市奇幻",
        help="World setting or genre.",
    )
    parser.add_argument(
        "--output",
        default="outputs/deepseek_ai2role_character_prompt.json",
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
        f"Generate a character design payload with these constraints:\n"
        f"- Core idea: {args.idea}\n"
        f"- Visual style: {args.style}\n"
        f"- World setting: {args.world}\n"
        f"- Output language: Chinese\n"
        f"- The character_card_input must be directly usable for a RunningHub character card workflow input node\n"
        f"- The visual_prompt and color_palette_prompt must be polished enough for downstream image generation and art direction\n"
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
        "name",
        "core_concept",
        "character_card_input",
        "visual_prompt",
        "color_palette_prompt",
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
    print(f"name: {data['name']}")
    print()
    print("core_concept:")
    print(data["core_concept"])
    print()
    print("character_card_input:")
    print(data["character_card_input"])
    print()
    print("visual_prompt:")
    print(data["visual_prompt"])
    print()
    print("color_palette_prompt:")
    print(data["color_palette_prompt"])
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