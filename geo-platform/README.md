# GEO Platform - Generative Engine Optimization

> **Take control of how AI sees you, be visible, accurate, and future-ready**

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd geo-platform

# Start infrastructure
docker-compose up -d postgres redis

# Setup backend
cd backend
npm install
npm run db:migrate
npm run dev

# Setup agents
cd ../agents
pip install -r requirements/dev.txt
celery -A src.tasks worker --loglevel=info

# Setup frontend
cd ../frontend
npm install
npm run dev
```

## 📁 Project Structure

```
geo-platform/
├── backend/                 # Node.js API gateway & crawling
├── agents/                  # Python AI agents
├── frontend/                # Next.js dashboard
├── shared/                  # Shared types and schemas
├── infrastructure/          # Docker, K8s, monitoring
├── docs/                    # Documentation
├── scripts/                 # Automation scripts
└── tests/                   # End-to-end tests
```

## 🏗️ Architecture

- **Frontend**: Next.js 14 + Tailwind CSS + shadcn/ui
- **Backend**: Node.js + Express + Prisma + BullMQ
- **AI Agents**: Python + FastAPI + LangChain + Celery
- **Databases**: PostgreSQL + Redis
- **Infrastructure**: Docker + Kubernetes

## 📊 Core Features

- **Website Analysis**: Automated crawling and content extraction
- **AI Visibility Testing**: Multi-platform AI engine testing
- **GEO Scoring**: Visibility, Accuracy, Actionability metrics
- **Automated Optimization**: AI-generated improvements
- **Real-time Dashboard**: Live analysis updates
- **GitHub Integration**: Automated PR creation

## 🔧 Development

See [docs/development.md](docs/development.md) for detailed setup instructions.

## 📈 Monitoring

- **Logs**: Winston (Node.js) + Python logging
- **Metrics**: Prometheus + Grafana
- **Health Checks**: `/health` endpoints on all services

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
