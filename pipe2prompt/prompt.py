from dataclasses import dataclass, field
import re
import sys

from openai import OpenAI

from .utils import get_logger

LOG = get_logger(__name__)

@dataclass
class Prompt:
    name: str
    content: str = field(default="")
    base_model: str = field(default=None)
    description: str = field(default="")
    enabled: bool = field(default=True)

    def __post_init__(self):
        self.validate()

    def validate(self):
        if not self.enabled:
            return

        missing_fields = []
        if self.content is None or self.content == "":
            missing_fields.append("content")
        if self.base_model is None:
            missing_fields.append("base_model")
        if len(missing_fields) > 0:
            LOG.error(f"Prompt '{self.name}' requires {', '.join(missing_fields)} fields")
            sys.exit(1)

        # Use regex to find all placeholders in the content
        allowed_placeholder = "pipe"
        format_vars = re.findall(r'{(.*?)}', self.content)
        for var_name in format_vars:
            if var_name != allowed_placeholder:
                LOG.error(f"Only '{allowed_placeholder}' placeholder is allowed, found: '{{{var_name}}}'")
                sys.exit(1)

    def run(self, pipe_input):
        client = OpenAI()

        message = self.content.format(pipe=pipe_input)
        with open('prompt.txt', 'w') as f:
            f.write(message)

        stream = client.chat.completions.create(
            model=self.base_model,
            messages=[{"role": "user", "content": message}],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        
        client.close()