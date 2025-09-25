# 🚀 **COMPREHENSIVE EXPERIMENT COMMANDS**

## 📋 **Quick Reference: All Models & Variants**

### **Available Models:**
- `default` - GPT-4.1-nano (Default configuration)
- `gpt-4.1-nano` - GPT-4.1-nano (Explicit)
- `gpt-4o-mini` - GPT-4o-mini (Fast & Cost-effective)
- `deepseek-v3` - DeepSeek-V3 (Alternative perspective)

### **Available Meta Prompts:**
- `crocodile_conservation_intelligence`
- `healthcare_cost_prediction_system`
- `global_economic_intelligence`
- `educational_performance_optimization`
- `fraud_detection_intelligence`
- `shakespeare_sonnet_linguistic_analysis`
- `mathematical_proof_assistant`
- `journey_to_the_west_analysis`
- `grid_runner_game_development`
- `todo_lite_app_development`

---

## 🎯 **SINGLE EXPERIMENTS**

### **Basic Single Experiments (Different Models)**

```bash
# GPT-4.1-nano (High Quality)
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4.1-nano \
  --num_agents 5 \
  --num_rounds 3 \
  --boids_enabled

# GPT-4o-mini (Fast & Cost-effective)
python run_real_experiment.py \
  --meta_prompt_id healthcare_cost_prediction_system \
  --model gpt-4o-mini \
  --num_agents 5 \
  --num_rounds 3 \
  --boids_enabled

# DeepSeek-V3 (Alternative perspective)
python run_real_experiment.py \
  --meta_prompt_id shakespeare_sonnet_linguistic_analysis \
  --model deepseek-v3 \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled
```

### **Boids Rule Variants (Individual Rules)**

```bash
# Separation Only
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4o-mini \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled \
  --boids_separation

# Alignment Only
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4o-mini \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled \
  --boids_alignment

# Cohesion Only
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4o-mini \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled \
  --boids_cohesion

# All Rules Combined
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4o-mini \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled \
  --boids_separation \
  --boids_alignment \
  --boids_cohesion
```

### **Evolution & Self-Reflection Variants**

```bash
# With Evolution
python run_real_experiment.py \
  --meta_prompt_id healthcare_cost_prediction_system \
  --model gpt-4.1-nano \
  --num_agents 4 \
  --num_rounds 3 \
  --boids_enabled \
  --evolution_enabled \
  --evolution_frequency 2 \
  --evolution_selection_rate 0.3

# With Self-Reflection
python run_real_experiment.py \
  --meta_prompt_id fraud_detection_intelligence \
  --model gpt-4o-mini \
  --num_agents 4 \
  --num_rounds 3 \
  --boids_enabled \
  --self_reflection

# Without Self-Reflection (Explicit)
python run_real_experiment.py \
  --meta_prompt_id global_economic_intelligence \
  --model gpt-4.1-nano \
  --num_agents 4 \
  --num_rounds 3 \
  --boids_enabled \
  --no_self_reflection
```

### **Baseline (No Boids) Experiments**

```bash
# Pure Baseline - No Boids
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4.1-nano \
  --num_agents 5 \
  --num_rounds 3

# Baseline with Different Models
python run_real_experiment.py \
  --meta_prompt_id healthcare_cost_prediction_system \
  --model gpt-4o-mini \
  --num_agents 5 \
  --num_rounds 3

python run_real_experiment.py \
  --meta_prompt_id shakespeare_sonnet_linguistic_analysis \
  --model deepseek-v3 \
  --num_agents 3 \
  --num_rounds 2
```

---

## 🧪 **ABLATION STUDIES**

### **Complete Ablation Studies (All 7 Variants)**

```bash
# GPT-4.1-nano Ablation Study
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4.1-nano \
  --mode ablation \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_k 2 \
  --boids_sep 0.45 \
  --evolution_frequency 3 \
  --evolution_selection_rate 0.2

# GPT-4o-mini Ablation Study (Cost-effective)
python run_real_experiment.py \
  --meta_prompt_id healthcare_cost_prediction_system \
  --model gpt-4o-mini \
  --mode ablation \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_k 3 \
  --boids_sep 0.5

# DeepSeek-V3 Ablation Study
python run_real_experiment.py \
  --meta_prompt_id shakespeare_sonnet_linguistic_analysis \
  --model deepseek-v3 \
  --mode ablation \
  --num_agents 2 \
  --num_rounds 2
```

### **Quick Ablation Studies (Smaller Scale)**

```bash
# Mini Ablation - 2 agents, 1 round (for testing)
python run_real_experiment.py \
  --meta_prompt_id fraud_detection_intelligence \
  --model gpt-4o-mini \
  --mode ablation \
  --num_agents 2 \
  --num_rounds 1

# Medium Ablation - 4 agents, 3 rounds
python run_real_experiment.py \
  --meta_prompt_id global_economic_intelligence \
  --model gpt-4.1-nano \
  --mode ablation \
  --num_agents 4 \
  --num_rounds 3
```

---

## 📊 **COMPARATIVE STUDIES**

### **Model Comparison (Same Task)**

```bash
# Compare all models on same task
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4.1-nano \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled

python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4o-mini \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled

python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model deepseek-v3 \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled
```

### **Boids vs Baseline Comparison**

```bash
# Boids Version
python run_real_experiment.py \
  --meta_prompt_id healthcare_cost_prediction_system \
  --model gpt-4.1-nano \
  --num_agents 5 \
  --num_rounds 3 \
  --boids_enabled \
  --boids_k 2 \
  --boids_sep 0.45

# Baseline Version (No Boids)
python run_real_experiment.py \
  --meta_prompt_id healthcare_cost_prediction_system \
  --model gpt-4.1-nano \
  --num_agents 5 \
  --num_rounds 3
```

---

## 🎨 **SPECIALIZED EXPERIMENTS**

### **PDF-Based Tasks**

```bash
# Shakespeare Analysis with GPT-4.1-nano
python run_real_experiment.py \
  --meta_prompt_id shakespeare_sonnet_linguistic_analysis \
  --model gpt-4.1-nano \
  --num_agents 4 \
  --num_rounds 3 \
  --boids_enabled

# Mathematical Proof Assistant
python run_real_experiment.py \
  --meta_prompt_id mathematical_proof_assistant \
  --model gpt-4.1-nano \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled

# Journey to the West Analysis
python run_real_experiment.py \
  --meta_prompt_id journey_to_the_west_analysis \
  --model deepseek-v3 \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled
```

### **Data Science Tasks**

```bash
# Healthcare Cost Prediction
python run_real_experiment.py \
  --meta_prompt_id healthcare_cost_prediction_system \
  --model gpt-4o-mini \
  --num_agents 5 \
  --num_rounds 3 \
  --boids_enabled

# Fraud Detection
python run_real_experiment.py \
  --meta_prompt_id fraud_detection_intelligence \
  --model gpt-4.1-nano \
  --num_agents 4 \
  --num_rounds 3 \
  --boids_enabled

# Economic Intelligence
python run_real_experiment.py \
  --meta_prompt_id global_economic_intelligence \
  --model gpt-4.1-nano \
  --num_agents 4 \
  --num_rounds 3 \
  --boids_enabled
```

### **Software Development Tasks**

```bash
# Game Development
python run_real_experiment.py \
  --meta_prompt_id grid_runner_game_development \
  --model gpt-4.1-nano \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled

# App Development
python run_real_experiment.py \
  --meta_prompt_id todo_lite_app_development \
  --model gpt-4o-mini \
  --num_agents 3 \
  --num_rounds 2 \
  --boids_enabled
```

---

## ⚡ **QUICK TEST COMMANDS**

### **Minimal Tests (Fast Validation)**

```bash
# Ultra-fast test (1 agent, 1 round)
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4o-mini \
  --num_agents 1 \
  --num_rounds 1 \
  --boids_enabled

# Quick model test
python run_real_experiment.py \
  --meta_prompt_id healthcare_cost_prediction_system \
  --model deepseek-v3 \
  --num_agents 2 \
  --num_rounds 1 \
  --boids_enabled
```

---

## 🔧 **PARAMETER TUNING EXPERIMENTS**

### **Boids Parameter Variations**

```bash
# High Separation Threshold
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4o-mini \
  --num_agents 4 \
  --num_rounds 2 \
  --boids_enabled \
  --boids_k 3 \
  --boids_sep 0.7

# Low Separation Threshold
python run_real_experiment.py \
  --meta_prompt_id crocodile_conservation_intelligence \
  --model gpt-4o-mini \
  --num_agents 4 \
  --num_rounds 2 \
  --boids_enabled \
  --boids_k 2 \
  --boids_sep 0.3

# High K Neighbors
python run_real_experiment.py \
  --meta_prompt_id healthcare_cost_prediction_system \
  --model gpt-4.1-nano \
  --num_agents 5 \
  --num_rounds 2 \
  --boids_enabled \
  --boids_k 4 \
  --boids_sep 0.45
```

### **Evolution Parameter Variations**

```bash
# Frequent Evolution
python run_real_experiment.py \
  --meta_prompt_id fraud_detection_intelligence \
  --model gpt-4.1-nano \
  --num_agents 4 \
  --num_rounds 4 \
  --boids_enabled \
  --evolution_enabled \
  --evolution_frequency 2 \
  --evolution_selection_rate 0.4

# Rare Evolution
python run_real_experiment.py \
  --meta_prompt_id global_economic_intelligence \
  --model gpt-4.1-nano \
  --num_agents 4 \
  --num_rounds 6 \
  --boids_enabled \
  --evolution_enabled \
  --evolution_frequency 5 \
  --evolution_selection_rate 0.1
```

---

## 🎯 **RECOMMENDED EXPERIMENT SEQUENCES**

### **For Research Papers (High Quality)**

```bash
# 1. Baseline Comparison
python run_real_experiment.py --meta_prompt_id crocodile_conservation_intelligence --model gpt-4.1-nano --num_agents 5 --num_rounds 5
python run_real_experiment.py --meta_prompt_id crocodile_conservation_intelligence --model gpt-4.1-nano --num_agents 5 --num_rounds 5 --boids_enabled

# 2. Full Ablation Study
python run_real_experiment.py --meta_prompt_id healthcare_cost_prediction_system --model gpt-4.1-nano --mode ablation --num_agents 5 --num_rounds 4

# 3. Model Comparison
python run_real_experiment.py --meta_prompt_id shakespeare_sonnet_linguistic_analysis --model gpt-4.1-nano --num_agents 4 --num_rounds 3 --boids_enabled
python run_real_experiment.py --meta_prompt_id shakespeare_sonnet_linguistic_analysis --model deepseek-v3 --num_agents 4 --num_rounds 3 --boids_enabled
```

### **For Quick Prototyping (Cost-effective)**

```bash
# 1. Quick validation
python run_real_experiment.py --meta_prompt_id fraud_detection_intelligence --model gpt-4o-mini --num_agents 3 --num_rounds 2 --boids_enabled

# 2. Mini ablation
python run_real_experiment.py --meta_prompt_id healthcare_cost_prediction_system --model gpt-4o-mini --mode ablation --num_agents 2 --num_rounds 2

# 3. Parameter testing
python run_real_experiment.py --meta_prompt_id global_economic_intelligence --model gpt-4o-mini --num_agents 3 --num_rounds 2 --boids_enabled --boids_k 3 --boids_sep 0.6
```

---

## 📝 **NOTES**

- **GPT-4.1-nano**: Best for high-quality, complex experiments
- **GPT-4o-mini**: Best for rapid prototyping and cost-effective testing
- **DeepSeek-V3**: Best for alternative perspectives and diversity
- **Ablation mode**: Automatically runs all 7 variants (baseline, individual rules, combined, evolution, self-reflection)
- **Default parameters**: `boids_k=2`, `boids_sep=0.45`, `evolution_frequency=5`, `evolution_selection_rate=0.2`

**🚀 Ready to run serious experiments with multiple models and configurations!**
