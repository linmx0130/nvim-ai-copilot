nvim-ai-copilot
===
Simple AI code completion for neovim.

## Dependencies
This project should be run with [`uv`](https://github.com/astral-sh/uv).

## `config.py`
Configuration on which model to use and which API provider to call should be set in this file.

An example can be found at `config.py.example`.

## Enable the tool in `init.lua`
Add following code into `init.lua` in your nvim config.
```lua 
vim.keymap.set('n', '<C-n>', function()
  vim.cmd('silent! execute "!uv --directory [PATH_TO_PLUGIN_FOLDER] run main.py " . v:servername . " & "')
end)
```

Then you can invoke the AI completion in normal mode with `Ctrl + N`.

## Copyright
Copyright (c) 2025 Mengxiao Lin. See [LICENSE](LICENSE) for more details.
