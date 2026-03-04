#!/bin/bash
# AIOS - AI Operating System
# One-Click Installer for Linux/macOS

set -e

echo "======================================================================"
echo "AIOS - AI Operating System"
echo "One-Click Installer for Linux/macOS"
echo "======================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ok() { echo -e "    ${GREEN}[OK]${NC} $1"; }
warn() { echo -e "    ${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "    ${RED}[ERROR]${NC} $1"; exit 1; }

# Step 1: Check Python
echo "[1/5] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        error "Python not found. Please install Python 3.8+ from https://python.org"
    fi
    PYTHON=python
else
    PYTHON=python3
fi

PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo "    Found Python $PYTHON_VERSION"

# Check Python 3.8+
$PYTHON -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" || \
    error "Python 3.8+ required. Found $PYTHON_VERSION"
ok "Python version compatible"

# Step 2: Check pip
echo ""
echo "[2/5] Checking pip..."
if ! $PYTHON -m pip --version &> /dev/null; then
    error "pip not found. Please install pip."
fi
ok "pip available"

# Step 3: Install optional dependencies
echo ""
echo "[3/5] Installing optional dependencies..."
$PYTHON -m pip install aiosqlite --quiet 2>/dev/null && \
    ok "aiosqlite installed" || \
    warn "aiosqlite not installed (optional, for Storage Manager)"

# Step 4: Verify AIOS files
echo ""
echo "[4/5] Verifying AIOS files..."

if [ ! -f "aios.py" ]; then
    error "aios.py not found. Please run this script from the AIOS directory."
fi
ok "aios.py found"

if [ ! -f "core/event_bus.py" ]; then
    error "core/event_bus.py not found. AIOS installation may be incomplete."
fi
ok "Core modules found"

if [ ! -f "agent_system/agents.json" ]; then
    warn "agent_system/agents.json not found. Creating default..."
    mkdir -p agent_system
    echo '{"agents": [], "metadata": {"last_updated": ""}}' > agent_system/agents.json
fi
ok "Agent system ready"

# Step 5: Run quick test
echo ""
echo "[5/5] Running quick test..."
$PYTHON aios.py version > /dev/null 2>&1 || \
    error "AIOS test failed. Please check the installation."
ok "AIOS test passed"

# Done
echo ""
echo "======================================================================"
echo "Installation Complete!"
echo "======================================================================"
echo ""
echo "Quick Start:"
echo "  $PYTHON aios.py demo --scenario 1    # File monitor demo"
echo "  $PYTHON aios.py demo --scenario 2    # API health check demo"
echo "  $PYTHON aios.py demo --scenario 3    # Log analysis demo"
echo ""
echo "  $PYTHON aios.py submit --desc 'My task' --type code --priority high"
echo "  $PYTHON aios.py tasks"
echo "  $PYTHON aios.py heartbeat"
echo ""
echo "  $PYTHON aios.py dashboard            # Open Dashboard"
echo ""
echo "Documentation: README.md"
echo "======================================================================"
