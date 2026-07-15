#!/usr/bin/env bash
# Highway Pilot - Quick Start Setup Script

echo "🛣️  Highway Pilot - Quick Start Setup"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Backend Setup
echo -e "${BLUE}Step 1: Setting up Backend...${NC}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment
echo "Creating Python virtual environment..."
python -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate  # For Linux/Mac
# For Windows, use: .venv\Scripts\activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Setup environment
echo "Setting up environment file..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}⚠️  Please edit .env with your API keys:${NC}"
    echo "   - OPENAI_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - DATABASE_URL"
else
    echo -e "${GREEN}✅ .env already exists${NC}"
fi

echo ""
echo -e "${GREEN}✅ Backend setup complete!${NC}"
echo ""

# Step 2: Frontend Setup
echo -e "${BLUE}Step 2: Setting up Frontend...${NC}"
cd "$SCRIPT_DIR/pilot-web"

echo "Installing Node dependencies..."
npm install

echo ""
echo -e "${GREEN}✅ Frontend setup complete!${NC}"
echo ""

# Step 3: Start Services
echo -e "${BLUE}Step 3: Ready to Start Services${NC}"
echo ""
echo "To start the application:"
echo ""
echo -e "${YELLOW}Terminal 1 - Backend:${NC}"
echo "  cd $SCRIPT_DIR"
echo "  source .venv/bin/activate"
echo "  python -m uvicorn backend.app.main:app --reload --port 8000"
echo ""
echo -e "${YELLOW}Terminal 2 - Frontend:${NC}"
echo "  cd pilot-web"
echo "  npm run dev"
echo ""
echo -e "${YELLOW}Then open: ${GREEN}http://localhost:5173${NC}"
echo ""

# Summary
echo "════════════════════════════════════════════"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Follow the startup instructions above"
echo "2. Add your API keys to backend/.env"
echo "3. Open http://localhost:5173 in your browser"
echo "4. Start using Highway Pilot!"
echo ""
echo "For detailed information, see:"
echo "  - HIGHWAY_PILOT_SETUP.md - Full setup guide"
echo "  - README_HIGHWAY_PILOT.md - Project overview"
echo "  - IMPLEMENTATION_SUMMARY.md - What was built"
echo ""
