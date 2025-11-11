# M4 Max Setup Walkthrough

**Goal**: Set up your M4 Max as a remote workstation for ML/poetry work, accessible from your MacBook Air via SSH.

**Time Required**: ~30-45 minutes (mostly automated)

---

## Part 1: Prepare MacBook Air (Do This First)

### Step 1: Verify Tailscale is Running

```bash
tailscale status
```

You should see your Air listed. If not:
```bash
open /Applications/Tailscale.app
```

### Step 2: Generate SSH Key (if you don't have one)

Check if you already have a key:
```bash
ls -la ~/.ssh/id_ed25519*
```

If not, create one:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter for default location
# Enter a passphrase (recommended)
```

### Step 3: Note Your Air's Tailscale IP

```bash
tailscale ip -4
```

Write this down - you'll need it later if you want to SSH back from M4 Max to Air.

---

## Part 2: Initial M4 Max Setup (Unbox, First Boot)

### Step 1: Fresh macOS Install

When setting up your M4 Max:
- **Choose**: "Set up as new Mac" (NOT restore from backup)
- **Why**: Keep it clean for compute work only
- Sign in with your Apple ID
- Complete basic setup (name, password, etc.)

### Step 2: Open Terminal

Open Terminal.app (Applications > Utilities > Terminal)

### Step 3: Install Xcode Command Line Tools

```bash
xcode-select --install
```

Click "Install" in the dialog that appears. This takes 5-10 minutes.

---

## Part 3: Run Automated Setup Script

### Step 1: Download Setup Script

```bash
cd ~/Downloads
curl -O https://raw.githubusercontent.com/JustinStec/poetry-bert-formalism/main/setup_m4max.sh
chmod +x setup_m4max.sh
```

### Step 2: Run Setup Script

```bash
./setup_m4max.sh
```

**Important**: The script will pause at Tailscale installation. When it does:

1. Tailscale.app will open automatically
2. Click "Log In"
3. Sign in with the **same account** you use on your Air
4. Wait for it to connect
5. Return to Terminal and press Enter to continue

### Step 3: Get M4 Max Tailscale IP

When the script finishes, it will display your Tailscale IP. Write it down:

```bash
tailscale ip -4
# Example: 100.101.102.103
```

### Step 4: Note SSH Copy Command

The script will show a command like:
```
From Air: ssh-copy-id username@100.x.x.x
```

Keep Terminal open - you'll use this in the next step.

---

## Part 4: Connect from MacBook Air

### Step 1: Copy SSH Key to M4 Max

On your **MacBook Air**, run the command shown by the setup script:

```bash
ssh-copy-id username@100.x.x.x
# Replace with your actual username and IP
```

Enter your M4 Max password when prompted.

### Step 2: Update Air SSH Config

On your **MacBook Air**:

```bash
nano ~/.ssh/config
```

Add this (replace with your actual IP and username):

```
Host m4max
    HostName 100.x.x.x
    User your_username
    IdentityFile ~/.ssh/id_ed25519
    ForwardAgent yes
    ServerAliveInterval 60
    LocalForward 8888 localhost:8888
    LocalForward 8000 localhost:8000
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 3: Test SSH Connection

From your **MacBook Air**:

```bash
ssh m4max
```

You should connect without a password! You're now on your M4 Max.

---

## Part 5: Verify Everything Works

Run these commands **on the M4 Max** (via SSH from Air):

### 1. Activate Poetry Environment

```bash
poetry-env
```

You should see:
```
Poetry BERT environment activated
Python: /Users/username/venv-poetry/bin/python
Project: /Users/username/poetry-bert-formalism
```

### 2. Test MLX (Apple Silicon ML)

```bash
python -c "import mlx.core as mx; print('MLX works:', mx.array([1, 2, 3]))"
```

### 3. Test PyTorch

```bash
python -c "import torch; print('PyTorch version:', torch.__version__)"
```

### 4. Check Corpus

```bash
ls ~/poetry-bert-formalism/data/processed/poetry_platform_renamed | wc -l
```

Should show: `116674`

### 5. Check coverletter_tagger

```bash
ls ~/coverletter_tagger
```

Should show: `backend/`, `frontend/`, etc.

---

## Part 6: Setup coverletter_tagger OpenAI Key

The setup script prompted for your OpenAI API key. If you need to change it:

```bash
cd ~/coverletter_tagger/backend
nano .env
```

Add/update:
```
OPENAI_API_KEY=sk-your-key-here
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## Part 7: Daily Workflow Examples

### Start a Training Session

From **MacBook Air**:

```bash
ssh m4max
poetry-env
tmux new -s training

# Now you're in a persistent session
cd ~/poetry-bert-formalism
python scripts/your_training_script.py

# Detach from tmux (keeps running)
# Press: Ctrl+B, then D
```

You can close your Air, training continues!

### Reconnect Later

```bash
ssh m4max
tmux attach -t training
```

### Run coverletter_tagger Backend

```bash
ssh m4max
cd ~/coverletter_tagger/backend
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Access from Air browser: `http://localhost:8000`

### Use Jupyter Notebooks

```bash
ssh m4max
poetry-env
jupyter notebook --no-browser --port=8888
```

Access from Air browser: `http://localhost:8888`

(Copy the token from the terminal output)

### Edit Files with VS Code

1. Install "Remote - SSH" extension in VS Code on Air
2. `Cmd+Shift+P` → "Remote-SSH: Connect to Host"
3. Select "m4max"
4. Edit files directly on M4 Max
5. Terminal in VS Code runs on M4 Max

---

## Part 8: Troubleshooting

### Can't SSH to M4 Max

```bash
# Check Tailscale on both machines
tailscale status

# Verify M4 Max IP
tailscale ip -4

# Test ping
ping 100.x.x.x
```

### Lost tmux Session

```bash
# List all sessions
tmux ls

# Attach to any session
tmux attach -t training
```

### Python Environment Issues

```bash
# Deactivate and reactivate
deactivate
source ~/venv-poetry/bin/activate
```

---

## Part 9: Useful Commands Reference

```bash
# SSH to M4 Max
ssh m4max

# Activate poetry environment
poetry-env

# New tmux session
tmux new -s mysession

# List tmux sessions
tmux ls

# Attach to session
tmux attach -t mysession

# Detach from tmux
Ctrl+B, then D

# Kill session
tmux kill-session -t mysession

# Check Tailscale status
tailscale status

# Update poetry-bert repo
cd ~/poetry-bert-formalism && git pull

# Check disk space
df -h

# Check running processes
top
```

---

## Summary Checklist

After setup, verify:

- [ ] Can SSH from Air to M4 Max without password
- [ ] Tailscale shows both devices connected
- [ ] `poetry-env` command works
- [ ] MLX imports successfully
- [ ] PyTorch imports successfully
- [ ] 116,674 poems in corpus directory
- [ ] coverletter_tagger directory exists
- [ ] tmux works
- [ ] Jupyter runs

---

## Next Steps (After Setup Complete)

1. **Commit this setup**: You're ready for Phase 3
2. **Phase 3 Work**: Fine-tune local LLM for historical classification
   - 12 periods (Ancient, Medieval, Renaissance, etc.)
   - 13+ movements (Romanticism, Symbolism, etc.)
   - 4 modes (Lyric, Narrative, Dramatic, Satirical)
3. **Use MLX** for Apple Silicon-optimized training

---

## Questions?

- Review `M4MAX_SETUP_GUIDE.md` for more details
- Check `TODO.md` for project roadmap
- All scripts in `scripts/` directory
- Documentation in `docs/` directory

---

**You're all set!** Your M4 Max is now a dedicated ML workstation accessible from anywhere via Tailscale.
