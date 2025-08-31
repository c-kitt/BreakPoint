let playerNames = [];

// Load all player names on page load
async function loadPlayerNames() {
    try {
        const response = await fetch('/api/players/names');
        const names = await response.json();
        playerNames = names;
        console.log(`Loaded ${names.length} player names from database`);
    } catch (error) {
        console.error('Error loading players:', error);
        // Fallback to empty array if API fails
        playerNames = [];
    }
}

function initializeAutocomplete() {
    const player1Input = document.getElementById('player1');
    const player2Input = document.getElementById('player2');
    const suggestions1 = document.getElementById('suggestions1');
    const suggestions2 = document.getElementById('suggestions2');

    setupAutocomplete(player1Input, suggestions1);
    setupAutocomplete(player2Input, suggestions2);
}

function setupAutocomplete(input, suggestionsDiv) {
    input.addEventListener('input', function() {
        const value = this.value.trim();
        
        if (!value) {
            suggestionsDiv.style.display = 'none';
            return;
        }

        // Filter names that contain the typed value (case insensitive)
        const filteredNames = playerNames.filter(name => 
            name.toLowerCase().includes(value.toLowerCase())
        );

        if (filteredNames.length === 0) {
            suggestionsDiv.style.display = 'none';
            return;
        }

        // Show only first 3 matches
        suggestionsDiv.innerHTML = '';
        filteredNames.slice(0, 3).forEach(name => {
            const div = document.createElement('div');
            div.textContent = name;
            div.addEventListener('click', function() {
                input.value = name;
                suggestionsDiv.style.display = 'none';
            });
            suggestionsDiv.appendChild(div);
        });

        suggestionsDiv.style.display = 'block';
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !suggestionsDiv.contains(e.target)) {
            suggestionsDiv.style.display = 'none';
        }
    });
}

let currentSurface = 'grass'; // Default surface
const surfaces = ['grass', 'hard', 'clay'];

function initializeSurfaceButton() {
    const surfaceButton = document.querySelector('.btn-surface');
    
    surfaceButton.addEventListener('click', function() {
        // Cycle through surfaces
        const currentIndex = surfaces.indexOf(currentSurface);
        const nextIndex = (currentIndex + 1) % surfaces.length;
        currentSurface = surfaces[nextIndex];
        
        // Update button text and colors
        updateSurfaceDisplay();
    });
}

function updateSurfaceDisplay() {
    const surfaceButton = document.querySelector('.btn-surface');
    const courtOutline = document.querySelector('.court-outline');
    const title = document.querySelector('.title');
    
    switch(currentSurface) {
        case 'grass':
            surfaceButton.textContent = 'Grass';
            surfaceButton.className = 'btn-surface surface-grass';
            courtOutline.className = 'court-outline surface-grass';
            title.className = 'title surface-grass';
            break;
        case 'hard':
            surfaceButton.textContent = 'Hard';
            surfaceButton.className = 'btn-surface surface-hard';
            courtOutline.className = 'court-outline surface-hard';
            title.className = 'title surface-hard';
            break;
        case 'clay':
            surfaceButton.textContent = 'Clay';
            surfaceButton.className = 'btn-surface surface-clay';
            courtOutline.className = 'court-outline surface-clay';
            title.className = 'title surface-clay';
            break;
    }
}

function initializePredictButton() {
    const predictButton = document.querySelector('.btn-predict');
    
    predictButton.addEventListener('click', async function() {
        const player1Input = document.getElementById('player1');
        const player2Input = document.getElementById('player2');
        
        const player1 = player1Input.value.trim();
        const player2 = player2Input.value.trim();
        
        if (!player1 || !player2) {
            alert('Please select both players');
            return;
        }
        
        if (player1 === player2) {
            alert('Please select two different players');
            return;
        }
        
        // Clear previous winner highlighting
        player1Input.classList.remove('winner');
        player2Input.classList.remove('winner');
        
        try {
            predictButton.textContent = 'Predicting...';
            predictButton.disabled = true;
            
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    player1: player1,
                    player2: player2,
                    surface: currentSurface
                })
            });
            
            const result = await response.json();
            
            if (result.winner === player1) {
                player1Input.classList.add('winner');
            } else {
                player2Input.classList.add('winner');
            }
            
        } catch (error) {
            console.error('Prediction error:', error);
            alert('Error making prediction');
        } finally {
            predictButton.textContent = 'Predict';
            predictButton.disabled = false;
        }
    });
}

document.addEventListener('DOMContentLoaded', async function() {
    await loadPlayerNames();
    initializeAutocomplete();
    initializeSurfaceButton();
    initializePredictButton();
    updateSurfaceDisplay(); // Set initial display
});