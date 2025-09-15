# My To do List - 要件定義書

## プロジェクト概要
PythonとFlaskを使用したWebベースのタスク管理アプリケーションを開発する。
データはGoogleスプレッドシートに保存し、Googleカレンダーとの連携によるリマインド機能を持つ。

## 機能要件

### 1. タスク管理機能
- **タスク一覧表示**: 表形式でタスクを上から順番に表示
- **タスク入力**: 新しいタスクを表の最下行に追加可能
- **表の列構成**:
  - タイトル（必須）
  - 内容（任意）
  - 期日（日付形式、必須）
  - メモ📝（任意）

### 2. ソート機能
- 期日列にソート機能を実装
- 「早い順」「遅い順」の2つのソートオプション
- ソートボタンまたはクリック機能で切り替え可能

### 3. リマインド機能
- 期日の2日前に自動でGoogleカレンダーからリマインド通知
- Googleカレンダー APIを使用した自動イベント作成

## 技術要件

### バックエンド
- **フレームワーク**: Flask
- **言語**: Python 3.8以上
- **API連携**:
  - Google Sheets API（データ保存・読み取り）
  - Google Calendar API（リマインド機能）

### フロントエンド
- HTML/CSS/JavaScript
- レスポンシブデザイン対応

### データ保存
- **保存先**: Googleスプレッドシート
- **データ構造**:
  ```
  | タイトル | 内容 | 期日 | メモ📝 | 作成日時 |
  ```

## UI/UXデザイン要件

### デザインガイドライン
- **フォントサイズ**: 通常より大きめに設定（16px以上）
- **表ヘッダー**: 淡い緑色の背景色（#E8F5E8またはsimilar）
- **表全体**: 見やすい行間とパディングを確保
- **レスポンシブ対応**: スマートフォンでも使いやすいデザイン

### 具体的な実装要件
```css
/* ヘッダー部分のスタイル例 */
.table-header {
    background-color: #E8F5E8;
    font-weight: bold;
    font-size: 18px;
}

/* 本文のフォントサイズ */
.table-content {
    font-size: 16px;
}
```

## API連携要件

### Google Sheets API
- スプレッドシートの読み取り・書き込み権限
- OAuth 2.0認証の実装
- データの追加、更新、削除機能

### Google Calendar API
- カレンダーイベントの作成権限
- 期日の2日前の日時計算とイベント作成
- リマインド設定（通知タイミング）

## セキュリティ要件
- Google APIの認証情報を環境変数で管理
- CSRFプロテクション実装
- 入力データのバリデーション

## 開発環境セットアップ
```bash
# 必要なパッケージ
pip install flask google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## ファイル構成
```
my_todo_list/
├── app.py              # メインアプリケーション
├── templates/
│   └── index.html      # フロントエンドHTML
├── static/
│   ├── style.css       # CSS
│   └── script.js       # JavaScript
├── config.py           # 設定ファイル
├── google_api.py       # Google API連携
└── requirements.txt    # 依存パッケージ
```

## 追加考慮事項
1. **エラーハンドリング**: API接続エラー、データ保存失敗時の処理
2. **ユーザビリティ**: 入力フォームのバリデーション
3. **パフォーマンス**: 大量データ対応（ページネーション検討）
4. **アクセシビリティ**: スクリーンリーダー対応

## Cursor実装時の具体的指示

### 初期セットアップ指示
```bash
# Cursorに最初に入力するコマンド
mkdir my_todo_list && cd my_todo_list
pip install flask google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

### 必須実装チェックリスト
- [ ] Google API認証情報の環境変数設定
- [ ] エラーハンドリング（try-catch文を全API呼び出しに実装）
- [ ] フロントエンド・バックエンド両方のバリデーション
- [ ] aria-label、role属性の適切な設定
- [ ] ページネーション機能（50件以上の場合）
- [ ] レスポンシブデザイン（@media queries）
- [ ] CSRF保護の実装

### テスト用データ
```python
# 開発時用のサンプルデータ
SAMPLE_TASKS = [
    {"title": "会議資料作成", "content": "プレゼン資料の準備", "due_date": "2025-09-15", "memo": "重要"},
    {"title": "買い物", "content": "食材購入", "due_date": "2025-09-13", "memo": "卵、牛乳"},
    {"title": "定期検診", "content": "健康診断の予約", "due_date": "2025-09-20", "memo": ""}
]
```