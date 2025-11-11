#!/bin/bash
################################################################################
# M4 Max Setup Script - Poetry BERT Project
# Run this on your M4 Max after initial OS setup
################################################################################

set -e  # Exit on error

echo "=================================="
echo "M4 Max Poetry BERT Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo -e "${RED}Error: This script is for Apple Silicon Macs only${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Detected Apple Silicon${NC}"
echo ""

################################################################################
# 1. Enable Remote Login
################################################################################
echo "Step 1: Enabling Remote Login (SSH)..."
sudo systemsetup -setremotelogin on
echo -e "${GREEN}✓ Remote Login enabled${NC}"
echo ""

################################################################################
# 2. Install Homebrew (if not installed)
################################################################################
if ! command -v brew &> /dev/null; then
    echo "Step 2: Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add to PATH for Apple Silicon
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo -e "${GREEN}✓ Homebrew installed${NC}"
else
    echo "Step 2: Homebrew already installed"
    echo -e "${GREEN}✓ Homebrew ready${NC}"
fi
echo ""

################################################################################
# 3. Install Tailscale
################################################################################
if ! command -v tailscale &> /dev/null; then
    echo "Step 3: Installing Tailscale..."
    brew install --cask tailscale
    echo -e "${YELLOW}! Please open Tailscale.app and log in${NC}"
    echo -e "${YELLOW}! Then run this script again${NC}"
    open /Applications/Tailscale.app
    exit 0
else
    echo "Step 3: Tailscale already installed"
    echo -e "${GREEN}✓ Tailscale ready${NC}"
fi
echo ""

################################################################################
# 4. Install Python 3.11
################################################################################
echo "Step 4: Installing Python 3.11..."
brew install python@3.11
echo -e "${GREEN}✓ Python 3.11 installed${NC}"
echo ""

################################################################################
# 5. Install tmux for persistent sessions
################################################################################
echo "Step 5: Installing tmux..."
brew install tmux

# Create tmux config
cat > ~/.tmux.conf << 'EOF'
# Enable mouse support
set -g mouse on

# Increase scrollback buffer
set -g history-limit 10000

# Better colors
set -g default-terminal "screen-256color"

# Easy config reload
bind r source-file ~/.tmux.conf \; display "Config reloaded!"

# Split panes using | and -
bind | split-window -h
bind - split-window -v
EOF

echo -e "${GREEN}✓ tmux installed and configured${NC}"
echo ""

################################################################################
# 6. Install ML dependencies
################################################################################
echo "Step 6: Installing ML libraries (this may take a while)..."

# Create virtual environment
python3.11 -m venv ~/venv-poetry
source ~/venv-poetry/bin/activate

# Upgrade pip
pip install --upgrade pip

echo "  Installing MLX (Apple Silicon ML framework)..."
pip install mlx mlx-lm

echo "  Installing PyTorch..."
pip install torch torchvision torchaudio

echo "  Installing Transformers & Datasets..."
pip install transformers datasets accelerate

echo "  Installing standard ML/data libraries..."
pip install numpy pandas scikit-learn matplotlib seaborn tqdm

echo "  Installing Jupyter..."
pip install jupyter ipykernel notebook

echo "  Installing other utilities..."
pip install python-dotenv pyyaml

# Add kernel to Jupyter
python -m ipykernel install --user --name=poetry-bert --display-name="Poetry BERT (MLX)"

echo -e "${GREEN}✓ ML libraries installed${NC}"
echo ""

################################################################################
# 7. Clone repository
################################################################################
echo "Step 7: Cloning Poetry BERT repository..."
cd ~/
if [ ! -d "poetry-bert-formalism" ]; then
    git clone git@github.com:JustinStec/poetry-bert-formalism.git
    cd poetry-bert-formalism
    echo -e "${GREEN}✓ Repository cloned${NC}"
else
    echo "Repository already exists"
    cd poetry-bert-formalism
    git pull
    echo -e "${GREEN}✓ Repository updated${NC}"
fi
echo ""

################################################################################
# 8. Create activation script
################################################################################
echo "Step 8: Creating activation script..."
cat > ~/activate_poetry.sh << 'EOF'
#!/bin/bash
# Activate Poetry BERT environment

# Activate virtual environment
source ~/venv-poetry/bin/activate

# Navigate to project
cd ~/poetry-bert-formalism

echo "Poetry BERT environment activated"
echo "Python: $(which python)"
echo "Project: $(pwd)"
echo ""
echo "Quick commands:"
echo "  jupyter notebook  - Start Jupyter"
echo "  tmux new -s train - New tmux session"
echo "  git status        - Check repo status"
EOF

chmod +x ~/activate_poetry.sh

# Add alias to shell profile
if ! grep -q "alias poetry-env" ~/.zshrc 2>/dev/null; then
    echo "alias poetry-env='source ~/activate_poetry.sh'" >> ~/.zshrc
fi

echo -e "${GREEN}✓ Activation script created${NC}"
echo "  Use: ${YELLOW}poetry-env${NC} to activate environment"
echo ""

################################################################################
# 9. Setup coverletter_tagger
################################################################################
echo "Step 9: Setting up coverletter_tagger..."
cd ~/

if [ ! -d "coverletter_tagger" ]; then
    git clone git@github.com:JustinStec/coverletter_tagger.git
    cd coverletter_tagger
    echo -e "${GREEN}✓ Repository cloned${NC}"
else
    echo "Repository already exists"
    cd coverletter_tagger
    git pull
    echo -e "${GREEN}✓ Repository updated${NC}"
fi

# Create backend virtual environment
echo "  Setting up backend environment..."
cd backend
python3.11 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install --upgrade pip
pip install fastapi uvicorn openai pyyaml pypdf2 sentence-transformers python-multipart python-dotenv

# Prompt for OpenAI API key
echo ""
echo -e "${YELLOW}Please enter your OpenAI API key:${NC}"
read -r OPENAI_KEY

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=$OPENAI_KEY
EOF

echo -e "${GREEN}✓ Backend setup complete${NC}"
deactivate

# Setup frontend
cd ../frontend
if command -v node &> /dev/null; then
    echo "  Installing frontend dependencies..."
    npm install
    echo -e "${GREEN}✓ Frontend setup complete${NC}"
else
    echo -e "${YELLOW}! Node.js not installed, skipping frontend setup${NC}"
    echo "  Install Node.js with: brew install node"
fi

cd ~/
echo -e "${GREEN}✓ coverletter_tagger ready${NC}"
echo ""

################################################################################
# 10. Security setup
################################################################################
echo "Step 10: Configuring security..."

# Disable password authentication for SSH (keys only)
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
sudo sed -i '' 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i '' 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Restart SSH
sudo launchctl unload /System/Library/LaunchDaemons/ssh.plist 2>/dev/null || true
sudo launchctl load -w /System/Library/LaunchDaemons/ssh.plist

# Enable firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on

echo -e "${GREEN}✓ Security configured${NC}"
echo ""

################################################################################
# 11. Display info
################################################################################
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo -e "${GREEN}Tailscale IP:${NC} $(tailscale ip -4 2>/dev/null || echo 'Run: tailscale ip -4')"
echo ""
echo "Next steps:"
echo "  1. ${YELLOW}Copy SSH key from Air:${NC}"
echo "     From Air: ssh-copy-id $(whoami)@\$(tailscale ip -4)"
echo ""
echo "  2. ${YELLOW}Test SSH from Air:${NC}"
echo "     ssh m4max"
echo ""
echo "  3. ${YELLOW}Activate Poetry BERT environment:${NC}"
echo "     poetry-env"
echo ""
echo "  4. ${YELLOW}Start Jupyter (optional):${NC}"
echo "     jupyter notebook --no-browser --port=8888"
echo "     (Access from Air: http://localhost:8888)"
echo ""
echo "  5. ${YELLOW}Test MLX:${NC}"
echo "     python -c 'import mlx.core as mx; print(mx.array([1, 2, 3]))'"
echo ""
echo "  6. ${YELLOW}Run coverletter_tagger backend:${NC}"
echo "     cd ~/coverletter_tagger/backend"
echo "     source venv/bin/activate"
echo "     uvicorn api.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Projects installed:"
echo "  ${GREEN}✓${NC} ~/poetry-bert-formalism"
echo "  ${GREEN}✓${NC} ~/coverletter_tagger"
echo ""
echo "Useful commands:"
echo "  ${YELLOW}tmux new -s training${NC}  - Start persistent session"
echo "  ${YELLOW}tmux attach -t training${NC} - Reconnect to session"
echo "  ${YELLOW}Ctrl+B, then D${NC}        - Detach from tmux"
echo ""
