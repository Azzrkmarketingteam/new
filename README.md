# 🎮 SALES ARENA - Gamified Performance Dashboard

A modern, gaming-style performance dashboard for sales and marketing teams. Built with Streamlit, featuring a cyberpunk aesthetic with neon colors, glowing effects, and smooth animations.

![Dashboard Preview](preview.png)

## ✨ Features

### 📅 Weekly Performance Tab
- **Sub-tabs for each week** (Week 1, Week 2, Week 3, Week 4)
- **Interactive Leaderboard** with animated rankings
- **Score percentage** with visual progress bars
- **Hot Clients vs Target** comparison
- **Weekly Champion** announcement with celebrations

### 🏅 Total Standings Tab
- **Overall leaderboard** based on total points
- **Win tracking** (number of 1st place finishes)
- **Eligibility system** (must have at least one win)
- **Tournament statistics**
- **Visual comparison charts**

### 💬 Anonymous Chat (Team Pulse)
- **Quick feeling buttons** (Frustrated, Celebrating, Ideas, Need Support)
- **Anonymous messaging** - no names shown
- **Reply system** for team support
- **Timestamp tracking**
- **Stored in Google Sheets** for persistence

### 🎮 Games & Challenges Tab
- **Weekly Challenge** - dynamic challenge text that rotates
- **Reward Spinner** - spin for random prizes
- **Tie-Breaker Battle** - for resolving point ties
- **Quick Math Challenge** - mini-game for fun

## 🎯 Points System

| Rank | Points |
|------|--------|
| 🥇 1st Place | 3 points |
| 🥈 2nd Place | 2 points |
| 🥉 3rd Place | 2 points |
| 4th Place | 1 point |

### Winning Rules
- Winner is determined by **total points**
- Must have **at least one weekly win** (1st place) to be eligible

## 📊 Data Structure

### Google Sheets Setup

Your spreadsheet should have these sheets:

#### 1. Target Sheet
| Column | Description |
|--------|-------------|
| Companies | Company name |
| Target Hot Clients | Weekly target for hot clients |
| Target Leads | Weekly target for leads |
| Budget | Budget allocation |
| Manager | Manager name |
| Date | Date (YYYY-MM-DD format) |

#### 2. Clients Sheet
| Column | Description |
|--------|-------------|
| Name Clients | Manager name (must match Target Sheet) |
| Hot | Number of hot clients achieved |
| Cold | Number of cold clients |
| Date | Date (YYYY-MM-DD format) |

#### 3. Leads Sheet
| Column | Description |
|--------|-------------|
| Company Leads | Company name |
| Number of Leads | Lead count |
| Date Leads | Date |

#### 4. Chat Sheet (auto-created)
| Column | Description |
|--------|-------------|
| message | Anonymous message |
| reply | Replies (separated by ---) |
| timestamp | Message timestamp |

## 🗓️ Week Calculation

- Weeks run **Friday to Thursday**
- Automatic week grouping based on dates
- Auto-detect current week for filtering

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd gamified_dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **Google Sheets API** and **Google Drive API**
4. Create a **Service Account**:
   - Go to APIs & Services > Credentials
   - Create credentials > Service Account
   - Download the JSON key file
5. Share your Google Sheet with the service account email (Editor access)

### 4. Configure Secrets

#### For Local Development:

Create `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

#### For Streamlit Cloud:

Add secrets in your app's Settings > Secrets

### 5. Run the App

```bash
streamlit run app.py
```

## 🎨 UI Design

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Neon Green | `#00ff88` | Primary accent, success |
| Neon Blue | `#00d4ff` | Secondary accent |
| Neon Purple | `#b366ff` | Points, highlights |
| Neon Pink | `#ff66b2` | Special elements |
| Dark BG | `#0a0a0f` | Background |
| Card BG | `#12121a` | Card backgrounds |

### Fonts

- **Orbitron** - Headers, scores (futuristic)
- **Rajdhani** - Body text (modern)
- **Press Start 2P** - Retro gaming elements

## 📁 Project Structure

```
gamified_dashboard/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .streamlit/
    └── secrets.toml      # Google Sheets credentials (create this)
```

## 🔧 Configuration

### Customizing the Spreadsheet URL

In `app.py`, update this line:

```python
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
```

### Customizing Points System

```python
POINTS_SYSTEM = {1: 3, 2: 2, 3: 2, 4: 1}
```

### Customizing Weekly Challenges

```python
challenges = [
    "🔥 Get 3 new hot clients this week!",
    "📞 Make 50 cold calls today!",
    # Add more challenges...
]
```

## 🐛 Troubleshooting

### "Connection Error" Message

1. Check that Google Sheets API is enabled
2. Verify service account email has access to the spreadsheet
3. Ensure credentials are correctly formatted in secrets.toml

### "No data available" Message

1. Check that sheet names match exactly ("Target Sheet", "Clients Sheet")
2. Verify column names match the expected format
3. Ensure dates are in a recognizable format

### Demo Mode

If credentials aren't configured, the app will automatically use demo data for preview purposes.

## 📝 License

MIT License - feel free to use and modify for your team!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

Built with ❤️ for high-performing sales teams
