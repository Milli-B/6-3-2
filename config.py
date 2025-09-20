import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class Config:
    # Flask設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Google API設定
    GOOGLE_CREDENTIALS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE')
    GOOGLE_CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')  # 環境変数からの認証情報
    GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID')
    GOOGLE_CALENDAR_ID = os.environ.get('GOOGLE_CALENDAR_ID') or 'primary'
    
    # スプレッドシート設定
    SHEET_NAME = os.environ.get('SHEET_NAME', 'TaskList')
    HEADERS = ['タイトル', '内容', '期日', 'メモ📝', '作成日時']
    
    # リマインド設定
    REMINDER_DAYS_BEFORE = 2
