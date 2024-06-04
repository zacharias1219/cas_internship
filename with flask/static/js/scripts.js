document.getElementById('scenarioForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const scenario = document.getElementById('scenario').value;
    const level = document.getElementById('level').value;
    sessionStorage.setItem('scenario', scenario);
    sessionStorage.setItem('level', level);
    window.location.href = '/chat';
});

document.getElementById('chatForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const message = document.getElementById('message').value;
    const scenario = sessionStorage.getItem('scenario');
    const level = sessionStorage.getItem('level');

    if (message.trim() === '') return;

    appendMessage('user', message);

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ scenario: scenario, level: level, message: message })
    })
    .then(response => response.json())
    .then(data => {
        appendMessage('assistant', data.response);
        // Handle audio response
        if (data.audio) {
            const audio = new Audio(data.audio);
            audio.play();
        }
    });

    document.getElementById('message').value = '';
});

document.getElementById('resetButton').addEventListener('click', function() {
    fetch('/reset', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'reset') {
            sessionStorage.clear();
            window.location.href = '/';
        }
    });
});

function appendMessage(role, content) {
    const chatbox = document.getElementById('chatbox');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(role);
    messageDiv.textContent = content;
    chatbox.appendChild(messageDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
}
