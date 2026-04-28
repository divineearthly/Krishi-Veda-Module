
// frontend/onboarding.js
// This file is for the Krishi-Veda HuggingFace Space frontend logic.
// Assumes basic HTML elements with IDs: #welcome-modal, #start-app-button, #activate-demo-button,
// #ph_input, #n_input, #p_input, #k_input, #moisture_input, #om_input, #run-analysis-button,
// #loading-status, #results-output, #farmer-mode-toggle

document.addEventListener('DOMContentLoaded', () => {
    console.log('Krishi-Veda Onboarding Script Loaded');

    const welcomeModal = document.getElementById('welcome-modal');
    const startAppButton = document.getElementById('start-app-button');
    const activateDemoButton = document.getElementById('activate-demo-button');
    const loadingArea = document.getElementById('loading-status');
    const resultsArea = document.getElementById('results-output');
    const farmerModeToggle = document.getElementById('farmer-mode-toggle');

    // Input fields for demo mode
    const phInput = document.getElementById('ph_input');
    const nInput = document.getElementById('n_input');
    const pInput = document.getElementById('p_input');
    const kInput = document.getElementById('k_input');
    const moistureInput = document.getElementById('moisture_input');
    const omInput = document.getElementById('om_input');

    // --- 1. Welcome Screen Logic ---
    function showWelcomeScreen() {
        if (welcomeModal) {
            welcomeModal.style.display = 'block'; // Show the welcome modal
        }
        console.log('Displaying welcome screen...');
    }

    function hideWelcomeScreen() {
        if (welcomeModal) {
            welcomeModal.style.display = 'none'; // Hide the welcome modal
        }
        console.log('Hiding welcome screen...');
    }

    // Attach event listeners for welcome screen buttons
    if (startAppButton) {
        startAppButton.addEventListener('click', hideWelcomeScreen);
    }

    // --- 2. Demo Mode Functionality ---
    function activateDemoMode() {
        console.log('Activating demo mode...');
        hideWelcomeScreen(); // Hide welcome screen after activating demo

        // Pre-fill inputs with example data
        if (phInput) phInput.value = 6.8;
        if (nInput) nInput.value = 35;
        if (pInput) pInput.value = 30;
        if (kInput) kInput.value = 45;
        if (moistureInput) moistureInput.value = 55;
        if (omInput) omInput.value = 2.1;

        showLoadingMessage('Pre-filling with demo data...');
        setTimeout(() => {
            hideLoadingMessage();
            // Optionally, trigger the analysis button click here or prompt user
            console.log('Demo data pre-filled. User can now run analysis.');
        }, 1000);
    }

    if (activateDemoButton) {
        activateDemoButton.addEventListener('click', activateDemoMode);
    }

    // --- 3. Simplified Farmer UI Elements ---
    // Applies or removes CSS classes to simplify the UI
    function applyFarmerUIMode(enable) {
        console.log(`Applying simplified farmer UI: ${enable ? 'enabled' : 'disabled'}`);
        const body = document.body;
        if (enable) {
            body.classList.add('farmer-friendly-ui');
            // Example: Change button texts or add tooltips
            document.querySelectorAll('button').forEach(btn => {
                if (btn.dataset.originalText) {
                    btn.textContent = btn.dataset.originalText;
                } else {
                    btn.dataset.originalText = btn.textContent; // Store original text
                    if (btn.id === 'run-analysis-button') btn.textContent = 'Get Advice';
                    // Add more specific text changes as needed
                }
                btn.classList.add('large-button');
            });
        } else {
            body.classList.remove('farmer-friendly-ui');
            document.querySelectorAll('button').forEach(btn => {
                if (btn.dataset.originalText) {
                    btn.textContent = btn.dataset.originalText; // Restore original text
                    delete btn.dataset.originalText;
                }
                btn.classList.remove('large-button');
            });
        }
    }

    // Toggle farmer mode based on a UI element (e.g., a checkbox or button)
    if (farmerModeToggle) {
        farmerModeToggle.addEventListener('change', (event) => {
            applyFarmerUIMode(event.target.checked);
        });
        // Initial state
        applyFarmerUIMode(farmerModeToggle.checked);
    }

    // --- 4. Loading Messages ---
    function showLoadingMessage(message) {
        if (loadingArea) {
            loadingArea.innerHTML = `<div class="spinner"></div><p>🌱 ${message}</p>`; // Added a simple spinner CSS class assumption
            loadingArea.style.display = 'flex'; // Use flex for spinner and text alignment
        }
    }

    function hideLoadingMessage() {
        if (loadingArea) {
            loadingArea.style.display = 'none';
        }
    }

    // --- 5. Simplified Results Language ---
    // Expects 'data' to be an object with results from the backend
    function displaySimplifiedResults(data) {
        console.log('Displaying simplified results:', data);
        if (resultsArea) {
            let htmlContent = '<h3>🌾 Your Personalized Krishi-Veda Advice:</h3>';

            if (data.soil_wellness !== undefined) {
                htmlContent += `<p><strong>Overall Soil Health:</strong> ${data.soil_wellness.toFixed(1)}/100. `; // Assuming soil_wellness is a number
                if (data.soil_wellness > 75) {
                    htmlContent += 'Your soil is thriving! Excellent foundation for growth. 🌱</p>';
                } else if (data.soil_wellness > 50) {
                    htmlContent += 'Your soil health is moderate. Good for many crops, but gentle improvements can boost yields. 🌻</p>';
                } else {
                    htmlContent += 'Your soil needs attention. Focus on enriching it for better future harvests. 🚜</p>';
                }
            }

            if (data.ph_recommendation) { // Assuming backend returns a string like 'Add Lime: 250 kg/ha' or 'pH is balanced'
                htmlContent += `<p><strong>pH Balance:</strong> ${data.ph_recommendation}</p>`;
            } else {
                 // Fallback if ph_recommendation is not directly provided but ph_input is available
                const phVal = parseFloat(phInput.value);
                if (!isNaN(phVal)) {
                    if (phVal < 6.0) htmlContent += '<p><strong>pH Balance:</strong> Your soil is a bit acidic. Consider adding liming agents.</p>';
                    else if (phVal > 7.0) htmlContent += '<p><strong>pH Balance:</strong> Your soil is a bit alkaline. Consider adding organic matter or sulfur.</p>';
                    else htmlContent += '<p><strong>pH Balance:</strong> Your soil pH is well-balanced for most crops.</p>';
                }
            }

            if (data.npk_status) { // Assuming backend returns a string like 'Good (32.0 ppm)'
                htmlContent += `<p><strong>Nutrient Levels (N-P-K):</strong> ${data.npk_status}</p>`;
            } else {
                // Fallback for NPK based on input values
                const nVal = parseFloat(nInput.value);
                const pVal = parseFloat(pInput.value);
                const kVal = parseFloat(kInput.value);

                let npkAdvice = [];
                if (!isNaN(nVal) && nVal < 30) npkAdvice.push('Nitrogen is low');
                if (!isNaN(pVal) && pVal < 25) npkAdvice.push('Phosphorus is low');
                if (!isNaN(kVal) && kVal < 35) npkAdvice.push('Potassium is low');

                if (npkAdvice.length > 0) {
                    htmlContent += `<p><strong>Nutrient Levels:</strong> ${npkAdvice.join(', ')}. Consider appropriate fertilization.</p>`;
                } else {
                    htmlContent += '<p><strong>Nutrient Levels:</strong> Your NPK levels appear balanced.</p>';
                }
            }

            htmlContent += '<p>For detailed recommendations, please consult a local agricultural expert.</p>';

            resultsArea.innerHTML = htmlContent;
            resultsArea.style.display = 'block';
        }
    }

    // Initial calls (example)
    showWelcomeScreen();
    // applyFarmerUIMode(true); // Example: start in farmer-friendly mode if desired

    // Example of how you might trigger loading/results (these would typically be hooked to API calls)
    // For a Gradio app, this might involve listening to events or calling a Python function via Gradio's client-side JS.
    // showLoadingMessage('Analyzing soil data using Vedic intelligence');
    // setTimeout(() => {
    //     hideLoadingMessage();
    //     // Simulate receiving data from the backend
    //     displaySimplifiedResults({
    //         soil_wellness: 68.5,
    //         ph_recommendation: 'pH is balanced (6.5)',
    //         npk_status: 'Nitrogen: Good (32.0 ppm), Phosphorus: Good (26.0 ppm), Potassium: Excellent (41.0 ppm)'
    //     });
    // }, 3000);
});

// Basic CSS for spinner and large button (you'd typically put this in a .css file)
// <style>
// .spinner {
//     border: 4px solid rgba(0, 0, 0, 0.1);
//     border-left-color: #7983ff;
//     border-radius: 50%;
//     width: 20px;
//     height: 20px;
//     animation: spin 1s linear infinite;
//     display: inline-block;
//     vertical-align: middle;
//     margin-right: 10px;
// }
// @keyframes spin {
//     to { transform: rotate(360deg); }
// }
// .farmer-friendly-ui button.large-button {
//     padding: 15px 30px;
//     font-size: 1.2em;
//     border-radius: 8px;
//     background-color: #4CAF50; /* Green */
//     color: white;
//     border: none;
//     cursor: pointer;
// }
// .farmer-friendly-ui button.large-button:hover {
//     background-color: #45a049;
// }
// #loading-status {
//     display: flex;
//     align-items: center;
//     justify-content: center;
//     padding: 10px;
//     background-color: #e0f7fa;
//     color: #00796b;
//     border-radius: 5px;
//     margin-top: 15px;
//     display: none; /* Hidden by default */
// }
// #results-output {
//     padding: 15px;
//     border: 1px solid #c8e6c9;
//     border-radius: 5px;
//     margin-top: 20px;
//     background-color: #f1f8e9;
//     color: #333;
//     display: none; /* Hidden by default */
// }
// </style>
