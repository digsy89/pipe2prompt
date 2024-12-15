import click
import tomllib
from pathlib import Path
import os
import subprocess
import sys


def load_prompts_from_toml():
    config_path = Path.home() / ".pp" / "config.toml"
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return {}


class PromptCommand(click.Command):
    def __init__(self, name, prompt_config):
        self.prompt_config = prompt_config

        super().__init__(
            name=name,
            callback=self.run_prompt,
            params=[
                click.Argument(['stdin'], required=False)
            ],
            help=prompt_config.get('description', f'Execute {name} prompt'),
            hidden=True
        )

    def get_short_help_str(self, limit=45):
        return self.prompt_config.get('description', f'Execute {self.name} prompt')

    def run_prompt(self, stdin=None):
        if stdin is None and not sys.stdin.isatty():
            stdin = sys.stdin.read().strip()
        click.echo(self.prompt_config)
        click.echo(stdin)


class PromptManager(click.Group):
    """Manages prompt-related commands and configurations"""
    def __init__(self):
        super().__init__(name='prompt', help="Prompt management commands")
        self.add_command(self.list_command())
        self.add_command(self.update_command())

    def list_command(self):
        @click.command()
        @click.option('--long', '-l', is_flag=True, help='Show long format including descriptions')
        def list(long):
            """List available prompts"""
            cli_instance = click.get_current_context().find_root().command
            prompts = cli_instance.prompts

            if long:
                prompts_with_desc = [
                    (name, config) for name, config in prompts.items()
                    if 'description' in config
                ]
                if prompts_with_desc:
                    max_name_length = max(len(name) for name, _ in prompts_with_desc)
                    for name, config in sorted(prompts_with_desc):
                        padded_name = name.ljust(max_name_length)
                        click.echo(f"{click.style(padded_name, fg='green')}  {config['description']}")
                else:
                    click.echo("No prompts with descriptions found.")
            else:
                for name in sorted(prompts.keys()):
                    click.echo(name)
        return list

    def update_command(self):
        @click.command()
        def update():
            """Update prompt completion"""
            self.install_prompt_completion()
            click.echo("Prompt completion updated successfully")
        return update

    def install_prompt_completion(self):
        shell = os.environ.get('SHELL', '').split('/')[-1]
        if shell == 'bash':
            completion_script = '''
    _pp_completion() {
        local prompts="$(pp prompt list)"
        COMPREPLY=( $(compgen -W "${prompts}" -- "${COMP_WORDS[1]}") )
    }
    complete -F _pp_completion pp
    '''
            rc_file = os.path.expanduser('~/.bashrc')
            subprocess.run(['bash', '-c', completion_script])
        elif shell == 'zsh':
            completion_script = '''
    autoload -Uz compinit
    compinit

    _pp() {
        local prompts=(${(f)"$(pp prompt list)"})
        _describe 'prompt' prompts
    }
    compdef _pp pp
    '''
            rc_file = os.path.expanduser('~/.zshrc')
            subprocess.run(['zsh', '-c', completion_script])
        else:
            click.echo(f"Unsupported shell: {shell}")
            return

        with open(rc_file, 'a+') as f:
            f.seek(0)
            if completion_script not in f.read():
                f.write(f'\n# PP CLI completion\n{completion_script}\n')
                click.echo(f"Added completion script to {rc_file}")
            else:
                click.echo("Completion script already installed")


class CLI(click.Group):
    def __init__(self):
        super().__init__()
        self.prompts = load_prompts_from_toml()

        self.add_command(PromptManager())
        for prompt_name, prompt_config in self.prompts.items():
            self.add_command(PromptCommand(prompt_name, prompt_config))

    def list_commands(self, ctx):
        """Return list of available commands"""
        return sorted(
            name for name, cmd in self.commands.items()
            if not getattr(cmd, 'hidden', False)
        )

    def get_command(self, ctx, cmd_name):
        """Get a specific command object"""
        return self.commands.get(cmd_name)


# CLI 인스턴스 생성
cli = CLI()


if __name__ == '__main__':
    cli()
