#!/bin/bash
# ============================================================
# AI Shield - One-Click Installer
# Usage: curl -sL https://raw.githubusercontent.com/USER/ai-shield/main/install.sh | bash
# ============================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="${HOME}/.ai-shield"
REPO_URL="https://github.com/akzkak-web/ai-shield.git"
VERSION="1.0.0"

banner() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║        🛡️  AI Shield Installer        ║${NC}"
    echo -e "${BLUE}║     Local AI Security Scanner          ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
    echo ""
}

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()   { echo -e "${RED}[ERROR]${NC} $1"; }

# Check Python
check_python() {
    info "Checking Python..."
    if command -v python3 &>/dev/null; then
        PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
        if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 9 ]; then
            ok "Python $PY_VER found"
            return 0
        fi
    fi
    err "Python 3.9+ is required but not found."
    echo ""
    echo "Install Python:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS:         brew install python3"
    echo "  CentOS/RHEL:   sudo dnf install python3 python3-pip"
    echo ""
    exit 1
}

# Install
install() {
    banner

    # Check python
    check_python

    # Create install directory
    mkdir -p "$INSTALL_DIR"

    # Check if running from repo or need to clone
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
    if [ -f "$SCRIPT_DIR/ai-shield.py" ] && [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        info "Installing from local source: $SCRIPT_DIR"
        SOURCE_DIR="$SCRIPT_DIR"
    else
        info "Cloning repository..."
        if command -v git &>/dev/null; then
            git clone --depth 1 "$REPO_URL" "$INSTALL_DIR/src" 2>/dev/null || {
                warn "Git clone failed. Trying alternative..."
                # Fallback: download tarball
                curl -sL "https://github.com/USER/ai-shield/archive/refs/heads/main.tar.gz" | tar xz -C "$INSTALL_DIR"
                mv "$INSTALL_DIR/ai-shield-main" "$INSTALL_DIR/src"
            }
            SOURCE_DIR="$INSTALL_DIR/src"
        else
            err "Git is required. Install with: sudo apt install git / brew install git"
            exit 1
        fi
    fi

    # Create virtual environment
    info "Creating virtual environment..."
    python3 -m venv "$INSTALL_DIR/venv" 2>/dev/null || {
        warn "venv module not found, trying virtualenv..."
        pip3 install virtualenv
        virtualenv "$INSTALL_DIR/venv"
    }
    source "$INSTALL_DIR/venv/bin/activate"

    # Install dependencies
    info "Installing dependencies..."
    pip install --quiet --upgrade pip
    pip install --quiet -r "$SOURCE_DIR/requirements.txt"
    ok "Dependencies installed"

    # Copy source if from remote
    if [ "$SOURCE_DIR" != "$SCRIPT_DIR" ] && [ "$SOURCE_DIR" != "$INSTALL_DIR/src" ]; then
        cp -r "$SOURCE_DIR"/* "$INSTALL_DIR/src/" 2>/dev/null || true
    fi

    # Create launcher script
    info "Creating launcher..."
    cat > "$INSTALL_DIR/ai-shield" << 'LAUNCHER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
cd "$SCRIPT_DIR/src"
python ai-shield.py "$@"
LAUNCHER
    chmod +x "$INSTALL_DIR/ai-shield"

    # Create symlink
    if [ -w "/usr/local/bin" ] 2>/dev/null; then
        ln -sf "$INSTALL_DIR/ai-shield" /usr/local/bin/ai-shield
    else
        # Add to PATH via shell profile
        SHELL_RC=""
        if [ -f "$HOME/.bashrc" ]; then
            SHELL_RC="$HOME/.bashrc"
        elif [ -f "$HOME/.zshrc" ]; then
            SHELL_RC="$HOME/.zshrc"
        fi

        if [ -n "$SHELL_RC" ]; then
            if ! grep -q "ai-shield" "$SHELL_RC" 2>/dev/null; then
                echo "export PATH=\"\$HOME/.ai-shield:\$PATH\"  # AI Shield" >> "$SHELL_RC"
                info "Added to PATH in $SHELL_RC"
            fi
        fi
    fi

    # Done
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     ✅  AI Shield installed!           ║${NC}"
    echo -e "${GREEN}╠═══════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║                                       ║${NC}"
    echo -e "${GREEN}║  Start Web UI:                        ║${NC}"
    echo -e "${GREEN}║    ai-shield web                      ║${NC}"
    echo -e "${GREEN}║                                       ║${NC}"
    echo -e "${GREEN}║  CLI Scan:                            ║${NC}"
    echo -e "${GREEN}║    ai-shield scan 127.0.0.1            ║${NC}"
    echo -e "${GREEN}║                                       ║${NC}"
    echo -e "${GREEN}║  Help:                                ║${NC}"
    echo -e "${GREEN}║    ai-shield --help                   ║${NC}"
    echo -e "${GREEN}║                                       ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BLUE}Open http://127.0.0.1:8899 after running:${NC}"
    echo -e "  ${YELLOW}ai-shield web${NC}"
    echo ""
}

# Uninstall
uninstall() {
    info "Uninstalling AI Shield..."
    rm -rf "$INSTALL_DIR"
    rm -f /usr/local/bin/ai-shield 2>/dev/null
    ok "AI Shield removed."
}

# Main
case "${1:-install}" in
    install)  install ;;
    uninstall) uninstall ;;
    *)
        echo "Usage: $0 {install|uninstall}"
        exit 1
        ;;
esac
