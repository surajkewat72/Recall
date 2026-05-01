async function syncDrive() {
    const urlInput = document.getElementById('gdrive-url').value;
    const btn = document.getElementById('sync-btn');
    const spinner = document.getElementById('sync-spinner');
    const btnText = document.querySelector('.btn-text');
    const statusMsg = document.getElementById('sync-status');

    // UI Loading state
    btn.disabled = true;
    spinner.style.display = 'block';
    btnText.textContent = 'Syncing...';
    statusMsg.textContent = '';
    statusMsg.style.color = 'var(--text-secondary)';

    const requestBody = urlInput ? { url: urlInput } : {};

    try {
        const response = await fetch('/api/v1/sync-drive', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: Object.keys(requestBody).length > 0 ? JSON.stringify(requestBody) : null
        });

        const data = await response.json();

        if (response.ok) {
            statusMsg.textContent = `Successfully synced ${data.length} file(s).`;
            statusMsg.style.color = 'var(--success-color)';
        } else {
            statusMsg.textContent = data.detail || 'An error occurred during sync.';
            statusMsg.style.color = 'var(--error-color)';
        }
    } catch (err) {
        statusMsg.textContent = 'Failed to connect to the server.';
        statusMsg.style.color = 'var(--error-color)';
    } finally {
        // Reset UI
        btn.disabled = false;
        spinner.style.display = 'none';
        btnText.textContent = 'Sync Document';
    }
}

function handleKeyPress(e) {
    if (e.key === 'Enter') {
        askQuestion();
    }
}

function addMessage(text, sender, sources = []) {
    const container = document.getElementById('chat-messages');
    
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Simple markdown to HTML (just for line breaks)
    contentDiv.innerHTML = text.replace(/\n/g, '<br>');
    msgDiv.appendChild(contentDiv);
    
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'sources';
        sources.forEach(source => {
            const badge = document.createElement('span');
            badge.className = 'source-badge';
            badge.textContent = `📄 ${source}`;
            sourcesDiv.appendChild(badge);
        });
        msgDiv.appendChild(sourcesDiv);
    }

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
    return msgDiv;
}

async function askQuestion() {
    const inputField = document.getElementById('chat-input');
    const filterField = document.getElementById('file-filter');
    const sendBtn = document.getElementById('send-btn');
    
    const query = inputField.value.trim();
    const fileName = filterField.value.trim();
    
    if (!query) return;

    // Add user message
    addMessage(query, 'user');
    inputField.value = '';
    
    // Add temporary loading message
    const loadingMsg = addMessage('Thinking...', 'ai');
    sendBtn.disabled = true;

    const requestBody = { query: query };
    if (fileName) requestBody.file_name = fileName;

    try {
        const response = await fetch('/api/v1/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();
        
        // Remove loading message
        loadingMsg.remove();

        if (response.ok) {
            addMessage(data.answer, 'ai', data.sources);
        } else {
            addMessage(`Error: ${data.detail}`, 'ai');
        }
    } catch (err) {
        loadingMsg.remove();
        addMessage('Failed to connect to the server.', 'ai');
    } finally {
        sendBtn.disabled = false;
        inputField.focus();
    }
}
