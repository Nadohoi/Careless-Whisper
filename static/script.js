document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const modelSelect = document.getElementById('model-select');
    const deviceSelect = document.getElementById('device-select');
    const fileInput = document.getElementById('file-input');
    const selectedFileLabel = document.getElementById('selected-file-label');
    const transformButton = document.getElementById('transform-button');
    const outputText = document.getElementById('output-text');
    const downloadContainer = document.getElementById('download-container');
    const downloadLink = document.getElementById('download-link');
    
    // Event listeners
    fileInput.addEventListener('change', handleFileSelection);
    transformButton.addEventListener('click', handleTransform);
    
    // Check GPU availability and update device options accordingly
    checkGpuAvailability();
    
    function checkGpuAvailability() {
        // This is a frontend check that will be complemented by a backend check
        // We'll leave GPU option available but the backend will fallback to CPU if needed
        if (navigator.gpu === undefined) {
            // If WebGPU is not available, we'll assume no GPU
            const gpuOption = Array.from(deviceSelect.options).find(option => option.value === 'gpu');
            if (gpuOption) {
                gpuOption.disabled = true;
                gpuOption.text = 'GPU (not available)';
            }
            deviceSelect.value = 'cpu';
        }
    }
    
    function handleFileSelection(event) {
        const file = event.target.files[0];
        if (file) {
            selectedFileLabel.textContent = `Selected: ${file.name}`;
        } else {
            selectedFileLabel.textContent = 'No file selected';
        }
    }
    
    async function handleTransform() {
        if (!fileInput.files.length) {
            alert('Please select a file first.');
            return;
        }
        
        // Add loading state
        document.body.classList.add('loading');
        transformButton.disabled = true;
        outputText.value = 'Processing... Please wait.';
        downloadContainer.style.display = 'none';
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('model', modelSelect.value);
        formData.append('device', deviceSelect.value);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                outputText.value = `Error: ${data.error}`;
                return;
            }
            
            // Display results
            let transcription = `Detected language '${data.language}' with probability ${data.language_probability}\n\n`;
            
            data.segments.forEach(segment => {
                transcription += `${segment.id}\n${segment.start} --> ${segment.end}\n${segment.text}\n\n`;
            });
            
            outputText.value = transcription;
            
            // Show download link with session ID
            const downloadUrl = `/download/${data.session_id}`;
            downloadLink.href = downloadUrl;
            downloadLink.download = data.srt_filename;
            downloadContainer.style.display = 'block';
            
            // Handle download via click (in case the link is opened in a new tab)
            downloadLink.onclick = function(e) {
                e.preventDefault();
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = data.srt_filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                return false;
            };
            
        } catch (error) {
            outputText.value = `Error: ${error.message}`;
        } finally {
            // Remove loading state
            document.body.classList.remove('loading');
            transformButton.disabled = false;
        }
    }
});
