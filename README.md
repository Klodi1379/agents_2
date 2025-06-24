# 🤖 AI Company - Autonomous Business Analysis Platform

Një platformë revolucionare që përdor agjentë të inteligjencës artificiale për të analizuar dhe vlerësuar idetë e biznesit. E ndërtuar me Django dhe e pajisur me një ekip virtual agjentësh të AI që simulojnë një kompani të vërtetë analitike.

## 🌟 Karakteristikat Kryesore

### 🏢 Kompania Autonome e AI
- **CEO Agent**: Orkestron të gjithë procesin dhe krijon përmbledhjen ekzekutive
- **Market Research Agent**: Analizon tregun, konkurrencën dhe segmentet e klientëve
- **Financial Analyst**: Vlerëson qëndrueshmërinë financiare dhe krijon projeksione
- **Technical Lead**: Vlerëson realizueshmërinë teknike dhe arkitekturën
- **Risk Analyst**: Identifikon rreziqet dhe strategjitë e zbutjes
- **Marketing Strategist**: Zhvillon strategji marketingu dhe marrjen e klientëve
- **Idea Generator**: Gjeneron ide të reja biznesi bazuar në kritere

### 📊 Analiza Gjithëpërfshirëse
- Vlerësim i detajuar të tregut dhe konkurrencës
- Modelim financiar dhe projeksione fitimi
- Analizë e realizueshmërisë teknike
- Vlerësim i rrezikut gjithëpërfshirës
- Strategji marketingu dhe shitjesh
- Rekomandime ekzekutive dhe vendimmarrje

### 🔄 Përditësime në Kohë Reale
- Ndjekje e progresit të analizës në kohë reale
- Përditësime automatike të statusit
- Dashboard interaktiv me metrika
- Njoftimet dhe alertet

### 📈 Analytics dhe Raportim
- Analiza e performancës së ideve
- Metrika të agjentëve të AI
- Trendet dhe insight-et
- Raporte të detajuara të eksportit

## 🏗️ Arkitektura Teknike

```
┌─────────────────────────────────────────────────────────────┐
│                     Django Web Platform                     │
├─────────────────────────────────────────────────────────────┤
│  Web Interface │ API Layer │ Task Orchestrator │ Dashboard  │
├─────────────────────────────────────────────────────────────┤
│                    Agent Communication Layer                │
├─────────────────────────────────────────────────────────────┤
│ CEO Agent │ Market │ Finance │ Tech │ Risk │ Marketing │... │
├─────────────────────────────────────────────────────────────┤
│        LLM Services (OpenAI/Claude/Local Models)            │
├─────────────────────────────────────────────────────────────┤
│    External Data Sources │ Task Queue │ Database            │
└─────────────────────────────────────────────────────────────┘
```

### Komponentët Kryesorë
- **Django**: Framework web për ndërfaqen dhe API
- **Celery**: Queue i detyrave për proceset e sfondit
- **Redis**: Cache dhe broker për Celery
- **PostgreSQL**: Baza e të dhënave kryesore
- **OpenAI/Anthropic**: Shërbimet e LLM për agjentët
- **Bootstrap**: Framework frontend për UI

## 🚀 Fillimi i Shpejtë

### ⚡ Docker Setup (Rekomandohet)
```bash
# 1. Clone the repository
git clone <repository-url>
cd ai_company

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys (see below)

# 3. Start with Docker
docker-compose up --build
```

### 🔧 Local Development Setup
```bash
# 1. Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Setup database
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# 5. Start services (in separate terminals)
python manage.py runserver                    # Terminal 1
celery -A ai_company worker --loglevel=info   # Terminal 2
celery -A ai_company beat --loglevel=info     # Terminal 3 (optional)
```

## 🔧 Konfigurimi

### API Keys të Kërkuara
Ndrysho `.env` file me:

```env
# OpenAI API Key (required)
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API Key (optional, por rekomandohet)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Database Configuration
DB_NAME=ai_company_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### Marrja e API Keys
- **OpenAI**: Shko tek [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic**: Shko tek [Anthropic Console](https://console.anthropic.com/)

## 💡 Si të Përdorni

### 1. Krijimi i Llogarisë
- Hyr në `http://localhost:8000`
- Kliko "Create Account" për të regjistruar
- Ose përdor superuser account-in që krijove

### 2. Dorëzimi i Idesë së Biznesit
- Kliko "Submit New Idea" në dashboard
- Mbush formularin me detaje:
  - **Titulli**: Emri i qartë i idesë
  - **Përshkrimi**: Detaje gjithëpërfshirëse (minimum 20 karaktere)
  - **Industria**: Zgjedh industrinë relevante
  - **Tregu i Synuar**: Përshkrim i klientëve të synuar
  - **Buxheti**: Investimi i parashikuar fillestar

### 3. Ndjekja e Analizës
- Shiko progresin në kohë reale
- Çdo agjent përfundon analizën e tij
- Merr njoftimet kur analiza përfundon

### 4. Shikimi i Rezultateve
- **Raporti Individual i Agjentëve**: Analiza e detajuar nga çdo agjent
- **Raporti Final**: Përmbledhja ekzekutive dhe rekomandimet
- **Nota Gjithëpërfshirëse**: Vlerësim 1-100 për realizueshmërinë

### 5. Analytics dhe Insights
- Shiko performancën e ideve tuaja
- Analizo trendet dhe metritat
- Krahasimet me industrinë

## 📊 Tipet e Analizës

### Market Research
- Madhësia dhe rritja e tregut (TAM/SAM/SOM)
- Analiza e konkurrencës
- Segmentimi i klientëve
- Trendet e tregut

### Financial Analysis
- Modeli i të ardhurave
- Struktura e kostos
- Projeksionet financiare
- Analiza e break-even

### Technical Feasibility
- Kompleksiteti i implementimit
- Arkitektura e sistemit
- Stack-u teknologjik
- Timeline i zhvillimit

### Risk Assessment
- Rreziqet e tregut
- Rreziqet operacionale
- Rreziqet financiare
- Strategjitë e zbutjes

### Marketing Strategy
- Pozicionimi i markës
- Strategjia e kanaleve
- Planifikimi i marrjes së klientëve
- ROI i marketingut

## 🔌 API Documentation

### Endpoints Kryesorë

```
GET  /api/business-ideas/           # Lista e ideve
POST /api/business-ideas/           # Dorëzo ide të re
GET  /api/business-ideas/{id}/      # Detajet e idesë
GET  /api/business-ideas/{id}/analysis-status/  # Statusi i analizës
GET  /api/agent-reports/            # Raportet e agjentëve
GET  /api/analytics/platform-metrics/  # Metrikat e platformës
```

### Shembuj Përdorimi

```python
import requests

# Dorëzimi i idesë së re
response = requests.post('http://localhost:8000/api/business-ideas/', {
    'title': 'AI-Powered Restaurant Management',
    'description': 'A comprehensive system for managing restaurant operations...',
    'industry': 'TECH',
    'target_market': 'Small to medium restaurants',
    'estimated_budget': 50000
})

# Kontrollimi i statusit
idea_id = response.json()['id']
status = requests.get(f'http://localhost:8000/api/business-ideas/{idea_id}/analysis-status/')
```

## 🛠️ Zhvillimi dhe Kontributi

### Struktura e Projektit
```
ai_company/
├── ai_company/          # Django project settings
├── analysis_engine/     # Core business logic
├── agent_system/        # AI agents implementation
├── dashboard/           # Web interface
├── templates/           # HTML templates
├── static/             # CSS, JS, images
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # Docker configuration
└── README.md           # This file
```

### Shtimi i Agjentëve të Rinj

1. **Krijo klasën e agjentit** në `agent_system/extended_agents.py`:
```python
class MyNewAgent(BaseAIAgent):
    def __init__(self):
        super().__init__("MyNewAgent", "gpt-4-turbo-preview")
    
    def get_system_prompt(self) -> str:
        return "You are a specialist in..."
    
    def get_analysis_prompt(self, context: AnalysisContext) -> str:
        return f"Analyze this business idea: {context.title}..."
    
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        # Parse LLM response into structured data
        return {}
```

2. **Regjistro agjentin** në `initialize_all_agents()`

3. **Shto në modelin** `AgentReport.AGENT_TYPES`

### Testing

```bash
# Run unit tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📈 Monitorimi dhe Logs

### Celery Monitoring
```bash
# Flower (Web UI for Celery)
celery -A ai_company flower
# Visit http://localhost:5555
```

### Logs
- Application logs: `logs/ai_company.log`
- Agent execution logs në Django admin
- Celery logs në terminali

## 🔒 Siguria dhe Performanca

### Siguria
- API rate limiting
- Input validation dhe sanitization
- Secure environment variables
- HTTPS për production

### Performanca
- Async agent execution me Celery
- Database indexing për queries të shpejtë
- Caching me Redis
- Optimizim i query-eve të bazës

## 🚀 Deployment

### Production Setup
1. **Environment Variables**
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

2. **Docker Production**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Manual Deployment**
- Configure Nginx/Apache
- Setup SSL certificates
- Configure process manager (systemd/supervisor)
- Setup monitoring (Sentry, etc.)

## 🆘 Troubleshooting

### Problemet e Zakonshme

**Agent nuk funksionon**
```bash
# Check API keys
echo $OPENAI_API_KEY
# Check Celery worker
celery -A ai_company worker --loglevel=debug
```

**Database errors**
```bash
# Reset database
python manage.py flush
python manage.py migrate
```

**Permission errors**
```bash
# Fix file permissions
chmod +x setup.sh
chmod -R 755 static/
```

## 📚 Dokumentacioni i Avancuar

### Customizing Agents
- [Agent Development Guide](docs/agent-development.md)
- [Prompt Engineering Best Practices](docs/prompt-engineering.md)
- [Model Integration Guide](docs/model-integration.md)

### API Integration
- [REST API Documentation](docs/api-documentation.md)
- [Webhook Integration](docs/webhooks.md)
- [Authentication Guide](docs/authentication.md)

## 🤝 Kontributi

Ne mirëpresim kontributet! Ju lutemi:

1. Fork projektin
2. Krijo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit ndryshimet (`git commit -m 'Add some AmazingFeature'`)
4. Push në branch (`git push origin feature/AmazingFeature`)
5. Hap një Pull Request

## 📄 Liçensa

Ky projekt është licensuar nën MIT License - shiko `LICENSE` file për detaje.

## 🙏 Falënderime

- OpenAI për GPT models
- Anthropic për Claude models
- Django community për framework-un e shkëlqyer
- Celery team për task queue system

## 📞 Kontakti dhe Suporti

- **GitHub Issues**: [Project Issues](https://github.com/yourusername/ai-company/issues)
- **Email**: support@aicompany.com
- **Documentation**: [Full Documentation](https://docs.aicompany.com)

---

**🚀 Filloni udhëtimin tuaj të analizës së biznesit me AI sot!**
