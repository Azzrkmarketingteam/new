"""
🎮 GAMIFIED SALES PERFORMANCE DASHBOARD
A modern gaming-style dashboard for tracking sales team performance
Built with Streamlit, Google Sheets, and a cyberpunk aesthetic

LOCAL VERSION - Uses credentials.json file directly
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import random
import time
import json
import os

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1sUbTvewtx-bOi3kY_b1t7oNQu-n1wzF6QBLb1BJMg6Y/edit"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Points system: Rank → Points (ranks beyond 5 receive 0)
POINTS_SYSTEM = {1: 3, 2: 2, 3: 1, 4: 0.5, 5: 0.5}

# Weekly date ranges per spec
WEEK_RANGES = {
    1: (datetime(2026, 4, 1),  datetime(2026, 4, 9)),
    2: (datetime(2026, 4, 10), datetime(2026, 4, 16)),
    3: (datetime(2026, 4, 17), datetime(2026, 4, 23)),
    4: (datetime(2026, 4, 24), datetime(2026, 4, 30)),
}

# Neon color palette
COLORS = {
    'neon_green': '#00ff88',
    'neon_blue': '#00d4ff',
    'neon_purple': '#b366ff',
    'neon_pink': '#ff66b2',
    'neon_orange': '#ff9933',
    'dark_bg': '#0a0a0f',
    'card_bg': '#12121a',
    'text': '#ffffff',
    'text_muted': '#8888aa'
}

# ============================================================================
# PAGE CONFIG & CUSTOM CSS
# ============================================================================

st.set_page_config(
    page_title="🎮 Marketing Arena",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    """Inject custom CSS fo
    r gaming-style UI"""
    st.markdown(f"""
    <style>
        /* Import gaming fonts */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Press+Start+2P&display=swap');
        
        /* Root variables */
        :root {{
            --neon-green: {COLORS['neon_green']};
            --neon-blue: {COLORS['neon_blue']};
            --neon-purple: {COLORS['neon_purple']};
            --neon-pink: {COLORS['neon_pink']};
            --neon-orange: {COLORS['neon_orange']};
            --dark-bg: {COLORS['dark_bg']};
            --card-bg: {COLORS['card_bg']};
        }}
        
        /* Main app styling */
        .stApp {{
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0a0a0f 100%);
            background-attachment: fixed;
        }}
        
        /* Add animated grid background */
        .stApp::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(0, 255, 136, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 136, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: 0;
        }}
        
        /* Headers */
        h1, h2, h3 {{
            font-family: 'Orbitron', sans-serif !important;
            color: var(--neon-green) !important;
            text-shadow: 0 0 10px var(--neon-green), 0 0 20px var(--neon-green), 0 0 40px var(--neon-green);
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: rgba(18, 18, 26, 0.8);
            padding: 10px;
            border-radius: 15px;
            border: 1px solid rgba(0, 255, 136, 0.2);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            font-family: 'Orbitron', sans-serif;
            font-weight: 600;
            color: #8888aa;
            background: transparent;
            border-radius: 10px;
            padding: 10px 20px;
            transition: all 0.3s ease;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            color: var(--neon-blue);
            background: rgba(0, 212, 255, 0.1);
        }}
        
        .stTabs [aria-selected="true"] {{
            color: var(--neon-green) !important;
            background: rgba(0, 255, 136, 0.15) !important;
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
        }}
        
        /* Card styling */
        .game-card {{
            background: linear-gradient(145deg, rgba(18, 18, 26, 0.95), rgba(26, 26, 46, 0.95));
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 20px;
            padding: 25px;
            margin: 10px 0;
            box-shadow: 
                0 0 20px rgba(0, 255, 136, 0.1),
                inset 0 0 60px rgba(0, 255, 136, 0.02);
            transition: all 0.3s ease;
        }}
        
        .game-card:hover {{
            border-color: rgba(0, 255, 136, 0.6);
            box-shadow: 
                0 0 30px rgba(0, 255, 136, 0.2),
                inset 0 0 80px rgba(0, 255, 136, 0.05);
            transform: translateY(-2px);
        }}
        
        /* Leaderboard styling */
        .leaderboard-item {{
            background: linear-gradient(90deg, rgba(18, 18, 26, 0.9), rgba(26, 26, 46, 0.9));
            border-left: 4px solid var(--neon-green);
            border-radius: 10px;
            padding: 15px 20px;
            margin: 8px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.3s ease;
        }}
        
        .leaderboard-item.rank-1 {{
            border-left-color: #ffd700;
            background: linear-gradient(90deg, rgba(255, 215, 0, 0.15), rgba(18, 18, 26, 0.9));
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
        }}
        
        .leaderboard-item.rank-2 {{
            border-left-color: #c0c0c0;
            background: linear-gradient(90deg, rgba(192, 192, 192, 0.1), rgba(18, 18, 26, 0.9));
        }}
        
        .leaderboard-item.rank-3 {{
            border-left-color: #cd7f32;
            background: linear-gradient(90deg, rgba(205, 127, 50, 0.1), rgba(18, 18, 26, 0.9));
        }}
        
        /* Rank badge */
        .rank-badge {{
            font-family: 'Press Start 2P', cursive;
            font-size: 14px;
            padding: 8px 15px;
            border-radius: 8px;
            margin-right: 15px;
        }}
        
        .rank-1 .rank-badge {{
            background: linear-gradient(135deg, #ffd700, #ffaa00);
            color: #000;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        }}
        
        .rank-2 .rank-badge {{
            background: linear-gradient(135deg, #c0c0c0, #a0a0a0);
            color: #000;
        }}
        
        .rank-3 .rank-badge {{
            background: linear-gradient(135deg, #cd7f32, #a05a20);
            color: #fff;
        }}
        
        /* Manager name */
        .manager-name {{
            font-family: 'Rajdhani', sans-serif;
            font-size: 20px;
            font-weight: 600;
            color: #fff;
            flex-grow: 1;
        }}
        
        /* Score display */
        .score-display {{
            font-family: 'Orbitron', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: var(--neon-green);
            text-shadow: 0 0 10px var(--neon-green);
        }}
        
        /* Progress bar */
        .progress-container {{
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 5px 0;
            border: 1px solid rgba(0, 255, 136, 0.2);
        }}
        
        .progress-bar {{
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, var(--neon-green), var(--neon-blue));
            box-shadow: 0 0 10px var(--neon-green);
            transition: width 1s ease-out;
        }}
        
        /* Stats box */
        .stat-box {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(145deg, rgba(18, 18, 26, 0.9), rgba(26, 26, 46, 0.9));
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 15px;
            margin: 5px;
        }}
        
        .stat-value {{
            font-family: 'Orbitron', sans-serif;
            font-size: 36px;
            font-weight: 800;
            color: var(--neon-blue);
            text-shadow: 0 0 15px var(--neon-blue);
        }}
        
        .stat-label {{
            font-family: 'Rajdhani', sans-serif;
            font-size: 14px;
            color: #8888aa;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 5px;
        }}
        
        /* Winner announcement */
        .winner-box {{
            text-align: center;
            padding: 40px;
            background: linear-gradient(145deg, rgba(255, 215, 0, 0.1), rgba(18, 18, 26, 0.95));
            border: 2px solid #ffd700;
            border-radius: 25px;
            box-shadow: 
                0 0 50px rgba(255, 215, 0, 0.3),
                inset 0 0 100px rgba(255, 215, 0, 0.05);
            animation: pulse-gold 2s infinite;
        }}
        
        @keyframes pulse-gold {{
            0%, 100% {{ box-shadow: 0 0 50px rgba(255, 215, 0, 0.3), inset 0 0 100px rgba(255, 215, 0, 0.05); }}
            50% {{ box-shadow: 0 0 80px rgba(255, 215, 0, 0.5), inset 0 0 120px rgba(255, 215, 0, 0.1); }}
        }}
        
        .winner-title {{
            font-family: 'Press Start 2P', cursive;
            font-size: 14px;
            color: #ffd700;
            text-shadow: 0 0 10px #ffd700;
            margin-bottom: 15px;
        }}
        
        .winner-name {{
            font-family: 'Orbitron', sans-serif;
            font-size: 42px;
            font-weight: 900;
            color: #fff;
            text-shadow: 0 0 20px #ffd700, 0 0 40px #ffd700;
            animation: glow 1.5s infinite alternate;
        }}
        
        @keyframes glow {{
            from {{ text-shadow: 0 0 20px #ffd700, 0 0 40px #ffd700; }}
            to {{ text-shadow: 0 0 30px #ffd700, 0 0 60px #ffd700, 0 0 80px #ffd700; }}
        }}
        
        /* Chat message */
        .chat-message {{
            background: linear-gradient(145deg, rgba(18, 18, 26, 0.95), rgba(26, 26, 46, 0.95));
            border: 1px solid rgba(179, 102, 255, 0.3);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
        }}
        
        .chat-message .message-text {{
            font-family: 'Rajdhani', sans-serif;
            font-size: 18px;
            color: #fff;
            margin-bottom: 10px;
        }}
        
        .chat-message .message-time {{
            font-size: 12px;
            color: #666;
        }}
        
        .chat-reply {{
            background: rgba(0, 212, 255, 0.1);
            border-left: 3px solid var(--neon-blue);
            padding: 10px 15px;
            margin: 10px 0 10px 20px;
            border-radius: 0 10px 10px 0;
        }}
        
        /* Button styling */
        .stButton > button {{
            font-family: 'Orbitron', sans-serif;
            font-weight: 600;
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 212, 255, 0.2));
            border: 1px solid var(--neon-green);
            color: var(--neon-green);
            border-radius: 10px;
            padding: 10px 25px;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.4), rgba(0, 212, 255, 0.4));
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.4);
            transform: translateY(-2px);
        }}
        
        /* Text input */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background: rgba(18, 18, 26, 0.9) !important;
            border: 1px solid rgba(0, 255, 136, 0.3) !important;
            border-radius: 10px !important;
            color: #fff !important;
            font-family: 'Rajdhani', sans-serif !important;
        }}
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--neon-green) !important;
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.2) !important;
        }}
        
        /* Metrics */
        [data-testid="stMetricValue"] {{
            font-family: 'Orbitron', sans-serif;
            color: var(--neon-green);
        }}
        
        /* Spin wheel */
        .spin-wheel {{
            width: 250px;
            height: 250px;
            border-radius: 50%;
            border: 5px solid var(--neon-purple);
            box-shadow: 0 0 30px var(--neon-purple);
            margin: 20px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            background: conic-gradient(
                var(--neon-green) 0deg 60deg,
                var(--neon-blue) 60deg 120deg,
                var(--neon-purple) 120deg 180deg,
                var(--neon-pink) 180deg 240deg,
                var(--neon-orange) 240deg 300deg,
                var(--neon-green) 300deg 360deg
            );
            transition: transform 3s cubic-bezier(0.17, 0.67, 0.12, 0.99);
        }}
        
        .spin-wheel.spinning {{
            animation: spin 3s cubic-bezier(0.17, 0.67, 0.12, 0.99);
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(1800deg); }}
        }}
        
        /* Challenge card */
        .challenge-card {{
            background: linear-gradient(145deg, rgba(179, 102, 255, 0.15), rgba(18, 18, 26, 0.95));
            border: 2px solid var(--neon-purple);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 0 30px rgba(179, 102, 255, 0.2);
        }}
        
        .challenge-title {{
            font-family: 'Press Start 2P', cursive;
            font-size: 12px;
            color: var(--neon-purple);
            margin-bottom: 15px;
        }}
        
        .challenge-text {{
            font-family: 'Rajdhani', sans-serif;
            font-size: 22px;
            color: #fff;
            line-height: 1.6;
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: rgba(18, 18, 26, 0.9);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(var(--neon-green), var(--neon-blue));
            border-radius: 10px;
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            font-family: 'Orbitron', sans-serif;
            background: rgba(18, 18, 26, 0.9);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# DATA CONNECTION & PROCESSING
# ============================================================================

def connect_to_sheets():
    """
    Connect to Google Sheets.
    Method 1: credentials.json file (local development)
    Method 2: Streamlit secrets  (cloud deployment on Streamlit Community Cloud)
    """
    try:
        # Method 1: Try to load from credentials.json file (LOCAL DEVELOPMENT)
        credentials_file = 'credentials.json'

        if os.path.exists(credentials_file):
            credentials = Credentials.from_service_account_file(
                credentials_file, scopes=SCOPES
            )
            client = gspread.authorize(credentials)
            spreadsheet = client.open_by_url(SPREADSHEET_URL)
            st.success("Connected")
            return spreadsheet

        # Method 2: Try Streamlit secrets (FOR CLOUD DEPLOYMENT)
        elif 'gcp_service_account' in st.secrets:
            creds_dict = dict(st.secrets['gcp_service_account'])

            # FIX: Streamlit TOML secrets sometimes store the private_key
            # with literal '\n' (two characters) instead of actual newlines.
            # Google's JWT library needs real newline characters to parse the
            # PEM key. Without this, you get "Invalid JWT Signature" errors.
            if 'private_key' in creds_dict:
                creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')

            credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            client = gspread.authorize(credentials)
            spreadsheet = client.open_by_url(SPREADSHEET_URL)
            return spreadsheet

        else:
            st.error("""
            ❌ **credentials.json not found!**
            
            **How to fix (Local):**
            1. Put your `credentials.json` file in the same folder as this script
            
            **How to fix (Streamlit Cloud):**
            1. Go to App Settings → Secrets
            2. Add your service account JSON under `[gcp_service_account]`
            
            **Current folder:** """ + os.getcwd())
            return None

    except Exception as e:
        st.error(f"⚠️ Connection Error: {str(e)}")
        return None

@st.cache_data(ttl=60)
def get_data(_spreadsheet):
    """
    Fetch data from all 4 sheets with caching.
    Sheet names: Target, Leads, Clients, Meetings
    """
    try:
        def load_sheet(name):
            ws = _spreadsheet.worksheet(name)
            records = ws.get_all_records()
            df = pd.DataFrame(records)
            df.columns = df.columns.str.strip()
            return df

        target_df   = load_sheet("Target")    # Companies, Target Hot, Clients, Target Leads, Budget, Manager, Date
        leads_df    = load_sheet("Leads")     # Company, Number of leads, Date Leads
        clients_df  = load_sheet("Clients")   # Company, Hot, Cold, Date
        meetings_df = load_sheet("Meeting")  # Name Meeting, Leads Meeting, Meeting, Date Meeting

        return target_df, leads_df, clients_df, meetings_df

    except Exception as e:
        st.error(f"⚠️ Data Fetch Error: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def get_chat_data(_spreadsheet):
    """Fetch chat messages from Chat sheet"""
    try:
        chat_sheet = _spreadsheet.worksheet("Chat")
        chat_data = chat_sheet.get_all_records()
        return pd.DataFrame(chat_data)
    except:
        # Create Chat sheet if it doesn't exist
        try:
            chat_sheet = _spreadsheet.add_worksheet(title="Chat", rows=100, cols=3)
            chat_sheet.update('A1:C1', [['message', 'reply', 'timestamp']])
            return pd.DataFrame(columns=['message', 'reply', 'timestamp'])
        except:
            return pd.DataFrame(columns=['message', 'reply', 'timestamp'])

def add_chat_message(_spreadsheet, message):
    """Add a new anonymous message to the Chat sheet"""
    try:
        chat_sheet = _spreadsheet.worksheet("Chat")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_sheet.append_row([message, '', timestamp])
        return True
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return False

def add_chat_reply(_spreadsheet, row_index, reply):
    """Add a reply to an existing message"""
    try:
        chat_sheet = _spreadsheet.worksheet("Chat")
        current_reply = chat_sheet.cell(row_index + 2, 2).value
        if current_reply:
            new_reply = f"{current_reply}\n---\n{reply}"
        else:
            new_reply = reply
        chat_sheet.update_cell(row_index + 2, 2, new_reply)
        return True
    except Exception as e:
        st.error(f"Error sending reply: {str(e)}")
        return False

def parse_date(date_str):
    """Parse date string to datetime object"""
    if pd.isna(date_str) or str(date_str).strip() == '':
        return None
    date_str = str(date_str).strip()

    # FIX: Moved %m/%d/%Y BEFORE %d/%m/%Y so that ambiguous dates like
    # "4/6/2026" parse as April 6 (US format) instead of June 4.
    # Previously, "4/6/2026" matched %d/%m/%Y first → June 4 → outside all
    # WEEK_RANGES → Week 1 data got assign_week = None and was silently dropped.
    # Dates like "4/13/2026" were unaffected because month=13 is invalid,
    # so %d/%m/%Y failed and %m/%d/%Y was used as fallback.
    # Also added common Google Sheets export formats as extra fallback.
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',            # US format — must come before %d/%m/%Y
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%m/%d/%Y %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%m-%d-%Y',
        '%m/%d/%y',            # 2-digit year variant
        '%d/%m/%y',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue

    # Fallback: let pandas infer the format (handles many edge cases from
    # Google Sheets such as "April 6, 2026" or "2026-04-06T00:00:00")
    try:
        result = pd.to_datetime(date_str, dayfirst=False)
        return result.to_pydatetime()
    except Exception:
        pass

    return None

def assign_week(date):
    """Assign week number (1-4) based on fixed date ranges from spec."""
    if date is None:
        return None
    for week_num, (start, end) in WEEK_RANGES.items():
        if start <= date <= end:
            return week_num
    return None

def process_data(target_df, leads_df, clients_df, meetings_df):
    """
    Add week numbers to all dataframes using date columns.
    Column mapping per spec:
      Target:   Date
      Leads:    Date Leads
      Clients:  Date
      Meetings: Date Meeting
    """
    def add_week(df, date_col):
        if date_col in df.columns:
            df = df.copy()
            df['parsed_date'] = df[date_col].apply(parse_date)
            df['week'] = df['parsed_date'].apply(assign_week)
        return df

    target_df   = add_week(target_df,   'Date')
    leads_df    = add_week(leads_df,    'Date Leads')
    clients_df  = add_week(clients_df,  'Date')
    meetings_df = add_week(meetings_df, 'Date Meeting')

    # FIX: Normalize the company column name in Target sheet.
    # Target uses 'Companies' (plural) while Clients/Leads/Meetings use 'Company'.
    # Rename to 'Company' so calculate_weekly_scores can use a single column name.
    if 'Companies' in target_df.columns and 'Company' not in target_df.columns:
        target_df = target_df.rename(columns={'Companies': 'Company'})

    return target_df, leads_df, clients_df, meetings_df

def calculate_weekly_scores(target_df, leads_df, clients_df, meetings_df):
    """
    Calculate weekly KPIs per manager.
    
    Target sheet:   Companies → Manager mapping, Target Hot, Target Leads
    Clients sheet:  Company → Hot, Cold  (join via Companies from Target)
    Leads sheet:    Company → Number of leads
    Meetings sheet: Leads Meeting → meetings count
    """
    results = []
    weeks = sorted(target_df['week'].dropna().unique()) if 'week' in target_df.columns else [1, 2, 3, 4]

    for week in weeks:
        wt = target_df[target_df['week'] == week] if 'week' in target_df.columns else target_df
        wc = clients_df[clients_df['week'] == week] if 'week' in clients_df.columns else clients_df
        wl = leads_df[leads_df['week'] == week]     if 'week' in leads_df.columns else leads_df
        wm = meetings_df[meetings_df['week'] == week] if 'week' in meetings_df.columns else meetings_df

        managers = wt['Manager'].dropna().unique() if 'Manager' in wt.columns else []

        for manager in managers:
            if str(manager).strip() == '':
                continue

            # --- Target rows for this manager ---
            mt = wt[wt['Manager'] == manager]
            # FIX: 'Companies' is now normalized to 'Company' in process_data(),
            # so all sheets use the same column name for company lookups.
            # Fallback handles both names in case process_data was bypassed.
            if 'Company' in mt.columns:
                companies = mt['Company'].dropna().unique()
            elif 'Companies' in mt.columns:
                companies = mt['Companies'].dropna().unique()
            else:
                companies = []

            # Target Hot (sum across all companies of this manager)
            target_hot = pd.to_numeric(mt['Target Hot'], errors='coerce').sum() if 'Target Hot' in mt.columns else 0

            # --- Clients: match on Company column ---
            if len(companies) and 'Company' in wc.columns:
                mc = wc[wc['Company'].isin(companies)]
            else:
                mc = pd.DataFrame()

            actual_hot  = pd.to_numeric(mc['Hot'],  errors='coerce').sum() if not mc.empty and 'Hot'  in mc.columns else 0
            actual_cold = pd.to_numeric(mc['Cold'], errors='coerce').sum() if not mc.empty and 'Cold' in mc.columns else 0
            total_clients = actual_hot + actual_cold

            # --- Leads: match on Company column ---
            if len(companies) and 'Company' in wl.columns:
                ml = wl[wl['Company'].isin(companies)]
                total_leads = pd.to_numeric(ml['Number of leads'], errors='coerce').sum()
            else:
                total_leads = 0

            # --- Meetings: match on Leads Meeting (company name) ---
            if len(companies) and 'Leads Meeting' in wm.columns:
                mm = wm[wm['Leads Meeting'].isin(companies)]
                total_meetings = pd.to_numeric(mm['Meeting'], errors='coerce').sum()
            else:
                total_meetings = 0

            # --- Achievement % ---
            score = (actual_hot / target_hot * 100) if target_hot > 0 else 0

            results.append({
                'week':           int(week),
                'manager':        manager,
                'target_hot':     int(target_hot)    if not pd.isna(target_hot)    else 0,
                'actual_hot':     int(actual_hot)    if not pd.isna(actual_hot)    else 0,
                'actual_cold':    int(actual_cold)   if not pd.isna(actual_cold)   else 0,
                'total_clients':  int(total_clients) if not pd.isna(total_clients) else 0,
                'total_leads':    int(total_leads)   if not pd.isna(total_leads)   else 0,
                'total_meetings': int(total_meetings) if not pd.isna(total_meetings) else 0,
                'score':          round(score, 1),
            })

    return pd.DataFrame(results)

def calculate_rankings(scores_df):
    """
    Rank managers within each week and assign points.
    Rule: a manager receives 0 points if actual_hot == 0 for that week,
    regardless of their achievement score or rank position.
    """
    if scores_df.empty:
        return scores_df

    rankings = []

    for week in scores_df['week'].unique():
        week_data = scores_df[scores_df['week'] == week].copy()
        week_data = week_data.sort_values('score', ascending=False).reset_index(drop=True)
        week_data['rank'] = range(1, len(week_data) + 1)
        # Assign points based on rank, then zero out if no hot clients
        week_data['points'] = week_data['rank'].apply(lambda x: POINTS_SYSTEM.get(x, 0))
        week_data.loc[week_data['actual_hot'] == 0, 'points'] = 0
        rankings.append(week_data)

    return pd.concat(rankings, ignore_index=True) if rankings else pd.DataFrame()

def calculate_total_standings(rankings_df):
    """Calculate overall standings based on total points"""
    if rankings_df.empty:
        return pd.DataFrame()

    agg_cols = {
        'points':         'sum',
        'score':          'mean',
        'actual_hot':     'sum',
        'target_hot':     'sum',
        'actual_cold':    'sum',
        'total_clients':  'sum',
        'total_leads':    'sum',
        'total_meetings': 'sum',
    }
    # Only aggregate columns that exist
    agg_cols = {k: v for k, v in agg_cols.items() if k in rankings_df.columns}

    total = rankings_df.groupby('manager').agg(agg_cols).reset_index()

    wins = rankings_df[rankings_df['rank'] == 1].groupby('manager').size().reset_index(name='wins')
    total = total.merge(wins, on='manager', how='left')
    total['wins'] = total['wins'].fillna(0).astype(int)
    total['eligible'] = total['wins'] >= 1

    total = total.sort_values(['points', 'wins', 'score'], ascending=[False, False, False]).reset_index(drop=True)
    total['rank'] = range(1, len(total) + 1)

    return total

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Render the main header with logo and title"""
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 48px; margin: 0;">🎮 Marketing ARENA</h1>
            <p style="font-family: 'Rajdhani', sans-serif; color: #8888aa; font-size: 18px; letter-spacing: 3px;">
                PERFORMANCE BATTLEGROUND
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_leaderboard_item(rank, manager, score, hot, target, points=None):
    """Render a single leaderboard item"""
    rank_class = f"rank-{rank}" if rank <= 3 else ""
    rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
    
    progress = min(100, score)
    bar_color = COLORS['neon_green'] if score >= 100 else COLORS['neon_blue'] if score >= 75 else COLORS['neon_purple']
    
    points_html = f"""
        <div style="
            font-family: 'Press Start 2P', cursive;
            font-size: 10px;
            color: {COLORS['neon_purple']};
            margin-left: 15px;
        ">+{points} PTS</div>
    """ if points else ""
    
    st.markdown(f"""
        <div class="leaderboard-item {rank_class}">
            <div style="display: flex; align-items: center;">
                <div class="rank-badge">{rank_emoji}</div>
                <div>
                    <div class="manager-name">{manager}</div>
                    <div style="font-family: 'Rajdhani', sans-serif; color: #666; font-size: 14px;">
                        🔥 {hot} / {target} Hot Clients
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center;">
                <div class="score-display">{score:.1f}%</div>
                {points_html}
            </div>
        </div>
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%; background: linear-gradient(90deg, {bar_color}, {COLORS['neon_blue']});"></div>
        </div>
    """, unsafe_allow_html=True)

def render_winner_announcement(winner_name, title="🏆 WEEKLY CHAMPION"):
    """Render winner announcement with animations"""
    st.balloons()
    st.markdown(f"""
        <div class="winner-box">
            <div class="winner-title">{title}</div>
            <div class="winner-name">{winner_name}</div>
            <div style="margin-top: 20px; font-size: 40px;">👑</div>
        </div>
    """, unsafe_allow_html=True)

def render_stat_box(value, label, color=COLORS['neon_blue']):
    """Render a statistics box"""
    st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value" style="color: {color}; text-shadow: 0 0 15px {color};">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

def render_challenge_card(challenge_text):
    """Render the weekly challenge card"""
    st.markdown(f"""
        <div class="challenge-card">
            <div class="challenge-title">⚡ WEEKLY CHALLENGE ⚡</div>
            <div class="challenge-text">{challenge_text}</div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TAB CONTENT
# ============================================================================

def render_weekly_tab(rankings_df):
    """Render the Weekly Performance tab"""
    st.markdown("## 📅 Weekly Performance")

    if rankings_df.empty:
        st.info("📊 No weekly data available yet. Data will appear once performance records are added.")
        return

    weeks = sorted(rankings_df['week'].unique())
    week_tabs = st.tabs([f"🗓️ Week {w}" for w in weeks])

    for idx, week in enumerate(weeks):
        with week_tabs[idx]:
            week_data = rankings_df[rankings_df['week'] == week].sort_values('rank')

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("### 🏆 Leaderboard")
                for _, row in week_data.iterrows():
                    render_leaderboard_item(
                        rank=int(row['rank']),
                        manager=row['manager'],
                        score=row['score'],
                        hot=int(row['actual_hot']),
                        target=int(row['target_hot']),
                        points=int(row['points'])
                    )

                # Full KPI comparison table
                st.markdown("### 📋 Full KPI Comparison")
                kpi_cols = ['manager', 'actual_hot', 'actual_cold', 'total_clients',
                            'total_leads', 'total_meetings', 'target_hot', 'score']
                available = [c for c in kpi_cols if c in week_data.columns]
                display_df = week_data[available].copy()
                display_df.columns = [c.replace('_', ' ').title() for c in available]
                display_df = display_df.rename(columns={
                    'Score': 'Achievement %',
                    'Actual Hot': 'Hot Clients',
                    'Actual Cold': 'Cold Clients',
                    'Total Clients': 'Total Clients',
                    'Total Leads': 'Leads',
                    'Total Meetings': 'Meetings',
                    'Target Hot': 'Target Hot',
                    'Manager': 'Manager',
                })
                if 'Achievement %' in display_df.columns:
                    display_df['Achievement %'] = display_df['Achievement %'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_df, use_container_width=True, hide_index=True)

            with col2:
                winner = week_data[week_data['rank'] == 1]
                if not winner.empty:
                    winner_name  = winner.iloc[0]['manager']
                    winner_score = winner.iloc[0]['score']
                    st.markdown("### 👑 Week Champion")
                    st.markdown(f"""
                        <div class="winner-box" style="padding: 25px;">
                            <div class="winner-title">🏆 CHAMPION</div>
                            <div class="winner-name" style="font-size: 28px;">{winner_name}</div>
                            <div style="font-family: 'Orbitron', sans-serif; font-size: 24px;
                                        color: {COLORS['neon_green']}; margin-top: 15px;">
                                {winner_score:.1f}%
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("### 📊 Week Stats")
                col_a, col_b = st.columns(2)
                with col_a:
                    render_stat_box(f"{week_data['score'].mean():.1f}%", "AVG SCORE", COLORS['neon_blue'])
                with col_b:
                    render_stat_box(int(week_data['actual_hot'].sum()), "TOTAL HOT", COLORS['neon_green'])

                # Extra KPI stats
                if 'total_leads' in week_data.columns:
                    col_c, col_d = st.columns(2)
                    with col_c:
                        render_stat_box(int(week_data['total_leads'].sum()), "TOTAL LEADS", COLORS['neon_purple'])
                    with col_d:
                        render_stat_box(int(week_data['total_meetings'].sum()), "MEETINGS", COLORS['neon_pink'])

def render_total_tab(total_standings):
    """Render the Total Standings tab"""
    st.markdown("## 🏅 Total Standings")
    
    if total_standings.empty:
        st.info("📊 No standings data available yet.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 Overall Leaderboard")
        
        for _, row in total_standings.iterrows():
            eligible_badge = "✅" if row['eligible'] else "❌"
            
            st.markdown(f"""
                <div class="leaderboard-item {'rank-' + str(int(row['rank'])) if row['rank'] <= 3 else ''}">
                    <div style="display: flex; align-items: center;">
                        <div class="rank-badge">#{int(row['rank'])}</div>
                        <div>
                            <div class="manager-name">
                                {row['manager']} {eligible_badge}
                            </div>
                            <div style="font-family: 'Rajdhani', sans-serif; color: #666; font-size: 14px;">
                                🏆 {int(row['wins'])} Wins | 📊 Avg: {row['score']:.1f}%
                            </div>
                        </div>
                    </div>
                    <div style="
                        font-family: 'Press Start 2P', cursive;
                        font-size: 16px;
                        color: {COLORS['neon_purple']};
                    ">{int(row['points'])} PTS</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Overall winner
        eligible_winners = total_standings[total_standings['eligible'] == True]
        if not eligible_winners.empty:
            final_winner = eligible_winners.iloc[0]
            
            st.markdown("### 👑 Current Leader")
            st.markdown(f"""
                <div class="winner-box">
                    <div class="winner-title">🎮 LEADING THE GAME</div>
                    <div class="winner-name" style="font-size: 32px;">{final_winner['manager']}</div>
                    <div style="
                        font-family: 'Press Start 2P', cursive;
                        font-size: 20px;
                        color: {COLORS['neon_purple']};
                        margin-top: 15px;
                    ">{int(final_winner['points'])} POINTS</div>
                    <div style="margin-top: 10px; color: #ffd700;">
                        🏆 {int(final_winner['wins'])} Wins
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Quick stats
        st.markdown("### 📈 Tournament Stats")
        col_a, col_b = st.columns(2)
        with col_a:
            render_stat_box(len(total_standings), "PLAYERS", COLORS['neon_blue'])
        with col_b:
            total_points = int(total_standings['points'].sum())
            render_stat_box(total_points, "TOTAL PTS", COLORS['neon_purple'])
    
    # Eligibility note
    st.markdown("""
        <div class="game-card" style="margin-top: 20px;">
            <div style="font-family: 'Orbitron', sans-serif; color: #ffd700; margin-bottom: 10px;">
                📋 WINNING RULES
            </div>
            <div style="font-family: 'Rajdhani', sans-serif; color: #fff;">
                ✅ = Eligible to win (has at least 1 weekly victory)<br>
                ❌ = Not eligible (needs at least 1 weekly win to qualify)
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Full KPI statistics table ────────────────────────────────────────────
    st.markdown("### 📊 Full Statistics Table")

    # Build the display dataframe from total_standings
    stat_cols_map = {
        'rank':           'Rank',
        'manager':        'Manager',
        'points':         'Total Points',
        'score':          'Avg Score (%)',
        'target_hot':     'Target Hot',
        'actual_hot':     'Actual Hot',
        'actual_cold':    'Actual Cold',
        'total_clients':  'Total Clients',
        'total_leads':    'Total Leads',
        'total_meetings': 'Total Meetings',
        'wins':           'Wins',
    }
    # Keep only columns that actually exist in the dataframe
    available_cols = [c for c in stat_cols_map if c in total_standings.columns]
    stats_df = total_standings[available_cols].copy()
    stats_df = stats_df.rename(columns=stat_cols_map)

    # Format numeric columns
    if 'Avg Score (%)' in stats_df.columns:
        stats_df['Avg Score (%)'] = stats_df['Avg Score (%)'].apply(lambda x: f"{x:.1f}%")
    if 'Total Points' in stats_df.columns:
        stats_df['Total Points'] = stats_df['Total Points'].apply(
            lambda x: f"{x:.1f}" if isinstance(x, float) else str(x)
        )

    # Style the dataframe
    st.dataframe(
        stats_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Rank':           st.column_config.NumberColumn('Rank', format='%d'),
            'Manager':        st.column_config.TextColumn('Manager'),
            'Total Points':   st.column_config.TextColumn('Total Points'),
            'Avg Score (%)':  st.column_config.TextColumn('Avg Score (%)'),
            'Target Hot':     st.column_config.NumberColumn('Target Hot'),
            'Actual Hot':     st.column_config.NumberColumn('Actual Hot'),
            'Actual Cold':    st.column_config.NumberColumn('Actual Cold'),
            'Total Clients':  st.column_config.NumberColumn('Total Clients'),
            'Total Leads':    st.column_config.NumberColumn('Total Leads'),
            'Total Meetings': st.column_config.NumberColumn('Total Meetings'),
            'Wins':           st.column_config.NumberColumn('Wins'),
        }
    )

def render_chat_tab(spreadsheet):
    """Render the Anonymous Chat tab"""
    st.markdown("## 💬 Team Pulse")
    st.markdown("""
        <p style="font-family: 'Rajdhani', sans-serif; color: #8888aa;">
            Share your thoughts anonymously. Support your teammates! 🤝
        </p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Share Your Thoughts")
        
        # Quick feeling buttons
        feeling_col1, feeling_col2 = st.columns(2)
        with feeling_col1:
            if st.button("😤 I'm feeling frustrated", use_container_width=True):
                st.session_state.show_message_input = True
                st.session_state.message_prefix = "😤 Feeling frustrated: "
        with feeling_col2:
            if st.button("🎉 Celebrating a win!", use_container_width=True):
                st.session_state.show_message_input = True
                st.session_state.message_prefix = "🎉 Celebration: "
        
        feeling_col3, feeling_col4 = st.columns(2)
        with feeling_col3:
            if st.button("💡 I have an idea", use_container_width=True):
                st.session_state.show_message_input = True
                st.session_state.message_prefix = "💡 Idea: "
        with feeling_col4:
            if st.button("🙏 Need support", use_container_width=True):
                st.session_state.show_message_input = True
                st.session_state.message_prefix = "🙏 Need support: "
        
        # Message input
        st.markdown("<br>", unsafe_allow_html=True)
        message = st.text_area(
            "Your anonymous message:",
            placeholder="Type your message here... Remember, this is anonymous! 🎭",
            key="chat_message_input"
        )
        
        if st.button("🚀 Send Anonymous Message", use_container_width=True):
            if message.strip():
                prefix = st.session_state.get('message_prefix', '')
                full_message = prefix + message if prefix else message
                if spreadsheet and add_chat_message(spreadsheet, full_message):
                    st.success("✅ Message sent anonymously!")
                    st.session_state.message_prefix = ''
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("Please enter a message")
    
    with col2:
        st.markdown("### 📨 Team Messages")
        
        if spreadsheet:
            chat_df = get_chat_data(spreadsheet)
            
            if not chat_df.empty:
                # Sort by timestamp descending
                if 'timestamp' in chat_df.columns:
                    chat_df = chat_df.sort_values('timestamp', ascending=False)
                
                for idx, row in chat_df.iterrows():
                    message_text = row.get('message', '')
                    reply_text = row.get('reply', '')
                    timestamp = row.get('timestamp', '')
                    
                    if not message_text:
                        continue
                    
                    st.markdown(f"""
                        <div class="chat-message">
                            <div class="message-text">{message_text}</div>
                            <div class="message-time">🕐 {timestamp}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Show existing replies
                    # Show existing replies
                    if isinstance(reply_text, str):
                       replies = reply_text.split('\n---\n')
                    elif reply_text is not None:
                        replies = [str(reply_text)]
                    else:
                       replies = []

                    for reply in replies:
                        if reply.strip():
                            st.markdown(f"""
                                <div class="chat-reply">
                                    <div style="color: #00d4ff;">↩️ {reply}</div>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    # Reply button
                    with st.expander("💬 Reply to this"):
                        reply_key = f"reply_{idx}"
                        reply_msg = st.text_input("Your reply:", key=reply_key)
                        if st.button("Send Reply", key=f"send_{idx}"):
                            if reply_msg.strip():
                                if add_chat_reply(spreadsheet, idx, reply_msg):
                                    st.success("Reply sent!")
                                    time.sleep(0.5)
                                    st.rerun()
            else:
                st.info("No messages yet. Be the first to share! 🎭")

def get_games_challenges(_spreadsheet):
    """
    Load challenges from the 'Games_Challenges' sheet.
    Columns: challenge_title, challenge_description
    Returns a list of dicts (up to 6). Falls back to built-in defaults if
    the sheet is missing or empty, and auto-creates the sheet with defaults.
    """
    defaults = [
        {"challenge_title": "🔥 Hot Client Blitz",      "challenge_description": "Get 3 new hot clients this week and dominate the leaderboard!"},
        {"challenge_title": "📞 Call Marathon",          "challenge_description": "Make 50 cold calls today — volume creates opportunity!"},
        {"challenge_title": "🎯 Target Crusher",         "challenge_description": "Exceed your hot client target by 20% this week!"},
        {"challenge_title": "🤝 Teammate Boost",         "challenge_description": "Help a teammate close a deal — teamwork wins the season!"},
        {"challenge_title": "📈 Cold-to-Hot Converter",  "challenge_description": "Convert at least 2 cold leads into hot clients this week!"},
        {"challenge_title": "⚡ Speed Champion",         "challenge_description": "First manager to reach 100% of their target wins a bonus!"},
    ]
    if _spreadsheet is None:
        return defaults
    try:
        ws = _spreadsheet.worksheet("Games_Challenges")
        records = ws.get_all_records()
        df = pd.DataFrame(records)
        df.columns = df.columns.str.strip()
        if 'challenge_title' not in df.columns or 'challenge_description' not in df.columns:
            return defaults
        df = df[df['challenge_title'].astype(str).str.strip() != '']
        result = df[['challenge_title', 'challenge_description']].head(6).to_dict('records')
        return result if result else defaults
    except Exception:
        # Sheet missing — auto-create it with defaults seeded in
        try:
            ws = _spreadsheet.add_worksheet(title="Games_Challenges", rows=20, cols=2)
            ws.update('A1:B1', [['challenge_title', 'challenge_description']])
            ws.append_rows([[d['challenge_title'], d['challenge_description']] for d in defaults])
        except Exception:
            pass
        return defaults


def render_games_tab(rankings_df, total_standings, spreadsheet=None):
    """
    Games & Challenges tab.
    Shows only Active Challenges in a responsive grid (up to 6 cards).
    Content is loaded dynamically from the Games_Challenges Google Sheet.
    """
    st.markdown("## 🎮 Games & Challenges")
    st.markdown("""
        <p style="font-family: 'Rajdhani', sans-serif; color: #8888aa; margin-bottom: 24px;">
            Complete challenges to earn recognition and boost your team's performance! 🏆
        </p>
    """, unsafe_allow_html=True)

    challenges = get_games_challenges(spreadsheet)

    if not challenges:
        st.info("No challenges found. Add rows to the 'Games_Challenges' Google Sheet (columns: challenge_title, challenge_description).")
        return

    # Render in a 3-column grid, 2 rows max (up to 6 cards)
    rows = [challenges[i:i+3] for i in range(0, len(challenges), 3)]

    for row_challenges in rows:
        cols = st.columns(len(row_challenges))
        for col, ch in zip(cols, row_challenges):
            title = ch.get('challenge_title', '⚡ Challenge')
            desc  = ch.get('challenge_description', '')
            with col:
                st.markdown(f"""
                    <div class="challenge-card" style="
                        height: 100%;
                        min-height: 160px;
                        display: flex;
                        flex-direction: column;
                        justify-content: flex-start;
                    ">
                        <div class="challenge-title">{title}</div>
                        <div class="challenge-text" style="font-size: 16px; margin-top: 8px;">{desc}</div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# ============================================================================
# DEMO DATA (for testing without Google Sheets connection)
# ============================================================================

def get_demo_data():
    """Generate demo data matching the real Google Sheets column spec"""
    managers   = ["Ahmed", "Mohamed", "Sara", "Fatima", "Omar"]
    companies  = {m: f"{m}_Co" for m in managers}

    # Week date samples (one date per week, mid-week)
    week_sample_dates = {
        1: "4/6/2026",
        2: "4/13/2026",
        3: "4/20/2026",
        4: "4/27/2026",
    }

    target_rows   = []
    clients_rows  = []
    leads_rows    = []
    meetings_rows = []

    for week, date_str in week_sample_dates.items():
        for manager in managers:
            company = companies[manager]
            target_hot = random.randint(8, 15)

            # --- Target sheet ---
            target_rows.append({
                'Companies':    company,
                'Target Hot':   target_hot,
                'Clients':      random.randint(10, 30),
                'Target Leads': random.randint(20, 40),
                'Budget':       random.randint(5000, 15000),
                'Manager':      manager,
                'Date':         date_str,
            })

            # --- Clients sheet ---
            actual_hot  = random.randint(3, target_hot + 2)
            actual_cold = random.randint(2, 10)
            clients_rows.append({
                'Company': company,
                'Hot':     actual_hot,
                'Cold':    actual_cold,
                'Date':    date_str,
            })

            # --- Leads sheet ---
            leads_rows.append({
                'Company':        company,
                'Number of leads': random.randint(10, 35),
                'Date Leads':     date_str,
            })

            # --- Meetings sheet ---
            meetings_rows.append({
                'Name Meeting':  f"Meeting_{manager}_W{week}",
                'Leads Meeting': company,
                'Meeting':       random.randint(2, 10),
                'Date Meeting':  date_str,
            })

    target_df   = pd.DataFrame(target_rows)
    leads_df    = pd.DataFrame(leads_rows)
    clients_df  = pd.DataFrame(clients_rows)
    meetings_df = pd.DataFrame(meetings_rows)

    # Add week numbers
    target_df, leads_df, clients_df, meetings_df = process_data(
        target_df, leads_df, clients_df, meetings_df
    )

    return target_df, leads_df, clients_df, meetings_df

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point"""
    inject_custom_css()
    render_header()

    if 'message_prefix' not in st.session_state:
        st.session_state.message_prefix = ''

    spreadsheet  = None
    use_demo     = False

    spreadsheet = connect_to_sheets()

    if spreadsheet:
        try:
            target_df, leads_df, clients_df, meetings_df = get_data(spreadsheet)
            if target_df.empty or clients_df.empty:
                st.warning("⚠️ Sheets are empty. Using demo data for preview.")
                use_demo = True
            else:
                target_df, leads_df, clients_df, meetings_df = process_data(
                    target_df, leads_df, clients_df, meetings_df
                )
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            use_demo = True
    else:
        use_demo = True

    if use_demo:
        st.info("📊 Using demo data for preview. Add credentials.json to connect to your Google Sheet.")
        target_df, leads_df, clients_df, meetings_df = get_demo_data()

    scores_df       = calculate_weekly_scores(target_df, leads_df, clients_df, meetings_df)
    rankings_df     = calculate_rankings(scores_df)
    total_standings = calculate_total_standings(rankings_df)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 WEEKLY",
        "🏅 TOTAL",
        "💬 CHAT",
        "🎮 GAMES"
    ])

    with tab1:
        render_weekly_tab(rankings_df)
    with tab2:
        render_total_tab(total_standings)
    with tab3:
        render_chat_tab(spreadsheet)
    with tab4:
        render_games_tab(rankings_df, total_standings, spreadsheet=spreadsheet)

    st.markdown("""
        <div style="text-align: center; padding: 40px 20px; margin-top: 40px; border-top: 1px solid rgba(0, 255, 136, 0.2);">
            <p style="font-family: 'Rajdhani', sans-serif; color: #666;">
                🎮 Marketing ARENA | Built for Champions | © 2026
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
