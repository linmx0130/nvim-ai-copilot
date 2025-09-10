from pynvim import attach
from openai import OpenAI
from config import MODEL_NAME, API_BASE_URL, API_KEY
import sys
import os
import time


def get_openai_client():
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def get_prompt(filename: str, before_cursor: str, after_cursor: str) -> str:
    """
    Return a prompt with the content before and after the cursor position.
    """
    return f"""
# Task
Act as a good programmer. Based on the code context provided, fill proper code that 
makes sense in the context.

## Output format
* Generate the proper code only. 
* Do not add any explanation.
* Generated code should be quoted by ```.
* Do not add extra intent

## Metadata
Filename: {filename}

## Context before the blank
```
{before_cursor}
```

## Context after the blank
```
{after_cursor}
```

"""


def main(nvim_socket_path: str):
    nvim = attach("socket", path=nvim_socket_path)
    current_buffer = nvim.current.buffer
    cursor_position = nvim.current.window.cursor
    filename = current_buffer.name

    # grab the content and split it based on the cursor position
    content_lines = [line for line in current_buffer]
    before_cursor = content_lines[: cursor_position[0] - 1]
    before_cursor.append(content_lines[cursor_position[0] - 1][: cursor_position[1]])
    after_cursor = [
        content_lines[cursor_position[0] - 1][cursor_position[1] :]
    ] + content_lines[cursor_position[0] :]

    prompt = get_prompt(filename, "\n".join(before_cursor), "\n".join(after_cursor))

    print(prompt)

    nvim.command('echo "Copilot is generating contents..."')
    last_print_time = time.monotonic()

    try:
        client = get_openai_client()
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            max_completion_tokens=512,
            stream=True,
        )

        generated_output: str = ""
        counter = 0
        for chunk in chat_completion:
            if chunk.choices[0].delta.content:
                generated_output += chunk.choices[0].delta.content
                if time.monotonic() - last_print_time > 1.0:
                    counter += 1
                    dots = "." * (counter % 6 + 1)
                    nvim.command(f'echo "Copilot is generating contents {dots}"')
                    last_print_time = time.monotonic()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        nvim.command(f'echo "Copilot fails to generate correct output.", Error: {e}')
        exit(1)

    generate_lines = generated_output.strip().split("\n")
    if generate_lines[-1] == "```" and generate_lines[0].startswith("```"):
        generate_lines = generate_lines[1:-1]
        generate_lines[0] = before_cursor[-1] + generate_lines[0]
        generate_lines[-1] = generate_lines[-1] + after_cursor[0]
        current_buffer[cursor_position[0] - 1] = generate_lines[0]
        if len(generate_lines) > 1:
            current_buffer.append(generate_lines[1:], cursor_position[0])
    else:
        nvim.command('echo "Copilot fails to generate correct output."')


if __name__ == "__main__":
    # Print error message if argv doesn't contain any arguments
    if len(sys.argv) < 2:
        print("Error: No nvim socket path provided", file=sys.stderr)
        exit(1)

    main(sys.argv[1])
