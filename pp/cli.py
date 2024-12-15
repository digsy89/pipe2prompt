import click
import tomllib
from pathlib import Path
import os
from pp.core import run_task

def load_commands_from_toml():
    config_path = Path.home() / ".pp" / "config.toml"
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"Config file not found at: {config_path}")
        return {}

COMMANDS = load_commands_from_toml()

class DynamicCLI(click.Group):
    def list_commands(self, ctx):
        global COMMANDS
        COMMANDS = load_commands_from_toml()
        return ['update'] + sorted(list(COMMANDS.keys()))

    def get_command(self, ctx, cmd_name):
        if cmd_name == 'update':
            @click.command(help="Update command completion")
            def update():
                global COMMANDS
                COMMANDS = load_commands_from_toml()
                print(COMMANDS)
                install_completion()
                click.echo("Command completion updated successfully")
            return update
            
        if cmd_name in COMMANDS:
            command_config = COMMANDS[cmd_name]
            
            @click.command(help=command_config.get('description', ''))
            @click.pass_context
            def dynamic_command(ctx):
                click.echo(f"Executing {cmd_name}")
                if 'command' in command_config:
                    run_task(command_config['command'])
                
            return dynamic_command
        return None

@click.group(cls=DynamicCLI)
def cli():
    """PP CLI Tool"""
    pass

def install_completion():
    shell = os.environ.get('SHELL', '').split('/')[-1]
    
    if shell == 'bash':
        completion_script = 'eval "$(_PP_COMPLETE=bash_source pp)"'
        rc_file = os.path.expanduser('~/.bashrc')
        shell_cmd = 'bash -c'
    elif shell == 'zsh':
        completion_script = 'eval "$(_PP_COMPLETE=zsh_source pp)"'
        rc_file = os.path.expanduser('~/.zshrc')
        shell_cmd = 'zsh -c'
    else:
        click.echo(f"Unsupported shell: {shell}")
        return

    with open(rc_file, 'a+') as f:
        f.seek(0)
        if completion_script not in f.read():
            f.write(f'\n# PP CLI completion\n{completion_script}\n')
            click.echo(f"Added completion script to {rc_file}")
            os.system(f'{shell_cmd} "{completion_script}"')
            click.echo("Completion is now available in current session")
        else:
            os.system(f'{shell_cmd} "{completion_script}"')
            click.echo("Completion script already installed and enabled for current session")

if __name__ == '__main__':
    cli()
