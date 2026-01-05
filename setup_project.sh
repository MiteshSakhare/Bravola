#!/bin/bash

set -e

echo "🚀 Setting up Bravola Mini SaaS..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create project structure
echo -e "${BLUE}📁 Creating directory structure...${NC}"
mkdir -p backend/app/{api/v1,core,models,schemas,discovery,benchmark,strategy,feedback,integrations,ml,utils}
mkdir -p backend/scripts
mkdir -p backend/tests/{test_api,test_discovery,test_benchmark,test_strategy}
mkdir -p backend/alembic/versions
mkdir -p backend/data/raw

mkdir -p frontend/src/{pages,components/{layout,discovery,benchmark,strategy,campaigns,common},hooks,api,store/slices,styles,utils}
mkdir -p frontend/public

mkdir -p ml_artifacts/{discovery/{models,preprocessors},benchmark/{models,preprocessors},strategy/{models,preprocessors}}

echo -e "${GREEN}✅ Directory structure created${NC}"

# Backend setup
echo -e "${BLUE}🐍 Setting up Python backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo -e "${GREEN}✅ Python dependencies installed${NC}"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created from template${NC}"
fi

cd ..

# Frontend setup
echo -e "${BLUE}⚛️  Setting up React frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    npm install
    echo -e "${GREEN}✅ Node dependencies installed${NC}"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Frontend .env file created${NC}"
fi

cd ..

# Database setup
echo -e "${BLUE}🗄️  Starting database...${NC}"
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
sleep 5

# Run migrations
echo -e "${BLUE}📊 Running database migrations...${NC}"
cd backend
source venv/bin/activate
alembic upgrade head
cd ..

echo -e "${GREEN}✅ Database migrations complete${NC}"

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Generate synthetic data: ${BLUE}make data${NC}"
echo "  2. Train ML models: ${BLUE}make train${NC}"
echo "  3. Test inference: ${BLUE}make test-ml${NC}"
echo "  4. Start the application: ${BLUE}make dev${NC}"
echo ""
echo "Access the application at:"
echo "  Frontend: ${BLUE}http://localhost:5173${NC}"
echo "  Backend API: ${BLUE}http://localhost:8000${NC}"
echo "  API Docs: ${BLUE}http://localhost:8000/docs${NC}"
