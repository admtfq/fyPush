// Function to recognize speech
async function recognizeSpeech() {
    const statusElement = document.getElementById('status');
    const resultElement = document.getElementById('result');

    if (statusElement) {
        statusElement.textContent = "Listening...";
    }

    try {
        const response = await fetch('/recognize', {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();

        if (statusElement) {
            statusElement.textContent = "Recognition completed.";
        }
        if (resultElement) {
            resultElement.textContent = "Recognized Text: " + result.text;
        }
    } catch (error) {
        console.error("Error recognizing speech:", error);
        if (statusElement) {
            statusElement.textContent = "Error in recognition.";
        }
    }
}

// Function to toggle the menu display
function toggleMenu() {
    const menuItems = document.getElementById('menu-items');
    if (menuItems.style.display === 'block') {
        menuItems.style.display = 'none';
    } else {
        menuItems.style.display = 'block';
    }
}
