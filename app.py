from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import os
import logging
from config import Config
from google_api import GoogleSheetsAPI, GoogleCalendarAPI

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Google APIクライアント初期化
try:
    # 環境変数から認証情報を取得
    credentials_file = Config.GOOGLE_CREDENTIALS_FILE
    if not credentials_file or not os.path.exists(credentials_file):
        credentials_file = None  # 環境変数から取得する
    
    logger.info("Google APIクライアント初期化開始...")
    sheets_api = GoogleSheetsAPI(
        credentials_file,
        Config.GOOGLE_SHEETS_ID
    )
    calendar_api = GoogleCalendarAPI(
        credentials_file,
        Config.GOOGLE_CALENDAR_ID
    )
    logger.info("Google APIクライアント初期化成功")
except Exception as e:
    logger.error(f"Google APIクライアント初期化エラー: {e}")
    sheets_api = None
    calendar_api = None

@app.route('/')
def index():
    """メインページ"""
    try:
        if not sheets_api:
            flash('Google APIの設定に問題があります。設定を確認してください。', 'error')
            return render_template('index.html', tasks=[], error=True)
        
        tasks = sheets_api.get_tasks()
        return render_template('index.html', tasks=tasks, error=False)
    except Exception as e:
        logger.error(f"メインページエラー: {e}")
        flash('データの取得に失敗しました。', 'error')
        return render_template('index.html', tasks=[], error=True)

@app.route('/add_task', methods=['POST'])
def add_task():
    """新しいタスクを追加"""
    try:
        if not sheets_api:
            return jsonify({'success': False, 'message': 'Google APIの設定に問題があります。'})
        
        # フォームデータを取得
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        due_date = request.form.get('due_date', '').strip()
        memo = request.form.get('memo', '').strip()
        
        # バリデーション
        if not title:
            return jsonify({'success': False, 'message': 'タイトルは必須です。'})
        
        if not due_date:
            return jsonify({'success': False, 'message': '期日は必須です。'})
        
        # 日付形式のバリデーション
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'success': False, 'message': '期日はYYYY-MM-DD形式で入力してください。'})
        
        # タスクを追加
        success = sheets_api.add_task(title, content, due_date, memo)
        
        if success:
            # リマインドイベントを作成
            if calendar_api:
                try:
                    calendar_api.create_reminder(title, due_date, memo)
                except Exception as e:
                    logger.warning(f"リマインドイベント作成失敗: {e}")
            
            return jsonify({'success': True, 'message': 'タスクが正常に追加されました。'})
        else:
            return jsonify({'success': False, 'message': 'タスクの追加に失敗しました。'})
            
    except Exception as e:
        logger.error(f"タスク追加エラー: {e}")
        return jsonify({'success': False, 'message': 'サーバーエラーが発生しました。'})

@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    """タスクを更新"""
    try:
        if not sheets_api:
            return jsonify({'success': False, 'message': 'Google APIの設定に問題があります。'})
        
        # フォームデータを取得
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        due_date = request.form.get('due_date', '').strip()
        memo = request.form.get('memo', '').strip()
        
        # バリデーション
        if not title:
            return jsonify({'success': False, 'message': 'タイトルは必須です。'})
        
        if not due_date:
            return jsonify({'success': False, 'message': '期日は必須です。'})
        
        # 日付形式のバリデーション
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'success': False, 'message': '期日はYYYY-MM-DD形式で入力してください。'})
        
        # タスクを更新
        success = sheets_api.update_task(task_id, title, content, due_date, memo)
        
        if success:
            return jsonify({'success': True, 'message': 'タスクが正常に更新されました。'})
        else:
            return jsonify({'success': False, 'message': 'タスクの更新に失敗しました。'})
            
    except Exception as e:
        logger.error(f"タスク更新エラー: {e}")
        return jsonify({'success': False, 'message': 'サーバーエラーが発生しました。'})

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    """タスクを削除"""
    try:
        if not sheets_api:
            return jsonify({'success': False, 'message': 'Google APIの設定に問題があります。'})
        
        success = sheets_api.delete_task(task_id)
        
        if success:
            return jsonify({'success': True, 'message': 'タスクが正常に削除されました。'})
        else:
            return jsonify({'success': False, 'message': 'タスクの削除に失敗しました。'})
            
    except Exception as e:
        logger.error(f"タスク削除エラー: {e}")
        return jsonify({'success': False, 'message': 'サーバーエラーが発生しました。'})

@app.route('/sort_tasks', methods=['POST'])
def sort_tasks():
    """タスクをソート"""
    try:
        if not sheets_api:
            return jsonify({'success': False, 'message': 'Google APIの設定に問題があります。'})
        
        sort_type = request.json.get('sort_type', 'asc')
        tasks = sheets_api.get_tasks()
        
        # 期日でソート
        if sort_type == 'asc':
            tasks.sort(key=lambda x: x.get('due_date', ''))
        else:
            tasks.sort(key=lambda x: x.get('due_date', ''), reverse=True)
        
        return jsonify({'success': True, 'tasks': tasks})
        
    except Exception as e:
        logger.error(f"タスクソートエラー: {e}")
        return jsonify({'success': False, 'message': 'ソートに失敗しました。'})

# Render用の設定
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)