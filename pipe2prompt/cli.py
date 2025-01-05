import os
import sys
from pathlib import Path

import click
import tomllib
from click import Command, Group

from .completion import install_shell_completion
from .prompt import Prompt

CONFIG_FILE = Path.home() / ".p2p" / "config.toml"


def load_prompts_from_toml():
    try:
        with open(CONFIG_FILE, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {CONFIG_FILE}")
        print("Run `p2p init` to create a new config file")
        return {}


class PromptCommand(Command, Prompt):
    def __init__(self, name, prompt_config):
        self.prompt_config = prompt_config

        Command.__init__(
            self,
            name=name,
            callback=self.run_prompt,
            params=[
                click.Argument(['pipe_input'], required=False)
            ],
            help=prompt_config.get('description', f'Execute {name} prompt'),
        )
        Prompt.__init__(self, name, **prompt_config)

    def get_short_help_str(self, limit=45):
        help_str = self.prompt_config.get(
            'description', f'Execute {self.name} prompt')
        help_str = "[PROMPT] " + help_str
        return help_str

    def run_prompt(self, pipe_input=None):
        if pipe_input is None and not sys.stdin.isatty():
            pipe_input = sys.stdin.read().strip()
        self.run(pipe_input)


class PromptManager(Group):
    """Manages prompt-related commands and configurations"""
    def __init__(self):
        super().__init__(name='prompt', help="Prompt management commands")
        self.add_command(self.list_prompts())

    def list_prompts(self):
        @click.command()
        @click.option('--long', '-l', is_flag=True,
                      help='Show long format including descriptions')
        def list(long):
            """List available prompts"""
            cli_instance = click.get_current_context().find_root().command
            prompts = {
                name: cmd for name, cmd in cli_instance.commands.items()
                if isinstance(cmd, PromptCommand)
            }
            if len(prompts) == 0:
                return

            max_name_length = max(len(name) for name, _ in prompts.items()) + 2

            if long:
                for name, cmd in sorted(prompts.items()):
                    padded_name = name.ljust(max_name_length)
                    click.echo(f"{click.style(padded_name, fg='green')}"
                               f"{cmd.get_short_help_str()}")
            else:
                terminal_width = os.get_terminal_size()[0]
                columns = max(1, terminal_width // max_name_length)
                
                line = []
                for idx, (name, _) in enumerate(sorted(prompts.items())):
                    line.append(name.ljust(max_name_length))
                    if len(line) == columns or idx == len(prompts) - 1:
                        click.echo(''.join(line).rstrip())
                        line = []

        return list


def init_command():
    @click.command()
    def init():
        """Initialize shell completion"""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not CONFIG_FILE.exists():
            CONFIG_FILE.touch()
        install_shell_completion()
    return init


class CLI(Group):
    def __init__(self):
        super().__init__()
        self.prompts = load_prompts_from_toml()

        self.add_command(init_command())
        self.add_command(PromptManager())
        for prompt_name, prompt_config in self.prompts.items():
            if prompt_config.get('enabled', True):
                self.add_command(PromptCommand(prompt_name, prompt_config))

    def format_commands(self, ctx, formatter):
        """Override format_commands to customize the help output"""
        builtin_commands = []
        prompt_commands = []

        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None:
                continue
            if isinstance(cmd, PromptCommand):
                prompt_commands.append((subcommand, cmd))
            else:
                builtin_commands.append((subcommand, cmd))

        with formatter.section("Built-in Commands"):
            formatter.write_dl(
                [
                    (name, cmd.get_short_help_str())
                    for name, cmd in builtin_commands
                ]
            )
        
        if len(prompt_commands) > 0:
            with formatter.section("User Defined Prompts"):
                formatter.write_dl(
                    [
                        (name, cmd.get_short_help_str())
                        for name, cmd in prompt_commands
                    ]
                )

    def list_commands(self, ctx):
        """Return list of available commands"""
        return sorted(self.commands.keys())

    def get_command(self, ctx, cmd_name):
        """Get a specific command object"""
        cmd = self.commands.get(cmd_name)

        return cmd
    

cli = CLI()


if __name__ == '__main__':
    cli()
