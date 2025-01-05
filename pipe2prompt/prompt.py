import re
import sys
from dataclasses import dataclass, field

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
    has_placeholder: bool = field(default=False)

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
            missing_fields_str = ", ".join(missing_fields)
            LOG.error(f"Prompt '{self.name}' requires {missing_fields_str} fields")
            sys.exit(1)

        # Use regex to find all placeholders in the content
        allowed_placeholder = "pipe"
        format_vars = re.findall(r'{(.*?)}', self.content)
        for var_name in format_vars:
            if var_name != allowed_placeholder:
                LOG.error(f"Only '{allowed_placeholder}' placeholder is allowed, "
                          f"found: '{{{var_name}}}'")
                sys.exit(1)
            else:
                self.has_placeholder = True

    def run(self, pipe_input):

        if self.has_placeholder:
            if pipe_input is None or pipe_input == "":
                LOG.error(f"Empty input. Prompt '{self.name}' requires pipe input")
                sys.exit(1)
            else:
                message = self.content.format(pipe=pipe_input)
        else:
            message = self.content

        client = OpenAI()

        stream = client.chat.completions.create(
            model=self.base_model,
            messages=[{"role": "user", "content": message}],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        
        client.close()