# Installation and model configuration

## 1. Install the plugin

Copy the whole directory to a personal plugin directory, for example:

```text
C:\Users\<your-user>\.agents\plugins\codex-comprehensive-orchestrator
```

Keep the `.codex-plugin/plugin.json` file and the `skills/` directory at the plugin root. A development copy under `outputs/` is not automatically the installed copy.

For a marketplace-backed personal installation, follow the Plugin Creator update flow rather than hand-editing marketplace metadata. After installing or updating, reload the Codex plugin list. The plugin manifest version is currently `0.4.0`.

## 2. One-command cross-platform setup

A GitHub download cannot safely auto-execute code. Run the bundled installer once after download:

```powershell
# Windows
.\install.ps1

# macOS/Linux
python3 install.py
```

The installer copies the plugin to the user-local `~/plugins/` directory, creates or merges the personal marketplace at `~/.agents/plugins/marketplace.json`, creates a disabled local `model_catalog.json`, and invokes `codex plugin marketplace add` / `codex plugin add` when the Codex CLI is available. Use `python install.py --no-register` to skip Codex registration. It preserves unrelated marketplace entries and never creates or transfers credentials. Start a new Codex task/thread after installation.

## 3. Configure model routing (optional)

The plugin does not ship with provider credentials and does not assume that Qwen, OpenAI, Anthropic, or any other external provider is available.

1. Copy `model_catalog.example.json` to a private file such as `model_catalog.json`.
2. Set the current model capabilities conservatively.
3. Add only models you are authorized to use.
4. Set `configured: true` only after the endpoint and authentication are actually available.
5. Keep API keys in environment variables. Use `api_key_env` only to name the variable; never put the key value in the JSON catalog.

Example:

```text
python scripts/model_selector.py "识别图片并制作PPT" --catalog model_catalog.json --json
```

A model marked `configured: false` or `enabled: false` is never selected. The selector is offline and only returns a recommendation. The host model or an explicitly authorized tool must perform the actual call.

## 4. Temporary API access

If a task needs an external model and you choose to provide temporary access:

- use a short-lived, least-privilege key;
- provide it through the host secret manager or an environment variable, not in a prompt or file;
- transfer only the task goal, relevant inputs, and acceptance criteria;
- do not upload unrelated files, credentials, or private data without consent;
- remove temporary environment/configuration files and revoke the key after completion;
- report whether cleanup succeeded.

If no provider is configured, the correct result is `request_user_configuration`, not a fabricated model response.

## 5. What this plugin can and cannot do

The plugin supplies orchestration policy, domain Skills, read-only helper scripts, and a model-choice protocol. Actual ability depends on the Codex host, installed tools, permissions, connectors, network access, and user authorization.

It does not itself provide:

- a full antivirus engine or guaranteed malware detection;
- automatic browser/desktop control when computer-use tools are absent;
- built-in access to every model provider or unlimited parallel workers;
- permission to delete, quarantine, kill, install, publish, purchase, deploy, or send anything;
- a substitute for professional medical, legal, financial, security, or biological review.

## 6. Reload and cleanup

After changing the plugin, reload the plugin in Codex. During development, tests may create `scripts/__pycache__/`; it is safe to remove that directory from this plugin before packaging. Do not delete unrelated workspace files.

Run validation from the plugin root:

```text
python C:\Users\Christina\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py .
python scripts/test_universal_router.py
python scripts/test_command_detector_unit.py
python scripts/test_installer.py
python scripts/test_model_selector.py
python scripts/smoke_test.py
```
