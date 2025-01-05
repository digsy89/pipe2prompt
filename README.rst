pipe2prompt (p2p)
================

A command-line tool that lets you pipe input into customizable AI prompts.

**Example Usage**

.. code-block:: bash

    # Generate a commit message from staged changes
    git diff --staged | p2p create-commit-message

**Example Output**

.. code-block:: text

    refactor: reorder imports in cli.py and update flake8 select list

    - Reorganize the import order in `pipe2prompt/cli.py` for better readability.
    - Remove the `isort` ("I") code from the flake8 select list in `pyproject.toml`.

Installation
-----------

Install from source:

.. code-block:: bash

    git clone https://github.com/digsy89/pipe2prompt
    cd pipe2prompt
    pip install --user .

This will:

1. Install the package locally with pip
2. Set up shell completion
3. Create initial config file at ``~/.p2p/config.toml``

Shell Completion
--------------

To manually set up completion:

.. code-block:: bash

    p2p init

This will:

1. Create completion scripts in your shell's completion directory
2. Add source commands to your shell config file
3. Enable tab completion for p2p commands and prompts

Supported shells:

- Bash (~/.bash_completion.d/_p2p)
- Zsh (~/.zsh/completions/_p2p) 
- Fish (~/.config/fish/completions/_p2p)

After installation, you may need to restart your shell or source your config file:

.. code-block:: bash

    # For bash
    source ~/.bashrc
    
    # For zsh
    source ~/.zshrc
    
    # For fish
    source ~/.config/fish/config.fish


Usage
-----

Basic usage:

.. code-block:: bash

    # Run a prompt directly
    p2p <prompt-name> "your input"
    
    # Pipe input into a prompt
    echo "your input" | p2p <prompt-name>

    # List available prompts
    p2p prompt list
    p2p prompt list --long

Configuration
------------

Prompts are configured in ``~/.p2p/config.toml``. Example configuration:

.. code-block:: toml

    [explain]
    content = "Explain this code: {pipe}"
    base_model = "gpt-3.5-turbo"
    description = "Explain code"

    [fix]
    content = "Fix this code and explain the issues: {pipe}" 
    base_model = "gpt-3.5-turbo"
    description = "Fix code issues"

Each prompt requires:

- ``content``: The prompt template. Use ``{pipe}`` to reference piped input
- ``base_model``: The OpenAI model to use
- ``description``: Description shown in help text
- ``enabled``: Optional boolean to enable/disable the prompt

License
-------

MIT