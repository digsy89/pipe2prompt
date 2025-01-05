import os
import logging
from pathlib import Path
import subprocess

from .utils import highlight

SUPPORTED_SHELLS = {
    'bash': {
        'config_file': '.bashrc',
        'completion_directory': '.bash_completion.d',
    },
    'zsh': {
        'config_file': '.zshrc',
        'completion_directory': '.zsh/completions',
    },
    'fish': {
        'config_file': '.config/fish/config.fish',
        'completion_directory': '.config/fish/completions',
    }
}


def install_shell_completion():
    """Validate and update shell completion for the CLI"""
    shell = os.environ.get('SHELL', '').split('/')[-1]
    if not shell:
        logging.error("Could not determine shell type")
        return

    if shell not in SUPPORTED_SHELLS:
        logging.error(f"Unsupported shell: `{shell}`. Supported shells: {SUPPORTED_SHELLS}")
        return

    home = Path('~')
    completion_command = f"_P2P_COMPLETE={shell}_source p2p"
    completion_command = subprocess.run(
        completion_command, shell=True, check=True, capture_output=True, text=True).stdout
    completion_directory = home / SUPPORTED_SHELLS[shell]['completion_directory']
    completion_directory.mkdir(parents=True, exist_ok=True)
    completion_file = completion_directory / '_p2p'
    completion_file.write_text(completion_command)
    run_completion_command = f"source {str(completion_file)}"

    shell_config_file = home / SUPPORTED_SHELLS[shell]['config_file']
    shell_config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(shell_config_file, 'a+') as f:
        f.seek(0)
        content = f.read()
        start_tag = "# >>> p2p shell completion >>>"
        end_tag = "# <<< p2p shell completion <<<"

        if run_completion_command not in content:
            f.write(f"\n{start_tag}")
            f.write(f"\n{run_completion_command}")
            f.write(f"\n{end_tag}")
            logging.info(f"Added completion script to {shell_config_file}")
        else:
            logging.info("Completion script already installed")

    print(f"Completion script installed to {shell_config_file}")
    print(f"Run `{highlight(run_completion_command)}` to enable completion in the current session")
