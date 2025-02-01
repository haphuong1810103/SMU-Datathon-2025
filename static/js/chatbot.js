document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendButton = document.querySelector('.send-btn');

    // Handle sending messages
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            // Add user message
            addMessage(message, 'user');
            
            // Clear input
            chatInput.value = '';

            // Fetch response from backend
            fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.reply, 'bot');
            })
            .catch(error => {
                addMessage("Error: Could not get response from AI.", 'bot');
                console.error("Fetch error:", error);
            });
        }
    }

    // Add a message to the chat
    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        let messageHTML = '';

        if (type === 'bot') {
            messageHTML = `
                <div class="bot-avatar">
                    <img src="/static/images/bot-avatar.png" alt="AskISD Bot">
                </div>
                <div class="message-content">
                    <p>${content}</p>
                </div>
            `;
        } else {
            messageHTML = `
                <div class="message-content">
                    <p>${content}</p>
                </div>
            `;
        }
        
        messageDiv.innerHTML = messageHTML;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Handle file attachment
    const attachButton = document.querySelector('.attach-btn');
    attachButton.addEventListener('click', function() {
        // Implement file attachment functionality
        console.log('File attachment clicked');
    });
});
