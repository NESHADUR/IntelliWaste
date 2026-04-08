# ♻️ IntelliWaste - Agentic Smart Waste Management System

> 🤖 An intelligent multi-agent system that revolutionizes waste management using AI computer vision and large language models.

## 📖 About The Project

**IntelliWaste** is an automated waste processing system that simulates a smart recycling facility using multiple specialized AI agents. When you upload an image of waste, the system:

1. **Classifies** the waste type (biodegradable, non-biodegradable, e-waste, or mixed)
2. **Identifies** individual components and recyclable materials
3. **Generates** appropriate treatment protocols
4. **Calculates** honor scores based on recycling value
5. **Sends** personalized email confirmations with recycling facts

This project demonstrates how AI agents can collaborate to solve real-world environmental challenges, making waste management more efficient, educational, and engaging.

## ✨ Key Features

- 🧠 **Multi-Agent Architecture** - 4 specialized AI agents working in concert
- 🔍 **Smart Classification** - Identifies waste type with reasoning
- 📦 **Component Detection** - Breaks down complex waste into recyclable parts
- ⚙️ **Treatment Protocols** - Generates material-specific recycling procedures
- 📧 **Automated Reports** - Sends personalized emails with honor scores
- 🎮 **Gamification** - Earn points for proper waste disposal
- 🌍 **Environmental Education** - Includes fun recycling facts

## 🛠️ Tech Stack

- **Python**: Core programming language
- **Frontend**: Streamlit
- **LLM Provider**: Alibaba Cloud DashScope (Qwen-VL-Plus, Qwen-Plus)
- **Qwen-VL-Plus**: Vision AI for image analysis
- **Qwen-Plus**: Text AI for email generation
- **DashScope API**: Alibaba Cloud AI API
- **Relay.app**: Email automation & webhook
- **python-dotenv**" Environment variable management
- **Image Processing**: PIL/Pillow

## ⚙️ Setup

### Prerequisites

- Python 3.9 or higher
- A [DashScope API key](https://dashscope.aliyun.com/) (Alibaba Cloud)
- A [Relay.app](https://relay.app/) account (for email notifications)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/NESHADUR/IntelliWaste.git
cd IntelliWaste
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:

```env
DASHSCOPE_API_KEY="your_dashscope_api_key_here"
RELAY_URL="your_relay_webhook_url_here"
```

### Running the Application

```bash
streamlit run IntelliWaste_App.py
```

The app will open in your browser at `http://localhost:8501`

## 📱 Usage

1. **Enter your email address** for receiving processing confirmations
2. **Upload a waste image** (supports JPG, JPEG, PNG formats)
   - Examples: plastic bottles, food waste, electronic items, mixed trash
3. **Click "Initiate Automated Treatment"**
   - The Classifier Agent analyzes your image
   - Based on classification, specialized agents process the waste
4. **Review the AI analysis**:
   - Waste classification with reasoning
   - Component identification
   - Treatment protocol
   - Recycling recommendations
5. **Check your email** for a personalized confirmation with:
   - Honor points earned
   - Interesting recycling facts
   - Environmental impact summary

### Example Waste Types

| Waste Type | Examples | Points per Item |
|------------|----------|-----------------|
| ♻️ Biodegradable | Food scraps, paper, wood | 10 points |
| 🗑️ Non-biodegradable | Plastics, glass, metals | 15 points |
| 📱 E-waste | Batteries, phones, cables | 25 points |
| 🔄 Mixed | Combination of above | Varies |

## 🤖 How the Agents Work

### 1. Classifier Agent
- Analyzes image and determines waste category
- Provides reasoning for classification

### 2. Component Identification Agent
- Lists specific items found in the waste
- Creates inventory of materials

### 3. Separator Agent (for mixed waste)
- Breaks down mixed waste into categories
- Counts items in each category

### 4. Recycling Agent
- Identifies recyclable materials
- Provides step-by-step recycling protocols
- Suggests what recycled materials become

## 🎯 Real-World Applications

- 🏢 **Corporate waste management** - Automate sorting in office buildings
- 🏫 **Educational institutions** - Teach students about recycling
- 🏭 **Recycling facilities** - Augment manual sorting processes
- 🏠 **Smart homes** - Help families recycle correctly

## 🔮 Future Roadmap

- [ ] Mobile app with camera integration
- [ ] Real-time video processing
- [ ] Carbon footprint calculation
- [ ] Blockchain-based recycling rewards
- [ ] Integration with municipal waste systems
- [ ] Multi-language support
- [ ] Historical data analytics dashboard

## 🙏 Acknowledgments

- **Alibaba Cloud DashScope** - For providing the Qwen-VL-Plus API
- **Streamlit** - For the amazing rapid application framework
- **Relay.app** - For webhook automation and email delivery
- **OpenAI** - For inspiring the agent-based architecture pattern

## 📞 Contact & Support

- **Email**: intelliwasteteam@gmail.com
- **Project Link**: [https://github.com/NESHADUR/IntelliWaste](https://github.com/NESHADUR/IntelliWaste)
