cat > README.md << 'EOF'

Genetic algorithm for optimizing drone survey routes in Curitiba, Brazil.

##  Project Description

This project implements a genetic algorithm to optimize drone routes for surveying multiple locations in Curitiba while considering:
- Battery autonomy and recharging
- Weather conditions (wind speed/direction)
- Time constraints and operational costs
- Multiple-day scheduling

##  Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/seu-usuario/drone-route-optimizer.git
cd drone-route-optimizer

# Create virtual environment
python -m venv venv

# Activate environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create sample data
python create_sample_data.py

# Run optimization
python main.py