🤖 ConnectsProBot – Advanced Telegram Chatbot

✔ Create Your Bot
✔ Let Users Create Their Own Bot
✔ Auto-Trial System
✔ Auto-Delete Old Messages
✔ Anti-Spam
✔ Railway Deployment
✔ No URL Needed
✔ Works Perfectly From Phone


---

🚀 Features

Feature	Status

3–4 Month Free Trial	✔
Auto Subscription	✔
Auto Trial Blocker	✔
Anti Spam	✔
Upload JSON Export	✔
Multi-Language	✔
Start With This Bot	✔
Create Your Own Bot	✔
PostgreSQL Database	✔
Deployed With Railway	✔



---

📁 Project Structure

connectsprobot/
│
├─ main.py                # App entry
├─ config.py              # Env & config
├─ database.py            # Database models
├─ requirements.txt       # All libraries
├─ .env.example           # Sample variables
│
├─ handlers/
│   ├─ menu.py
│   ├─ admin.py
│   ├─ user.py
│   ├─ trialstop.py
│   └─ lang.py
│
├─ jobs/
│   ├─ cleanup.py
│   └─ trialchecker.py
│
├─ services/
│   ├─ bot_factory.py
│   ├─ trial_service.py
│   └─ message_router.py
│
├─ templates/
│   ├─ intro_text.py
│   ├─ footer.py
│   └─ menus.py
│
└─ README.md


---

⚙️ Setup (Phone / PC)

Install GitHub App
Install Railway App OR open railway.app in browser
Install Termux (Android users)


---

🔧 Installation Commands (Termux)

pkg install python
pkg install git
git clone https://github.com/YOURUSERNAME/connectsprobot.git
cd connectsprobot
pip install -r requirements.txt


---

✍ Create .env File

Create a new file .env

BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id
DATABASE_URL=your_railway_postgres_url
FREE_TRIAL_DAYS=120
