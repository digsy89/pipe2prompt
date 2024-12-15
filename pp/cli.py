import click
import tomllib
from pathlib import Path
import os
from pp.core import run_task
import subprocess

def load_prompts_from_toml():
    config_path = Path.home() / ".pp" / "config.toml"
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"Config file not found at: {config_path}")
        return {}

PROMPTS = load_prompts_from_toml()

@click.group()
def cli():
    """PP CLI Tool"""
    pass

@click.group()
def prompt():
    """Prompt management commands"""
    pass

cli.add_command(prompt)

def install_prompt_completion():
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
        
        # 현재 세션에 바로 적용 (bash)
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
        
        # zsh의 경우 completion 스크립트만 현재 세션에 적용
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

@prompt.command()
def update():
    """Update prompt completion"""
    install_prompt_completion()
    click.echo("Prompt completion updated successfully")

@prompt.command()
@click.option('--long', '-l', is_flag=True, help='Show long format including descriptions')
def list(long):
    """List available prompts"""
    if long:
        # 상세 정보 출력
        prompts_with_desc = [(name, config) for name, config in PROMPTS.items() if 'description' in config]
        if prompts_with_desc:
            max_name_length = max(len(name) for name, _ in prompts_with_desc)
            for name, config in sorted(prompts_with_desc):
                padded_name = name.ljust(max_name_length)
                click.echo(f"{click.style(padded_name, fg='green')}  {config['description']}")
        else:
            click.echo("No prompts with descriptions found.")
    else:
        # 이름만 출력
        for name in sorted(PROMPTS.keys()):
            click.echo(name)

if __name__ == '__main__':
    cli()
