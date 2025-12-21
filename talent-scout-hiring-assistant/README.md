# TalentScout - AI Hiring Assistant Chatbot 🤖

An intelligent hiring assistant chatbot that streamlines the initial candidate screening process for technology placements. Built with Streamlit and powered by Large Language Models (LLMs), this chatbot collects candidate information and generates relevant technical questions based on their declared tech stack.

## 🌐 Live Demo

**Hosted Application:**   http://15.206.165.134:8501/

---

## 📋 Project Overview

TalentScout is an AI-powered recruitment tool designed for a fictional recruitment agency specializing in technology placements [web:6][web:9]. The chatbot assists in the initial screening by:

- Gathering essential candidate information
- Collecting tech stack details
- Generating personalized technical questions based on candidate's expertise
- Maintaining conversational context throughout the interaction
- Providing a seamless, user-friendly experience

---

## ✨ Key Features

### Core Functionality
- **Intelligent Greeting & Introduction**: Welcomes candidates and explains the purpose
- **Information Collection**: Gathers essential details including:
  - Full Name
  - Email Address
  - Phone Number
  - Years of Experience
  - Desired Position(s)
  - Current Location
  - Tech Stack (programming languages, frameworks, databases, tools)
- **Dynamic Question Generation**: Creates 3-5 tailored technical questions based on declared tech stack
- **Context Management**: Maintains conversation flow and handles follow-up questions
- **Fallback Handling**: Provides meaningful responses for unexpected inputs
- **Purpose-Focused**: Stays on track and doesn't deviate from hiring assistant role
- **Graceful Exit**: Concludes conversations professionally with next-steps information

### Technical Highlights
- Real-time response generation using LLMs
- Clean and intuitive user interface
- Secure handling of candidate information
- Conversation exit keywords support

---

## 🛠️ Tech Stack

- **Programming Language**: Python 3.8+
- **Frontend Framework**: Streamlit
- **LLM Integration**: OpenAI GPT / Google Gemini / Ollama (specify your model)
- **Data Storage**: JSON/CSV for candidate data persistence
- **Deployment**: AWS EC2 (Ubuntu Server)
- **Version Control**: Git & GitHub

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- API keys for LLM service (if using cloud-based models)

### Local Installation

1. **Clone the repository**
