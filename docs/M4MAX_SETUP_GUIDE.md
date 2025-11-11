# M4 Max Setup Guide

Quick reference for setting up your M4 Max as a remote workstation.

---

## Architecture Overview

**MacBook Air** (Daily driver):
- VS Code (edits files remotely)
- SSH client
- Tailscale
- Git (optional, for reviewing)
- Lightweight work

**M4 Max** (Compute workhorse):
- Full poetry corpus (116,674 poems, ~10GB)
- Python/ML environment (MLX, PyTorch, etc.)
- Training scripts & checkpoints
- Jupyter notebooks
- All heavy computation

**Connection**: Tailscale VPN (works through eduroam firewall)

---

## One-Time Setup

### On M4 Max (When It Arrives):

1. **Run automated setup script:**
   ```bash
   # Download and run
   curl -O https://raw.githubusercontent.com/JustinStec/poetry-bert-formalism/main/setup_m4max.sh
   chmod +x setup_m4max.sh
   ./setup_m4max.sh
   ```

   This installs:
   - Tailscale
   - Python 3.11 + virtual environment
   - MLX (Apple Silicon ML framework)
   - PyTorch, Transformers, Datasets
   - tmux (persistent sessions)
   - Jupyter
   - Poetry BERT repository
   - Security settings

2. **During setup, you'll need to:**
   - Log into Tailscale (same account as Air)
   - Copy SSH key from Air (script will show command)

3. **Get Tailscale IP:**
   ```bash
   tailscale ip -4
   # Example output: 100.101.102.103
   ```

### On MacBook Air:

1. **Update SSH config:**
   ```bash
   nano ~/.ssh/config
   ```

   Add:
   ```
   Host m4max
       HostName 100.x.x.x  # IP from M4 Max Tailscale
       User <YOUR_USERNAME>
       IdentityFile ~/.ssh/id_ed25519
       ForwardAgent yes
       ServerAliveInterval 60
       LocalForward 8888 localhost:8888
   ```

2. **Copy SSH key to M4 Max:**
   ```bash
   ssh-copy-id username@100.x.x.x
   ```

3. **Test connection:**
   ```bash
   ssh m4max
   ```

---

## Daily Workflow

### Starting Work Session:

```bash
# From Air, connect to M4 Max
ssh m4max

# Activate environment
poetry-env

# Start tmux session (persistent)
tmux new -s training

# Work on your code
cd ~/poetry-bert-formalism
python scripts/train_llm.py

# Detach from tmux (keeps running)
# Press: Ctrl+B, then D
```

### Reconnecting Later:

```bash
# From Air
ssh m4max

# Reconnect to existing session
tmux attach -t training

# Your work is still running!
```

### Using VS Code Remote:

1. Open VS Code on Air
2. `Cmd+Shift+P` → "Remote-SSH: Connect to Host"
3. Select "m4max"
4. Edit files directly on M4 Max
5. Terminal in VS Code runs on M4 Max

### Using Jupyter:

```bash
# On M4 Max
ssh m4max
poetry-env
jupyter notebook --no-browser --port=8888

# Access from Air's browser:
# http://localhost:8888
# (Port forwarding in SSH config handles this)
```

---

## Quick Reference

### Useful Commands:

```bash
# SSH to M4 Max
ssh m4max

# Activate environment
poetry-env

# Check GPU/memory
system_profiler SPDisplaysDataType

# List tmux sessions
tmux ls

# Attach to session
tmux attach -t training

# Kill session
tmux kill-session -t training

# Check Tailscale status
tailscale status

# Update repository
cd ~/poetry-bert-formalism && git pull

# Check Python environment
which python
pip list
```

### File Transfer:

```bash
# Copy from Air to M4 Max
scp file.txt m4max:~/poetry-bert-formalism/

# Copy from M4 Max to Air
scp m4max:~/poetry-bert-formalism/results.txt ./

# Sync entire directory
rsync -avz --progress ~/local_dir/ m4max:~/remote_dir/
```

---

## Troubleshooting

### Can't connect via SSH:
1. Check Tailscale is running on both machines
2. Verify IP: `tailscale ip -4`
3. Test ping: `ping 100.x.x.x`
4. Check SSH service: `ssh m4max "sudo systemsetup -getremotelogin"`

### Lost tmux session:
```bash
# List all sessions
tmux ls

# Attach to last session
tmux attach
```

### Python environment issues:
```bash
# Deactivate and reactivate
deactivate
source ~/venv-poetry/bin/activate

# Reinstall packages if needed
pip install -r requirements.txt
```

### Disk space:
```bash
# Check usage
df -h

# Find large files
du -sh ~/poetry-bert-formalism/*

# Clean pip cache
pip cache purge
```

---

## Security Notes

- SSH password authentication disabled (keys only)
- Firewall enabled
- Only accessible via Tailscale VPN
- Keep SSH key passphrase secure
- Regular macOS updates

---

## Testing Checklist

After setup, verify:

- [ ] Can SSH from Air to M4 Max
- [ ] Tailscale shows both devices
- [ ] SSH keys work (no password)
- [ ] VS Code Remote-SSH connects
- [ ] Python environment activates
- [ ] MLX imports: `python -c "import mlx.core as mx"`
- [ ] PyTorch works: `python -c "import torch; print(torch.__version__)"`
- [ ] Repository cloned: `ls ~/poetry-bert-formalism`
- [ ] Corpus accessible: `ls ~/poetry-bert-formalism/data/processed/poetry_platform_renamed | wc -l`
- [ ] tmux works: `tmux new -s test`
- [ ] Jupyter runs: `jupyter notebook --version`

---

## Resources

- **MLX Documentation**: https://ml-explore.github.io/mlx/
- **Tailscale Docs**: https://tailscale.com/kb/
- **tmux Cheat Sheet**: https://tmuxcheatsheet.com/
- **VS Code Remote-SSH**: https://code.visualstudio.com/docs/remote/ssh

---

**Questions?** Review this guide or check project documentation.
