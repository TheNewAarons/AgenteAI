marked.setOptions({
    breaks: true,
    gfm: true
});
mermaid.initialize({ startOnLoad: false, theme: 'dark' });

const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const latencyDisplay = document.getElementById('latencyDisplay');
const editorContainer = document.getElementById('editorContainer');
const mainContainer = document.getElementById('mainContainer');

let aceEditor = null;
let currentFilePath = null;

// Funciones de utilidad
function getCurrentTime() {
    const now = new Date();
    return now.toTimeString().split(' ')[0];
}

async function loadFileList() {
    const explorer = document.getElementById('fileExplorer');
    try {
        const response = await fetch('/list_files');
        const data = await response.json();

        const lines = data.structure.split('\n');
        explorer.innerHTML = '';
        lines.forEach(line => {
            const div = document.createElement('div');
            div.className = 'file-item';
            div.innerText = line;

            const fileName = line.trim().replace(/\/$/, '');
            if (fileName && !line.includes('/')) {
                div.onclick = () => simulateAIResponse(`Lee el archivo ${line.trim()} y muéstramelo`);
            }
            explorer.appendChild(div);
        });
    } catch (e) {
        explorer.innerText = '> ERROR LOADING FILES';
    }
}

async function saveCodeToServer() {
    if (!currentFilePath) {
        const path = prompt("> ENTER SAVE PATH:", "new_file.py");
        if (!path) return;
        currentFilePath = path;
    }

    const code = aceEditor.getValue();
    const btn = document.getElementById('saveFileBtn');
    const originalText = btn.innerText;

    btn.innerText = "SAVING...";
    btn.disabled = true;

    try {
        const response = await fetch('/save_file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: currentFilePath, content: code })
        });
        const data = await response.json();

        btn.innerText = "SAVED";
        btn.style.backgroundColor = "#4caf50";
        loadFileList();

        setTimeout(() => {
            btn.innerText = originalText;
            btn.style.backgroundColor = "";
            btn.disabled = false;
        }, 2000);
    } catch (e) {
        btn.innerText = "ERROR";
        btn.style.backgroundColor = "#f44336";
        setTimeout(() => {
            btn.innerText = originalText;
            btn.style.backgroundColor = "";
            btn.disabled = false;
        }, 2000);
    }
}

function openEditor(codeContent, languageClass, filePath = null) {
    currentFilePath = filePath;
    editorContainer.classList.add('active');
    mainContainer.classList.add('editor-open');

    let mode = "ace/mode/javascript";
    if (languageClass) {
        if (languageClass.includes("python")) mode = "ace/mode/python";
        if (languageClass.includes("html") || languageClass.includes("xml")) mode = "ace/mode/xml";
        if (languageClass.includes("css")) mode = "ace/mode/css";
    }

    setTimeout(() => {
        if (!aceEditor) {
            aceEditor = ace.edit("codeEditor");
            aceEditor.setTheme("ace/theme/tomorrow_night_eighties");
            aceEditor.setOptions({
                fontSize: "14px",
                showPrintMargin: false,
                wrap: true
            });
        }

        aceEditor.session.setMode(mode);
        aceEditor.setValue(codeContent);
        aceEditor.clearSelection();

        setTimeout(() => { aceEditor.resize(); aceEditor.focus(); }, 100);
    }, 10);
}

function closeEditor() {
    editorContainer.classList.remove('active');
    mainContainer.classList.remove('editor-open');
}

function createMessage(content, isUser = true) {
    const message = document.createElement('div');
    message.className = `message ${isUser ? 'user' : 'ai'}`;
    message.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">${isUser ? 'U' : 'AI'}</div>
            <span class="message-sender">${isUser ? 'USER' : 'SYSTEM'}</span>
            <span class="message-time">${getCurrentTime()}</span>
        </div>
        <div class="message-content">${content}</div>
    `;
    return message;
}

function addMessage(content, isUser = true) {
    const message = createMessage(content, isUser);
    chatContainer.insertBefore(message, typingIndicator);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function simulateAIResponse(userMessage) {
    typingIndicator.style.display = 'flex';
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Comandos locales
    if (['/clear', '/help', '/status', '/history'].includes(userMessage)) {
        handleLocalCommand(userMessage);
        return;
    }

    const startTime = Date.now();
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMessage })
        });

        if (!response.ok) throw new Error("Server error");

        typingIndicator.style.display = 'none';
        const message = createMessage('', false);
        chatContainer.insertBefore(message, typingIndicator);

        const contentDiv = message.querySelector('.message-content');
        let fullText = "";

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (let line of lines) {
                line = line.trim();
                if (line.startsWith('data: ')) {
                    const dataStr = line.replace('data: ', '').trim();
                    if (dataStr) {
                        try {
                            const parsed = JSON.parse(dataStr);
                            if (parsed.error) fullText += "\n> ERROR: " + parsed.error;
                            else if (parsed.chunk) fullText += parsed.chunk;

                            contentDiv.innerHTML = DOMPurify.sanitize(marked.parse(fullText));

                            contentDiv.querySelectorAll('pre code').forEach((block) => {
                                if (!block.className.includes('language-mermaid')) {
                                    hljs.highlightElement(block);
                                    if (!block.parentElement.querySelector('.code-action-btn')) {
                                        injectEditorButton(block);
                                    }
                                }
                                else {
                                    renderMermaid(block);
                                }
                            });

                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        } catch (e) { console.error("Parse error", e); }
                    }
                }
            }
        }
        latencyDisplay.innerText = `LATENCY: ${Date.now() - startTime}ms`;
    } catch (error) {
        typingIndicator.style.display = 'none';
        addMessage('> CONNECTION ERROR', false);
    }
}

function handleLocalCommand(cmd) {
    typingIndicator.style.display = 'none';
    if (cmd === '/clear') {
        chatContainer.querySelectorAll('.message').forEach(msg => {
            if (!msg.querySelector('.message-content').innerHTML.includes('WELCOME')) msg.remove();
        });
        fetch('/clear_history', { method: 'POST' });
    } else if (cmd === '/status') {
        addMessage('> STATUS: OPERATIONAL | RAG: ACTIVE | MODULAR: YES', false);
    }
}

function injectEditorButton(block) {
    const btn = document.createElement('button');
    btn.className = 'code-action-btn';
    btn.innerText = 'EDIT';
    let langClass = "";
    block.classList.forEach(cls => { if (cls.startsWith('language-')) langClass = cls; });
    btn.onclick = () => openEditor(block.textContent, langClass);
    block.parentElement.appendChild(btn);
}

async function renderMermaid(block) {
    try {
        const id = 'mermaid-' + Date.now();
        const { svg } = await mermaid.render(id, block.textContent);
        const container = document.createElement('div');
        container.innerHTML = svg;
        container.className = 'mermaid-render';
        block.parentElement.replaceWith(container);
    } catch (e) { console.warn("Mermaid error", e); }
}

function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        addMessage(message, true);
        messageInput.value = '';
        messageInput.style.height = 'auto';
        simulateAIResponse(message);
    }
}

async function refreshTasks() {
    const panel = document.getElementById('tasksPanel');
    try {
        const response = await fetch('/tasks');
        const tasks = await response.json();

        if (!tasks || tasks.length === 0) {
            panel.innerHTML = '<div class="no-tasks">> NO ACTIVE PLAN</div>';
            return;
        }

        panel.innerHTML = '';
        tasks.forEach(t => {
            const div = document.createElement('div');
            const statusClass = t.status.toLowerCase().replace(' ', '-');
            div.className = `task-item status-${statusClass}`;
            div.innerHTML = `
                <span class="task-status">${t.status}</span>
                <span class="task-id">#${t.id}</span>
                <span class="task-desc">${t.description}</span>
            `;
            panel.appendChild(div);
        });
    } catch (e) {
        console.warn("Error refreshing tasks", e);
    }
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

window.onload = () => {
    loadFileList();
    refreshTasks();
    setInterval(refreshTasks, 5000);
};
