import json
from pathlib import Path

from openai import OpenAI
from config import DEEPSEEK_API_KEY, BASE_URL


client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=BASE_URL,
)


PROMPT_FILE = Path("prompts/system_prompt.txt")


def load_system_prompt():
    """
    读取系统 Prompt
    """

    if not PROMPT_FILE.exists():
        raise FileNotFoundError(
            f"未找到 Prompt 文件：{PROMPT_FILE}"
        )

    return PROMPT_FILE.read_text(
        encoding="utf-8"
    )


def analyse(prompt):

    system_prompt = load_system_prompt()

    response = client.chat.completions.create(
        model="deepseek-chat",
        temperature=0.2,
        response_format={
            "type": "json_object"
        },
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return json.loads(
        response.choices[0].message.content
    )
