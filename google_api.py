import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheetsAPI:
    def __init__(self, credentials_file: str, spreadsheet_id: str):
        """Google Sheets APIクライアントを初期化"""
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=self.credentials)
            self.spreadsheet_id = spreadsheet_id
            logger.info("Google Sheets API初期化成功")
        except Exception as e:
            logger.error(f"Google Sheets API初期化エラー: {e}")
            raise

    def get_tasks(self) -> List[Dict]:
        """スプレッドシートからタスク一覧を取得"""
        try:
            range_name = f'{os.environ.get("SHEET_NAME", "タスク一覧")}!A:E'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return []
            
            # ヘッダー行をスキップしてデータを取得
            headers = values[0] if values else []
            tasks = []
            
            for i, row in enumerate(values[1:], start=2):  # ヘッダー行をスキップ
                if len(row) >= 4:  # 最低限の列数チェック
                    task = {
                        'id': i,
                        'title': row[0] if len(row) > 0 else '',
                        'content': row[1] if len(row) > 1 else '',
                        'due_date': row[2] if len(row) > 2 else '',
                        'memo': row[3] if len(row) > 3 else '',
                        'created_at': row[4] if len(row) > 4 else ''
                    }
                    tasks.append(task)
            
            logger.info(f"{len(tasks)}件のタスクを取得")
            return tasks
            
        except HttpError as e:
            logger.error(f"Google Sheets読み取りエラー: {e}")
            return []
        except Exception as e:
            logger.error(f"タスク取得エラー: {e}")
            return []

    def add_task(self, title: str, content: str, due_date: str, memo: str) -> bool:
        """新しいタスクをスプレッドシートに追加"""
        try:
            range_name = f'{os.environ.get("SHEET_NAME", "タスク一覧")}!A:E'
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            values = [[title, content, due_date, memo, created_at]]
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"タスク追加成功: {title}")
            return True
            
        except HttpError as e:
            logger.error(f"Google Sheets書き込みエラー: {e}")
            return False
        except Exception as e:
            logger.error(f"タスク追加エラー: {e}")
            return False

    def update_task(self, row_id: int, title: str, content: str, due_date: str, memo: str) -> bool:
        """タスクを更新"""
        try:
            range_name = f'{os.environ.get("SHEET_NAME", "タスク一覧")}!A{row_id}:E{row_id}'
            values = [[title, content, due_date, memo]]
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"タスク更新成功: {title}")
            return True
            
        except HttpError as e:
            logger.error(f"Google Sheets更新エラー: {e}")
            return False
        except Exception as e:
            logger.error(f"タスク更新エラー: {e}")
            return False

    def delete_task(self, row_id: int) -> bool:
        """タスクを削除"""
        try:
            # 行を削除
            request_body = {
                'requests': [{
                    'deleteDimension': {
                        'range': {
                            'sheetId': 0,  # 最初のシート
                            'dimension': 'ROWS',
                            'startIndex': row_id - 1,
                            'endIndex': row_id
                        }
                    }
                }]
            }
            
            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            
            logger.info(f"タスク削除成功: 行{row_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Google Sheets削除エラー: {e}")
            return False
        except Exception as e:
            logger.error(f"タスク削除エラー: {e}")
            return False


class GoogleCalendarAPI:
    def __init__(self, credentials_file: str, calendar_id: str = 'primary'):
        """Google Calendar APIクライアントを初期化"""
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            self.service = build('calendar', 'v3', credentials=self.credentials)
            self.calendar_id = calendar_id
            logger.info("Google Calendar API初期化成功")
        except Exception as e:
            logger.error(f"Google Calendar API初期化エラー: {e}")
            raise

    def create_reminder(self, title: str, due_date_str: str, memo: str = '') -> bool:
        """期日の2日前にリマインドイベントを作成"""
        try:
            # 期日を解析
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            reminder_date = due_date - timedelta(days=2)
            
            # リマインドイベントの詳細
            event_title = f"📝 リマインド: {title}"
            event_description = f"タスク: {title}\n期日: {due_date_str}\nメモ: {memo}"
            
            # イベント作成
            event = {
                'summary': event_title,
                'description': event_description,
                'start': {
                    'dateTime': reminder_date.strftime('%Y-%m-%dT09:00:00'),
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': reminder_date.strftime('%Y-%m-%dT09:30:00'),
                    'timeZone': 'Asia/Tokyo',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1日前
                        {'method': 'popup', 'minutes': 30},       # 30分前
                    ],
                },
            }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            logger.info(f"リマインドイベント作成成功: {event_title}")
            return True
            
        except Exception as e:
            logger.error(f"リマインドイベント作成エラー: {e}")
            return False
