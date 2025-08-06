// Email Compose Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeComposeForm();
});

function initializeComposeForm() {
    const generateBtn = document.getElementById('generateReplyBtn');
    const summarizeBtn = document.getElementById('summarizeEmailBtn');
    const originalEmailInput = document.getElementById('originalEmail');
    const contextInput = document.getElementById('context');
    const toneSelect = document.getElementById('emailTone');
    const modelSelect = document.getElementById('aiModel');
    const customInstructionsInput = document.getElementById('customInstructions');
    const subjectInput = document.getElementById('emailSubject');
    const bodyInput = document.getElementById('emailBody');
    const aiResponseCard = document.getElementById('aiResponseCard');
    const aiGeneratedContent = document.getElementById('aiGeneratedContent');
    const generationTime = document.getElementById('generationTime');

    if (generateBtn) {
        generateBtn.addEventListener('click', async function(e) {
            e.preventDefault();

            const originalEmail = originalEmailInput?.value || '';
            const context = contextInput?.value || '';
            const tone = toneSelect?.value || 'professional';
            const model = modelSelect?.value || 'auto';
            const customInstructions = customInstructionsInput?.value || '';

            if (!originalEmail.trim()) {
                if (window.appUtils) {
                    window.appUtils.showToast('Please enter the original email first', 'warning');
                } else {
                    alert('Please enter the original email first');
                }
                return;
            }

            // Show loading state
            generateBtn.disabled = true;
            const originalText = generateBtn.innerHTML;
            generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';

            showLoadingOverlay('Generating AI response...');

            try {
                const response = await fetch('/api/generate-reply', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        original_email: originalEmail,
                        context: context,
                        tone: tone,
                        model: model,
                        custom_instructions: customInstructions
                    })
                });

                const result = await response.json();
                console.log('AI Generation Result:', result);
                console.log('Subject:', result.subject);
                console.log('Body:', result.body);

                if (result.success) {
                    // Show AI response card
                    if (aiResponseCard) {
                        aiResponseCard.classList.remove('d-none');
                    }

                    // Display generated content with better handling
                    if (aiGeneratedContent) {
                        let content = '';

                        // Handle different response formats
                        if (result.subject && result.subject.trim() && result.subject !== 'Re: Email Reply') {
                            content += `Subject: ${result.subject}\n\n`;
                        }

                        if (result.body && result.body.trim()) {
                            content += result.body.trim();
                        } else if (result.content && result.content.trim()) {
                            content += result.content.trim();
                        } else {
                            content += 'AI generated a response, but the content appears to be empty. Please try again.';
                        }

                        console.log('Setting content to element:', aiGeneratedContent);
                        console.log('Content being set:', content);

                        if (aiGeneratedContent) {
                            aiGeneratedContent.textContent = content;
                            aiGeneratedContent.style.whiteSpace = 'pre-wrap';

                            // Force visibility test
                            console.log('Element after setting content:', aiGeneratedContent.textContent);
                            console.log('Element visibility:', window.getComputedStyle(aiGeneratedContent).display);
                        }
                    }

                    // Show generation info
                    if (generationTime) {
                        const modelUsed = result.model_used || model || 'AI';
                        const timeMs = result.generation_time_ms || 1500;
                        const timeDisplay = isNaN(timeMs) ? '1.5s' : `${(timeMs / 1000).toFixed(1)}s`;
                        const modelName = modelUsed === 'qwen-4-turbo' ? 'Qwen-4' : modelUsed;
                        generationTime.textContent = `Generated in ${timeDisplay} using ${modelName}`;
                    }

                    if (window.appUtils) {
                        window.appUtils.showToast('Email reply generated successfully!', 'success');
                    }
                } else {
                    const errorMsg = result.error || 'Failed to generate reply';
                    console.error('AI Generation Error:', errorMsg);
                    if (window.appUtils) {
                        window.appUtils.showToast(errorMsg, 'error');
                    } else {
                        alert('Error: ' + errorMsg);
                    }
                }
            } catch (error) {
                console.error('Error generating reply:', error);
                if (window.appUtils) {
                    window.appUtils.showToast('Network error occurred', 'error');
                } else {
                    alert('Network error occurred');
                }
            } finally {
                // Reset button
                generateBtn.disabled = false;
                generateBtn.innerHTML = originalText;
                hideLoadingOverlay();

                // Refresh feather icons
                if (typeof feather !== 'undefined') {
                    feather.replace();
                }
            }
        });
    }

    // Use AI Response button
    const useResponseBtn = document.getElementById('useResponseBtn');
    if (useResponseBtn) {
        useResponseBtn.addEventListener('click', function() {
            const aiContent = aiGeneratedContent?.textContent || '';
            if (!aiContent) {
                if (window.appUtils) {
                    window.appUtils.showToast('No AI content to use', 'warning');
                } else {
                    alert('No AI content to use');
                }
                return;
            }

            const lines = aiContent.split('\n');
            let subject = '';
            let body = '';
            let isBody = false;

            lines.forEach(line => {
                if (line.startsWith('Subject:')) {
                    subject = line.replace('Subject:', '').trim();
                } else if (isBody || (!line.startsWith('Subject:') && line.trim() !== '')) {
                    if (!line.startsWith('Subject:')) {
                        isBody = true;
                        body += line + '\n';
                    }
                }
            });

            if (subject && subjectInput) {
                subjectInput.value = subject;
            }
            if (body && bodyInput) {
                bodyInput.value = body.trim();
                // Auto-resize if it's a textarea
                if (bodyInput.tagName === 'TEXTAREA') {
                    if (window.appUtils) {
                        window.appUtils.autoResizeTextarea(bodyInput);
                    }
                }
            }

            if (aiResponseCard) {
                aiResponseCard.classList.add('d-none');
            }

            if (window.appUtils) {
                window.appUtils.showToast('AI response applied to email', 'success');
            }
        });
    }

    // Initialize summarize button functionality
    if (summarizeBtn) {
        summarizeBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            await summarizeEmail();
        });
    }

    // Initialize close summary button
    const closeSummaryBtn = document.getElementById('closeSummaryBtn');
    if (closeSummaryBtn) {
        closeSummaryBtn.addEventListener('click', function() {
            const summaryCard = document.getElementById('emailSummaryCard');
            if (summaryCard) {
                summaryCard.classList.add('d-none');
            }
        });
    }
}

// Email summarization function
async function summarizeEmail() {
    const originalEmailInput = document.getElementById('originalEmail');
    const summarizeBtn = document.getElementById('summarizeEmailBtn');
    const summaryCard = document.getElementById('emailSummaryCard');
    const summaryContent = document.getElementById('emailSummaryContent');
    const summaryModel = document.getElementById('summaryModel');

    if (!originalEmailInput || !originalEmailInput.value.trim()) {
        if (window.appUtils && window.appUtils.showToast) {
            window.appUtils.showToast('Please paste the original email content first', 'warning');
        } else {
            alert('Please paste the original email content first');
        }
        return;
    }

    const emailContent = originalEmailInput.value.trim();
    
    if (emailContent.length < 10) {
        if (window.appUtils && window.appUtils.showToast) {
            window.appUtils.showToast('Email content is too short to summarize', 'warning');
        } else {
            alert('Email content is too short to summarize');
        }
        return;
    }

    // Show loading state
    if (summarizeBtn) {
        summarizeBtn.disabled = true;
        const originalText = summarizeBtn.innerHTML;
        summarizeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Processing...';
        
        try {
            const response = await fetch('/api/summarize-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    email_content: emailContent
                })
            });

            if (!response.ok) {
                if (response.status === 302 || response.status === 401) {
                    throw new Error('Please log in to use the summarization feature');
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                // Display the summary
                if (summaryContent) {
                    summaryContent.innerHTML = result.summary;
                }
                if (summaryModel) {
                    const processingTime = result.processing_time_ms ? ` • ${result.processing_time_ms}ms` : '';
                    summaryModel.textContent = `Generated by ${result.model_used || 'AI'}${processingTime}`;
                }
                if (summaryCard) {
                    summaryCard.classList.remove('d-none');
                }

                // Replace feather icons
                if (typeof feather !== 'undefined') {
                    feather.replace();
                }

                if (window.appUtils && window.appUtils.showToast) {
                    window.appUtils.showToast(`Email summarized successfully using ${result.model_used || 'AI'}`, 'success');
                } else if (window.showToast) {
                    window.showToast(`Email summarized successfully using ${result.model_used || 'AI'}`, 'success');
                }
            } else {
                throw new Error(result.error || 'Failed to summarize email');
            }

        } catch (error) {
            console.error('Error summarizing email:', error);
            if (window.appUtils && window.appUtils.showToast) {
                window.appUtils.showToast('Failed to summarize email: ' + error.message, 'error');
            } else if (window.showToast) {
                window.showToast('Failed to summarize email: ' + error.message, 'error');
            } else {
                alert('Failed to summarize email: ' + error.message);
            }
        } finally {
            // Restore button state
            summarizeBtn.disabled = false;
            summarizeBtn.innerHTML = originalText;
        }
    }
}

// Export for global use
window.composeUtils = {
    initializeComposeForm,
    summarizeEmail
};