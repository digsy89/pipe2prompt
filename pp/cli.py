import click
import tomllib
from pathlib import Path
import os
from pp.core import run_task

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

# class DynamicCLI(click.Group):
#     def list_commands(self, ctx):
#         global PROMPTS
#         PROMPTS = load_prompts_from_toml()
#         return ['update'] + sorted(list(PROMPTS.keys()))
# 
#     def get_command(self, ctx, cmd_name):
#         if cmd_name == 'update':
#             @click.command(help="Update command completion")
#             def update():
#                 global PROMPTS
#                 PROMPTS = load_prompts_from_toml()
#                 print(PROMPTS)
#                 install_completion()
#                 click.echo("Command completion updated successfully")
#             return update
#             
#         if prompt_name in PROMPTS:
#             prompt_config = PROMPTS[prompt_name]
#             
#             @click.command(help=prompt_config.get('description', ''))
#             @click.pass_context
#             def dynamic_command(ctx):
#                 click.echo(f"Executing {prompt_name}")
#                 if 'command' in prompt_config:
#                     run_task(prompt_config['command'])
#                 
#             return dynamic_command
#         return None

@click.group()
def cli():
    """PP CLI Tool"""
    pass

@click.group()
def prompt():
    """Prompt management commands"""
    pass

cli.add_command(prompt)

def get_prompt_completions():
    global PROMPTS
    PROMPTS = load_prompts_from_toml()
    print(">_<", PROMPTS)
    print(list(PROMPTS.keys()))
    print(">_<")
    return list(PROMPTS.keys())

def install_completion():
    shell = os.environ.get('SHELL', '').split('/')[-1]
    
    if shell == 'bash':
        completion_script = '''
_pp_completion() {
    local commands="$(pp prompt list)"
    COMPREPLY=( $(compgen -W "${commands}" -- "${COMP_WORDS[1]}") )
}
complete -F _pp_completion pp
'''
        rc_file = os.path.expanduser('~/.bashrc')
    elif shell == 'zsh':
        completion_script = '''
_pp() {
    local commands=(${(f)"$(pp prompt list)"})
    _describe 'command' commands
}
compdef _pp pp
'''
        rc_file = os.path.expanduser('~/.zshrc')
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
    os.system(completion_script)

@prompt.command()
def update():
    """Update prompt completion"""
    install_completion()
    click.echo("Prompt completion updated successfully")

@prompt.command()
def list():
    """Internal command to get available commands for shell completion"""
    # 설명이 있는 프롬프트들만 필터링
    prompts_with_desc = [(name, config) for name, config in PROMPTS.items() if 'description' in config]
    
    # 가장 긴 프롬프트 이름의 길이 계산
    max_name_length = max(len(name) for name, _ in prompts_with_desc)
    
    # 정렬된 상태로 출력
    for name, config in sorted(prompts_with_desc):
        padded_name = name.ljust(max_name_length)
        click.echo(f"{click.style(padded_name, fg='green')}  {config['description']}")

if __name__ == '__main__':
    cli()
