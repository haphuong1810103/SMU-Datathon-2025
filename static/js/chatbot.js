document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendButton = document.querySelector('.send-btn');
    const attachButton = document.querySelector('.attach-btn');

    let uploadedFileText = ""; // Store extracted PDF text

    // Handle sending messages
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message && !uploadedFileText) {
            addMessage("Please enter a message or upload a PDF first.", 'bot');
            return;
        }

        // Add user message
        addMessage(`You: ${message}`, 'user');
        if (uploadedFileText) {
            addMessage(`📄 Attached PDF content: ${uploadedFileText.substring(0, 200)}...`, 'user'); // Show snippet
        }

        // Send message & extracted text to backend
        fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                extracted_text: uploadedFileText
            })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.reply, 'bot');
        })
        .catch(error => {
            addMessage("Error: Could not get response from AI.", 'bot');
            console.error("Fetch error:", error);
        });

        // Clear the input and uploaded text after submission
        chatInput.value = '';
        uploadedFileText = "";
    }

    // Add a message to the chat
    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        let messageHTML = `
            <div class="message-content">
                <p>${content}</p>
            </div>
        `;

        messageDiv.innerHTML = messageHTML;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Handle file attachment
    attachButton.addEventListener('click', function() {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf';
        fileInput.style.display = 'none';

        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                uploadFile(file);
            }
        });

        document.body.appendChild(fileInput);
        fileInput.click();
        document.body.removeChild(fileInput);
    });

    // Function to upload and extract text from PDF
    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                uploadedFileText = data.extracted_text;
                addMessage(`📎 PDF Uploaded: ${file.name} (Text extracted)`, 'user');
            } else {
                addMessage("Error: Failed to upload file.", 'bot');
            }
        })
        .catch(error => {
            addMessage("Error: Could not upload file.", 'bot');
            console.error("Upload error:", error);
        });
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
