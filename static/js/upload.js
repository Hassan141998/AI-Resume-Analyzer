/**
 * Upload Form Handler with Drag-and-Drop
 * Handles file upload, validation, and loading animation
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analysisForm');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('resumeFile');
    const fileNameDisplay = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const charCount = document.querySelector('.char-count');
    const jobDescTextarea = document.getElementById('jobDescription');
    const submitBtn = form?.querySelector('button[type="submit"]');
    const loadingOverlay = document.getElementById('loadingOverlay');

    if (!form) {
        console.error('Form not found! Make sure form has id="analysisForm"');
        return;
    }

    // ── Drag and Drop ──────────────────────────────────────────────────────
    if (dropZone && fileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        }, false);

        dropZone.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    // ── File Selection Handler ────────────────────────────────────────────
    function handleFileSelect(file) {
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        const maxSize = 10 * 1024 * 1024; // 10 MB

        if (!validTypes.includes(file.type)) {
            alert('Please upload a PDF or DOCX file only.');
            fileInput.value = '';
            return;
        }

        if (file.size > maxSize) {
            alert('File size must be less than 10 MB.');
            fileInput.value = '';
            return;
        }

        // Display file info
        if (fileNameDisplay) {
            fileNameDisplay.textContent = file.name;
            fileNameDisplay.classList.add('show');
        }
        if (fileSize) {
            fileSize.textContent = formatFileSize(file.size);
            fileSize.classList.add('show');
        }

        // Simulate upload progress (visual feedback only)
        simulateProgress();
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    function simulateProgress() {
        const progressBar = document.querySelector('.upload-progress');
        if (!progressBar) return;

        progressBar.style.display = 'block';
        let width = 0;
        const interval = setInterval(() => {
            if (width >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    progressBar.style.display = 'none';
                    progressBar.querySelector('.progress-fill').style.width = '0%';
                }, 500);
            } else {
                width += 10;
                progressBar.querySelector('.progress-fill').style.width = width + '%';
            }
        }, 50);
    }

    // ── Character Counter ─────────────────────────────────────────────────
    if (jobDescTextarea && charCount) {
        jobDescTextarea.addEventListener('input', () => {
            const count = jobDescTextarea.value.length;
            charCount.textContent = `${count.toLocaleString()} characters`;
        });
    }

    // ── Form Submission ───────────────────────────────────────────────────
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('Form submitted - starting validation...');

        // Validate
        if (!fileInput.files || fileInput.files.length === 0) {
            alert('Please select a resume file.');
            return;
        }

        if (!jobDescTextarea.value.trim()) {
            alert('Please enter a job description.');
            jobDescTextarea.focus();
            return;
        }

        if (jobDescTextarea.value.trim().length < 50) {
            alert('Job description is too short. Please provide more details (at least 50 characters).');
            jobDescTextarea.focus();
            return;
        }

        console.log('Validation passed - showing loading overlay...');

        // Show loading overlay
        if (loadingOverlay) {
            loadingOverlay.classList.add('active');
        }

        // Disable submit button
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Analyzing...';
        }

        // Create FormData
        const formData = new FormData(form);
        
        console.log('Sending request to /upload...');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            console.log('Response status:', response.status);

            if (response.redirected) {
                console.log('Redirecting to:', response.url);
                window.location.href = response.url;
                return;
            }

            if (response.ok) {
                const data = await response.text();
                console.log('Response received, checking for redirect...');
                
                // Check if response contains a redirect
                if (data.includes('/result/')) {
                    const uidMatch = data.match(/\/result\/([a-f0-9-]+)/);
                    if (uidMatch) {
                        window.location.href = `/result/${uidMatch[1]}`;
                        return;
                    }
                }

                // If no redirect found, the backend should have redirected us
                console.log('No redirect found in response');
            } else {
                const errorText = await response.text();
                console.error('Server error:', errorText);
                alert('An error occurred during analysis. Please try again.');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('Network error. Please check your connection and try again.');
        } finally {
            // Hide loading and re-enable button
            if (loadingOverlay) {
                loadingOverlay.classList.remove('active');
            }
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Analyze Resume';
            }
        }
    });

    console.log('Upload.js loaded successfully!');
});
