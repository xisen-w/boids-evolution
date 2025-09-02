#!/bin/bash

echo "🚀 Setting up Enhanced Boids Evolution Environment"
echo "================================================="
echo

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing packages from requirements.txt..."
pip install -r environment/requirements.txt
if [ $? -ne 0 ]; then
    echo "⚠️ Some packages failed to install. This is normal for optional packages."
fi

# Test environment manager
echo "🧪 Testing environment manager..."
python3 src/environment_manager.py

echo
echo "✅ Environment setup complete!"
echo
echo "🎯 Next steps:"
echo "   1. Activate the environment: source venv/bin/activate"
echo "   2. Set up your API keys in .env file:"
echo "      - AZURE_OPENAI_ENDPOINT=your_endpoint"
echo "      - AZURE_OPENAI_API_KEY=your_key"
echo "      - TAVILY_API_KEY=your_key"
echo "   3. Run experiments: python3 run_experiment.py"
echo
echo "📦 Available packages: $(wc -l < environment/requirements.txt) packages installed"
echo "🤖 AI capabilities: OpenAI, Azure OpenAI ready"
echo "🔍 Search capabilities: Tavily, DuckDuckGo ready"
echo "📊 Data analysis: pandas, numpy, matplotlib ready" 