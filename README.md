# 📚 Snap & Study

Snap & Study is an AI-powered Streamlit study assistant that helps students understand questions, problems, diagrams, and notes.

You can:

* 📸 Upload a photo of a question, diagram, or study material.
* 💬 Ask questions using text.
* 🤖 Get simple explanations and step-by-step answers from Gemini.
* 📧 Save your study conversation summary to your email.
* 🗑️ Clear the chat and start a new study session.

## 🛠️ Tech Stack

* Python
* Streamlit
* Google Gemini API
* Gmail SMTP

## ▶️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/snap-and-study.git
cd snap-and-study
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your secrets

Create:

```text
.streamlit/secrets.toml
```

Add:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
GMAIL_ADDRESS = "your-gmail-address"
GMAIL_APP_PASSWORD = "your-gmail-app-password"
```

Never commit `secrets.toml` to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 📁 Project Structure

```text
snap-and-study/
│
├── .streamlit/
│   └── secrets.toml.example
├── app.py
├── prompts.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔐 Security

API keys and email credentials are stored using Streamlit secrets and are excluded from Git using `.gitignore`.
