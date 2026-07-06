# 🤖 simple-ai-chatbot– Intelligent AI Learning Assistant

> **An AI-powered multi-persona learning assistant built with Python, Streamlit, and Google Gemini API.**

ChatWise is an intelligent chatbot that provides personalized learning experiences through specialized AI experts. Unlike traditional chatbots, ChatWise allows users to switch between multiple AI personas such as Coding Expert, Python Mentor, AI Tutor, Teacher, Student Assistant, Translator, Career Advisor, and more.

The system combines **authentication**, **context-aware conversations**, **intent validation**, **streaming AI responses**, and **conversation management** to create a modern AI learning platform.

---

## 🚀 Features

### 🔐 Secure User Authentication
- User Registration
- Secure Login
- Password Reset
- User Profile Management
- Session Management

---

### 🤖 16 Specialized AI Experts

Choose from multiple AI tutors based on your needs.

| Mode | Description |
|------|-------------|
| 💬 General | General-purpose AI assistant |
| 🎓 Student | Beginner-friendly explanations |
| 👨‍🏫 Teacher | Professional teaching style |
| 💻 Coding | Programming expert |
| 🐍 Python | Python specialist |
| ☕ Java | Java expert |
| ⚙️ C++ | C++ expert |
| 🤖 Artificial Intelligence | AI concepts |
| 🧠 Machine Learning | ML algorithms |
| 📊 Deep Learning | Neural Networks |
| ✍ Content Writer | Professional writing |
| 📝 Grammar | Grammar correction |
| 🌍 Translator | Language translation |
| 📚 Study Notes | Quick revision notes |
| 🚀 Career Advisor | Career guidance |
| 🔍 Explain | Simple explanations |

---

### 📚 Adaptive Learning Levels

ChatWise automatically changes its teaching style.

- 🟢 Beginner
- 🟡 Intermediate
- 🔴 Advanced

---

### 🎯 Intent Validation

The chatbot checks whether your question belongs to the selected AI mode.

Example:

**Selected Mode:** Python

✅ Explain decorators

❌ Explain Mughal Empire

Instead of answering incorrectly, ChatWise politely asks users to switch to the appropriate AI mode.

---

### 💬 Smart Chat Experience

- Real-time streaming responses
- Conversation memory
- Chat history
- New Chat
- Delete Chat
- Continue Previous Conversations
- Export Conversations

---

### ⚡ Powered by Google Gemini

- Fast responses
- Streaming output
- Context-aware conversations
- Optimized prompt engineering

---

# 🖥️ Screenshots

> Add screenshots here

| Login | Chat | Profile |
|-------|------|---------|
| <img width="1906" height="897" alt="image" src="https://github.com/user-attachments/assets/3825db80-3377-4a23-a2c2-363bffbeffaf" /> | <img width="1917" height="917" alt="image" src="https://github.com/user-attachments/assets/58021673-ec04-423e-a793-fc65bba0f345" /> | <img width="1860" height="902" alt="image" src="https://github.com/user-attachments/assets/a15cc125-2c15-4da0-a626-e97f614affc7" /> |

---

# 🏗️ Project Architecture

```
                    User
                      │
                      ▼
            Authentication System
                      │
                      ▼
            Streamlit User Interface
                      │
                      ▼
            AI Mode Selection
                      │
                      ▼
           Intent Validation Engine
                      │
                      ▼
             Google Gemini API
                      │
                      ▼
         Streaming AI Response
                      │
                      ▼
        Chat History Management
```

---

# 📂 Folder Structure

```
ChatWise
│
├── app.py
├── auth.py
├── chat.py
├── modes.py
├── users.json
├── chats.json
├── requirements.txt
├── .env
└── README.md
```

---

# 🛠️ Tech Stack

### Frontend
- Streamlit

### Backend
- Python

### AI Model
- Google Gemini API

### SDK
- google-genai

### Database
- JSON

### Environment
- python-dotenv

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/Biraj021/simple-ai-chatbot.git

cd simple-ai-chatbot
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

---

## Activate Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Create Environment File

Create a `.env` file.

```env
GEMINI_API_KEY=YOUR_API_KEY
```

---

## Run Application

```bash
streamlit run app.py
```

---

# 📖 Workflow

```
User Login
      │
      ▼
Select AI Expert
      │
      ▼
Choose Learning Level
      │
      ▼
Intent Validation
      │
      ▼
Google Gemini API
      │
      ▼
AI Generates Response
      │
      ▼
Chat Saved Automatically
```

---

# 🌟 Key Highlights

- 🔐 Authentication System
- 🤖 Multiple AI Personas
- 📚 Adaptive Learning Levels
- 🎯 Intent Validation
- 💬 Streaming AI Responses
- 📂 Chat History
- 📤 Export Conversations
- ⚡ Fast User Experience
- 🎨 Clean Streamlit UI
- 🧠 Powered by Google Gemini

---

# 🎯 Future Improvements

- Firebase Authentication
- PostgreSQL / MongoDB Integration
- Voice Assistant
- Image Upload Support
- PDF Chat
- Retrieval-Augmented Generation (RAG)
- Multi-language Support
- Dark Theme
- Mobile Responsive Design
- Cloud Deployment

---

# 📦 Requirements

```text
streamlit
google-genai
python-dotenv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 👨‍💻 Author

## Biraj Acherjee

🔗 GitHub

https://github.com/Biraj021

🔗 LinkedIn

https://www.linkedin.com/in/birajacherjee

---

# 📜 License

This project is licensed under the MIT License.

---

# ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.

It helps support future AI and open-source projects.
