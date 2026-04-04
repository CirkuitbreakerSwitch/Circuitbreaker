# Contributing to CircuitBreaker

First off, thank you for considering contributing to CircuitBreaker! 

## Where to start?

### Good First Issues
Look for issues labeled `good first issue` or `help wanted`.

### Areas We Need Help
- 🔌 **More integrations** (CrewAI, AutoGPT, etc.)
- 📊 **Dashboard/UI** (React/Vue frontend)
- 🧪 **More tests** (edge cases, performance)
- 📝 **Documentation** (tutorials, examples)
- 🌍 **Translations** (README in other languages)

## Development Setup

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Circuitbreaker.git
   cd Circuitbreaker

Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

Run tests
python -m pytest tests/ -v

Create .env file
cp .env.example .env
# Edit .env with your settings (optional for basic dev)

Making Changes
git checkout -b feature/your-feature-name

Make your changes
Write clean, documented code
Add tests for new features
Update README if needed

Test your changes
python -m pytest tests/
python quickstart.py  # Make sure quickstart still works

Commit
git add .
git commit -m "Add feature: description"

Push and create PR
git push origin feature/your-feature-name

Code Style
Follow PEP 8
Use type hints where possible
Add docstrings to functions
Keep functions focused and small

Commit Message Format
Add feature: brief description

Longer explanation if needed.

Fixes #123

Questions?
Open an issue for discussion
Join our Discord (coming soon)
Email: cirkuitbreaker@gmail.com
