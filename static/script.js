// DOM要素の取得
const addTaskForm = document.getElementById('add-task-form');
const editTaskForm = document.getElementById('edit-task-form');
const editModal = document.getElementById('edit-modal');
const taskTbody = document.getElementById('task-tbody');
const loading = document.getElementById('loading');
const sortAscBtn = document.getElementById('sort-asc');
const sortDescBtn = document.getElementById('sort-desc');

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    // 今日の日付を期日フィールドの最小値に設定
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('due_date').setAttribute('min', today);
    document.getElementById('edit-due_date').setAttribute('min', today);
});

// ローディング表示制御
function showLoading() {
    loading.style.display = 'flex';
}

function hideLoading() {
    loading.style.display = 'none';
}

// フラッシュメッセージを自動で非表示にする
function hideFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
}

// ページ読み込み時にフラッシュメッセージを非表示にする
document.addEventListener('DOMContentLoaded', hideFlashMessages);

// 新しいタスク追加
addTaskForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(addTaskForm);
    
    // バリデーション
    if (!validateForm(formData)) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/add_task', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // フォームをリセット
            addTaskForm.reset();
            
            // ページをリロードしてタスク一覧を更新
            location.reload();
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('サーバーエラーが発生しました。', 'error');
    } finally {
        hideLoading();
    }
});

// タスク編集
function editTask(taskId) {
    const taskRow = document.querySelector(`tr[data-task-id="${taskId}"]`);
    if (!taskRow) return;
    
    const cells = taskRow.querySelectorAll('td');
    const title = cells[0].textContent.trim();
    const content = cells[1].textContent.trim();
    const dueDate = cells[2].textContent.trim();
    const memo = cells[3].textContent.trim();
    
    // モーダルに値を設定
    document.getElementById('edit-task-id').value = taskId;
    document.getElementById('edit-title').value = title;
    document.getElementById('edit-content').value = content;
    document.getElementById('edit-due_date').value = dueDate;
    document.getElementById('edit-memo').value = memo;
    
    // モーダルを表示
    editModal.style.display = 'block';
    editModal.setAttribute('aria-hidden', 'false');
    document.getElementById('edit-title').focus();
}

// タスク更新
editTaskForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(editTaskForm);
    const taskId = formData.get('task_id');
    
    // バリデーション
    if (!validateForm(formData)) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`/update_task/${taskId}`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            closeEditModal();
            location.reload();
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('サーバーエラーが発生しました。', 'error');
    } finally {
        hideLoading();
    }
});

// タスク削除
async function deleteTask(taskId) {
    if (!confirm('このタスクを削除しますか？')) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`/delete_task/${taskId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            location.reload();
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('サーバーエラーが発生しました。', 'error');
    } finally {
        hideLoading();
    }
}

// タスクソート
sortAscBtn.addEventListener('click', () => sortTasks('asc'));
sortDescBtn.addEventListener('click', () => sortTasks('desc'));

async function sortTasks(sortType) {
    showLoading();
    
    try {
        const response = await fetch('/sort_tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ sort_type: sortType })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateTaskTable(result.tasks);
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('ソートに失敗しました。', 'error');
    } finally {
        hideLoading();
    }
}

// テーブル更新
function updateTaskTable(tasks) {
    taskTbody.innerHTML = '';
    
    tasks.forEach(task => {
        const row = document.createElement('tr');
        row.className = 'task-row';
        row.setAttribute('data-task-id', task.id);
        
        row.innerHTML = `
            <td class="col-title">${escapeHtml(task.title)}</td>
            <td class="col-content">${escapeHtml(task.content)}</td>
            <td class="col-due-date">${escapeHtml(task.due_date)}</td>
            <td class="col-memo">${escapeHtml(task.memo)}</td>
            <td class="col-actions">
                <button class="edit-btn" onclick="editTask(${task.id})" aria-label="タスクを編集">
                    ✏️
                </button>
                <button class="delete-btn" onclick="deleteTask(${task.id})" aria-label="タスクを削除">
                    🗑️
                </button>
            </td>
        `;
        
        taskTbody.appendChild(row);
    });
}

// モーダル制御
function closeEditModal() {
    editModal.style.display = 'none';
    editModal.setAttribute('aria-hidden', 'true');
    editTaskForm.reset();
}

// モーダル外クリックで閉じる
editModal.addEventListener('click', function(e) {
    if (e.target === editModal) {
        closeEditModal();
    }
});

// ESCキーでモーダルを閉じる
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && editModal.style.display === 'block') {
        closeEditModal();
    }
});

// バリデーション関数
function validateForm(formData) {
    const title = formData.get('title');
    const dueDate = formData.get('due_date');
    
    if (!title || title.trim() === '') {
        showMessage('タイトルは必須です。', 'error');
        return false;
    }
    
    if (!dueDate || dueDate.trim() === '') {
        showMessage('期日は必須です。', 'error');
        return false;
    }
    
    return true;
}

// メッセージ表示関数
function showMessage(message, type = 'info') {
    // 既存のメッセージを削除
    const existingMessages = document.querySelectorAll('.flash-message');
    existingMessages.forEach(msg => msg.remove());
    
    // 新しいメッセージを作成
    const messageDiv = document.createElement('div');
    messageDiv.className = `flash-message ${type}`;
    messageDiv.setAttribute('role', 'alert');
    messageDiv.setAttribute('aria-live', 'polite');
    messageDiv.innerHTML = `<p>${message}</p>`;
    
    // メッセージを挿入
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    // 自動で非表示にする
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => {
            messageDiv.remove();
        }, 300);
    }, 5000);
}

// HTMLエスケープ関数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
