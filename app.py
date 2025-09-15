from __future__ import annotations

import json
import os
import traceback
import sys
from datetime import datetime
from typing import List, Dict, Any

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired

from dotenv import load_dotenv
load_dotenv()

# エラーハンドリング用の関数
def log_error(error, context=""):
    print(f"[ERROR] {context}: {error}")
    print(f"[ERROR] Traceback: {traceback.format_exc()}")
    sys.stdout.flush()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_ROOT, "tasks.json")

try:
    # 相対import（パッケージとして実行されない場合のフォールバック）
    from . import config as app_config
    from . import google_api
except Exception:
    import config as app_config  # type: ignore
    import google_api  # type: ignore


def ensure_data_file_exists() -> None:
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def load_tasks() -> List[Dict[str, Any]]:
    try:
        # Sheets優先、未設定や失敗時はローカルJSONへフォールバック
        if app_config.USE_SHEETS and app_config.GOOGLE_SHEETS_SPREADSHEET_ID:
            print(f"[DEBUG] Sheets読み取りを試行中...")
            print(f"[DEBUG] USE_SHEETS: {app_config.USE_SHEETS}")
            print(f"[DEBUG] SPREADSHEET_ID: {app_config.GOOGLE_SHEETS_SPREADSHEET_ID}")
            
            result = google_api.read_tasks_from_sheet()
            print(f"[DEBUG] Sheets読み取り成功: {len(result)}件")
            return result
        else:
            print(f"[DEBUG] Sheets機能が無効またはID未設定")
    except Exception as e:
        log_error(e, "Sheets読み取り")
        print(f"[WARN] Sheets読み取り失敗のためローカルへフォールバック: {e}")
    
    # フォールバック
    ensure_data_file_exists()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


class TaskForm(FlaskForm):
    title = StringField("タイトル", validators=[DataRequired(message="タイトルは必須です")])
    content = TextAreaField("内容")
    due_date = DateField("期日", validators=[DataRequired(message="期日は必須です")], format="%Y-%m-%d")
    memo = TextAreaField("メモ📝")
    submit = SubmitField("追加")


# Flaskアプリケーションの作成
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

@app.route("/", methods=["GET", "POST"])
def index():
    form = TaskForm()
    tasks = load_tasks()

    # ソート
    order = request.args.get("order", "asc")
    def parse_date(value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d")

    try:
        tasks_sorted = sorted(tasks, key=lambda t: parse_date(t["due_date"]), reverse=(order == "desc"))
    except Exception:
        tasks_sorted = tasks

    if request.method == "POST" and form.validate_on_submit():
        new_task = {
            "title": form.title.data.strip(),
            "content": (form.content.data or "").strip(),
            "due_date": form.due_date.data.strftime("%Y-%m-%d"),
            "memo": (form.memo.data or "").strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # 先にSheetsへ
        if app_config.USE_SHEETS and app_config.GOOGLE_SHEETS_SPREADSHEET_ID:
            try:
                google_api.append_task_to_sheet(new_task)
                print(f"[DEBUG] Sheets追加成功: {new_task['title']}")
            except Exception as e:
                log_error(e, "Sheets追加")
                print(f"[WARN] Sheets追加失敗のためローカル保存へフォールバック: {e}")
        
        # カレンダーにリマインドイベントを作成
        if app_config.USE_CALENDAR and app_config.GOOGLE_SHEETS_SPREADSHEET_ID:
            try:
                google_api.create_reminder_event(new_task)
                print(f"[INFO] リマインドイベントを作成しました: {new_task['title']}")
            except Exception as e:
                log_error(e, "リマインドイベント作成")
                print(f"[WARN] リマインドイベント作成失敗: {e}")
        
        # ローカルにも反映（フォールバック/キャッシュ目的）
        tasks.append(new_task)
        save_tasks(tasks)
        flash("タスクを追加しました", "success")
        return redirect(url_for("index", order=order))

    if request.method == "POST" and not form.validate():
        flash("入力内容を確認してください", "error")

    return render_template("index.html", form=form, tasks=tasks_sorted, order=order)

@app.route("/delete/<int:task_index>", methods=["POST"])
def delete_task(task_index):
    try:
        # Sheetsから削除
        if app_config.USE_SHEETS and app_config.GOOGLE_SHEETS_SPREADSHEET_ID:
            google_api.delete_task_from_sheet(task_index)
        
        # ローカルからも削除（フォールバック/キャッシュ目的）
        tasks = load_tasks()
        if 0 <= task_index < len(tasks):
            tasks.pop(task_index)
            save_tasks(tasks)
        
        flash("タスクを削除しました", "success")
    except Exception as e:
        log_error(e, "タスク削除")
        flash(f"削除に失敗しました: {e}", "error")
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)