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
            
            // Simulate bot response
            setTimeout(() => {
                simulateBotResponse(message);
            }, 1000);
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

    // Simulate bot response
    function simulateBotResponse(userMessage) {
        const responses = [
            "I understand you're asking about " + userMessage + ". Let me help you with that.",
            "That's an interesting question about " + userMessage + ". Here's what I know.",
            "I'd be happy to help you understand more about " + userMessage + ".",
            "Let me analyze " + userMessage + " for you."
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        addMessage(randomResponse, 'bot');
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