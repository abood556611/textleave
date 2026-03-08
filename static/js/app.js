// Global variables
let currentVideoId = null;
let progressInterval = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    setupEventListeners();
});

function initializeForm() {
    // Calculate initial video info
    calculateVideoInfo(10);
}

function setupEventListeners() {
    // Duration buttons
    document.querySelectorAll('[data-duration]').forEach(btn => {
        btn.addEventListener('click', function() {
            setActiveButton(this, '[data-duration]');
            const duration = parseInt(this.dataset.duration);
            document.getElementById('duration').value = duration;
            calculateVideoInfo(duration);
        });
    });

    // FPS buttons
    document.querySelectorAll('[data-fps]').forEach(btn => {
        btn.addEventListener('click', function() {
            setActiveButton(this, '[data-fps]');
            document.getElementById('fps').value = this.dataset.fps;
        });
    });

    // Resolution buttons
    document.querySelectorAll('[data-resolution]').forEach(btn => {
        btn.addEventListener('click', function() {
            setActiveButton(this, '[data-resolution]');
            document.getElementById('resolution').value = this.dataset.resolution;
        });
    });

    // File upload
    document.getElementById('audioFile').addEventListener('change', function(e) {
        const fileName = e.target.files[0]?.name || 'اختر ملف صوتي';
        document.getElementById('fileName').textContent = fileName;
    });

    // Form submission
    document.getElementById('videoForm').addEventListener('submit', handleFormSubmit);
}

function setActiveButton(button, selector) {
    document.querySelectorAll(selector).forEach(btn => {
        btn.classList.remove('active');
    });
    button.classList.add('active');
}

async function calculateVideoInfo(duration) {
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ duration })
        });

        const data = await response.json();
        document.getElementById('pageCount').textContent = data.num_pages;
    } catch (error) {
        console.error('Error calculating video info:', error);
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();

    // Disable form
    const generateBtn = document.getElementById('generateBtn');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري التوليد...';

    // Hide download container if visible
    document.getElementById('downloadContainer').style.display = 'none';

    // Prepare form data
    const formData = new FormData(e.target);

    try {
        // Start video generation
        const response = await fetch('/api/generate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'فشل توليد الفيديو');
        }

        const data = await response.json();
        currentVideoId = data.video_id;

        // Show progress container
        document.getElementById('progressContainer').style.display = 'block';

        // Start polling for progress
        startProgressPolling();

    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ: ' + error.message);
        resetForm();
    }
}

function startProgressPolling() {
    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/progress/${currentVideoId}`);
            const data = await response.json();

            updateProgress(data.progress, data.status);

            if (data.status === 'complete') {
                stopProgressPolling();
                showDownloadButton();
            } else if (data.status === 'error') {
                stopProgressPolling();
                alert('حدث خطأ أثناء توليد الفيديو: ' + (data.error || 'خطأ غير معروف'));
                resetForm();
            }

        } catch (error) {
            console.error('Error polling progress:', error);
        }
    }, 1000); // Poll every second
}

function stopProgressPolling() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

function updateProgress(progress, status) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    progressFill.style.width = progress + '%';
    progressText.textContent = status;
}

function showDownloadButton() {
    document.getElementById('progressContainer').style.display = 'none';
    document.getElementById('downloadContainer').style.display = 'block';

    // Setup download button
    document.getElementById('downloadBtn').onclick = function() {
        window.location.href = `/api/download/${currentVideoId}`;
    };
}

function resetForm() {
    const generateBtn = document.getElementById('generateBtn');
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<i class="fas fa-magic"></i> توليد الفيديو';
    
    document.getElementById('progressContainer').style.display = 'none';
    document.getElementById('downloadContainer').style.display = 'none';
}

// Subscription functions
async function subscribePlan(plan) {
    try {
        const response = await fetch('/api/subscription/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ plan })
        });

        const data = await response.json();

        if (data.payment_url) {
            // In production, redirect to OxaPay payment page
            alert(`سيتم توجيهك إلى صفحة الدفع. المبلغ: $${data.amount}`);
            // window.location.href = data.payment_url;
        }

    } catch (error) {
        console.error('Error creating subscription:', error);
        alert('حدث خطأ في إنشاء الاشتراك');
    }
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href.startsWith('#')) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Handle support button
document.querySelector('.btn-support').addEventListener('click', function(e) {
    e.preventDefault();
    const whatsappNumber = this.href.match(/\d+/)[0];
    const message = encodeURIComponent('مرحباً، أرغب في الاستفسار عن خدمة TextLeaf');
    window.open(`https://wa.me/${whatsappNumber}?text=${message}`, '_blank');
});
