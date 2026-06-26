// ─── Mock Data ────────────────────────────────────────────────────────────────
const categories = [
    { id: 1, name: 'Plumbing', icon: '<path d="M2 12h20"/><path d="M20 12v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8"/><path d="m4 8 16-4"/><path d="m8 2 8 2"/>' },
    { id: 2, name: 'Electrical', icon: '<path d="m13 2-2 2.5-3 3 3 2.5-1 3.5 3-3.5 1-3.5-3-2.5 2-2z"/><path d="M11 13v8"/><path d="M15 13v8"/><path d="M7 13v8"/>' },
    { id: 3, name: 'Carpentry', icon: '<path d="M14.5 17.5 3 6V3h3l11.5 11.5"/><path d="m13 19 6-6"/><path d="m16 22 5-5"/><path d="m19 22 3-3"/>' },
    { id: 4, name: 'Cleaning', icon: '<path d="M3 3v18h18"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>' },
    { id: 5, name: 'Painting', icon: '<path d="m18 10-6-6-8 8 6 6z"/><path d="M12 16v5"/><path d="M16 12l4 4"/>' },
    { id: 6, name: 'HVAC', icon: '<path d="M12 2v20"/><path d="M12 12A10 10 0 0 0 2 22"/><path d="M12 12A10 10 0 0 1 22 22"/>' }
];

const pros = [
    { id: 1, name: 'Michael Davis', job: 'Master Plumber', rating: 4.9, reviews: 124, price: '$85', image: 'https://images.unsplash.com/photo-1540569014015-19a7be504e3a?auto=format&fit=crop&w=256&q=80', location: 'Visakhapatnam, AP', experience: '12 Years', completed: 450, bio: 'Licensed master plumber with over a decade of experience. Specializes in emergency repairs, pipe installations, and water heater maintenance.' },
    { id: 2, name: 'Sarah Jenkins', job: 'Certified Electrician', rating: 5.0, reviews: 89, price: '$95', image: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=256&q=80', location: 'Vijayawada, AP', experience: '8 Years', completed: 320, bio: 'Expert in residential wiring, panel upgrades, and smart home installations. Safety is my number one priority.' },
    { id: 3, name: 'David Rodriguez', job: 'Pro Carpenter', rating: 4.8, reviews: 215, price: '$70', image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=256&q=80', location: 'Guntur, AP', experience: '15 Years', completed: 800, bio: 'Custom furniture, framing, and detailed finish carpentry. I bring precision and craftsmanship to every project.' },
    { id: 4, name: 'Emily Chen', job: 'Deep Cleaning Specialist', rating: 4.9, reviews: 340, price: '$45', image: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=256&q=80', location: 'Tirupati, AP', experience: '5 Years', completed: 1200, bio: 'Thorough, eco-friendly cleaning services for residential and commercial spaces. Satisfaction guaranteed.' }
];

// ─── SVG Helpers ──────────────────────────────────────────────────────────────
const getSvgIcon = (path, w = 24, h = 24) =>
    `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${path}</svg>`;

const starIcon     = `<path d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>`;
const locationIcon = `<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>`;
const checkIcon    = `<polyline points="20 6 9 17 4 12"/>`;

// ─── Toast Notification System ────────────────────────────────────────────────
function showToast(message, type = 'info', duration = 4000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position:fixed;top:1.5rem;right:1.5rem;z-index:9999;display:flex;flex-direction:column;gap:0.75rem;';
        document.body.appendChild(container);
    }

    const colors = {
        success: { bg: 'rgba(16,185,129,0.15)', border: '#10b981', icon: '✓' },
        error:   { bg: 'rgba(239,68,68,0.15)',  border: '#ef4444', icon: '✕' },
        info:    { bg: 'rgba(59,130,246,0.15)', border: '#3b82f6', icon: 'ℹ' },
        warning: { bg: 'rgba(245,158,11,0.15)', border: '#f59e0b', icon: '⚠' },
    };
    const c = colors[type] || colors.info;

    const toast = document.createElement('div');
    toast.style.cssText = `background:${c.bg};border:1px solid ${c.border};border-left:4px solid ${c.border};border-radius:10px;padding:0.875rem 1.25rem;color:white;font-size:0.875rem;display:flex;align-items:center;gap:0.75rem;min-width:280px;max-width:380px;backdrop-filter:blur(12px);box-shadow:0 8px 32px rgba(0,0,0,0.4);transform:translateX(120%);transition:transform 0.35s cubic-bezier(0.34,1.56,0.64,1);`;
    toast.innerHTML = `<span style="font-size:1rem;flex-shrink:0;">${c.icon}</span><span>${message}</span>`;
    container.appendChild(toast);

    requestAnimationFrame(() => { toast.style.transform = 'translateX(0)'; });

    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        setTimeout(() => toast.remove(), 400);
    }, duration);
}

// ─── DOM Elements ─────────────────────────────────────────────────────────────
const categoriesGrid = document.getElementById('categories-grid');
const prosGrid       = document.getElementById('pros-grid');
const modalOverlay   = document.getElementById('worker-modal');
const closeModalBtn  = document.getElementById('close-modal');
const modalBody      = document.getElementById('modal-body');

// ─── Render Categories ────────────────────────────────────────────────────────
function renderCategories() {
    categories.forEach(cat => {
        const card = document.createElement('div');
        card.className = 'category-card glass-card';
        card.innerHTML = `<div class="category-icon">${getSvgIcon(cat.icon, 32, 32)}</div><h3>${cat.name}</h3>`;
        card.addEventListener('click', () => {
            document.getElementById('search-input').value = cat.name + ' repair';
            document.getElementById('professionals').scrollIntoView({ behavior: 'smooth' });
        });
        categoriesGrid.appendChild(card);
    });
}

// ─── Render Pros ──────────────────────────────────────────────────────────────
function renderPros() {
    pros.forEach(pro => {
        const card = document.createElement('div');
        card.className = 'pro-card glass-card';
        card.innerHTML = `
            <div class="pro-header">
                <img src="${pro.image}" alt="${pro.name}" class="pro-avatar">
                <div class="pro-info">
                    <h3>${pro.name}</h3>
                    <div class="pro-job">${pro.job}</div>
                    <div class="pro-rating">
                        ${getSvgIcon(starIcon, 16, 16).replace('stroke="currentColor"', 'fill="#f59e0b" stroke="none"')}
                        <span><strong>${pro.rating}</strong> (${pro.reviews} reviews)</span>
                    </div>
                </div>
            </div>
            <div class="pro-details">
                <div class="detail-item">${getSvgIcon(locationIcon, 16, 16)}<span>${pro.location}</span></div>
                <div class="detail-item">${getSvgIcon(checkIcon, 16, 16)}<span>${pro.completed} Jobs Completed</span></div>
            </div>
            <div class="pro-footer">
                <div class="pro-price">${pro.price}<span>/hr</span></div>
                <button class="btn btn-primary btn-book" data-id="${pro.id}">View Profile</button>
            </div>`;
        prosGrid.appendChild(card);
    });

    document.querySelectorAll('.btn-book').forEach(btn => {
        btn.addEventListener('click', e => openModal(parseInt(e.target.getAttribute('data-id'))));
    });
}

// ─── Worker Profile Modal ─────────────────────────────────────────────────────
function openModal(proId) {
    const pro = pros.find(p => p.id === proId);
    if (!pro) return;

    modalBody.innerHTML = `
        <div style="display:flex;gap:1.5rem;margin-bottom:2rem;align-items:center;">
            <img src="${pro.image}" alt="${pro.name}" style="width:100px;height:100px;border-radius:50%;object-fit:cover;border:3px solid var(--border-color);">
            <div>
                <h2 style="margin-bottom:0.25rem;">${pro.name}</h2>
                <div style="color:var(--accent-primary);font-weight:500;margin-bottom:0.5rem;">${pro.job}</div>
                <div style="display:flex;gap:1rem;color:var(--text-secondary);font-size:0.875rem;">
                    <span style="display:flex;align-items:center;gap:0.25rem;">${getSvgIcon(starIcon,16,16).replace('stroke="currentColor"','fill="#f59e0b" stroke="none"')} ${pro.rating} (${pro.reviews})</span>
                    <span style="display:flex;align-items:center;gap:0.25rem;">${getSvgIcon(locationIcon,16,16)} ${pro.location}</span>
                </div>
            </div>
        </div>
        <div style="background:rgba(255,255,255,0.05);padding:1.5rem;border-radius:12px;margin-bottom:2rem;">
            <div style="margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid var(--border-color);">
                <h3 style="margin-bottom:0.5rem;color:var(--accent-secondary);display:flex;align-items:center;gap:0.5rem;">✨ AI Review Summary</h3>
                <p id="ai-review-summary-text" style="font-size:0.875rem;color:var(--text-secondary);line-height:1.5;">Generating real-time review summary...</p>
            </div>
            <h3 style="margin-bottom:1rem;">About</h3>
            <p>${pro.bio}</p>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:2rem;">
            <div class="glass-card" style="padding:1rem;text-align:center;">
                <div style="color:var(--text-secondary);font-size:0.875rem;margin-bottom:0.5rem;">Experience</div>
                <div style="font-size:1.25rem;font-weight:600;color:white;">${pro.experience}</div>
            </div>
            <div class="glass-card" style="padding:1rem;text-align:center;">
                <div style="color:var(--text-secondary);font-size:0.875rem;margin-bottom:0.5rem;">Rate</div>
                <div style="font-size:1.25rem;font-weight:600;color:white;">${pro.price}/hr</div>
            </div>
        </div>
        <button class="btn btn-primary" id="open-booking-btn" style="width:100%;font-size:1.125rem;padding:1rem;">📅 Request to Book</button>`;

    modalOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Fetch AI review summary
    fetch('/api/review-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pro_name: pro.name, pro_job: pro.job })
    }).then(r => r.json()).then(data => {
        const el = document.getElementById('ai-review-summary-text');
        if (el && data.summary) el.innerText = data.summary;
    }).catch(() => {
        const el = document.getElementById('ai-review-summary-text');
        if (el) el.innerText = `Based on ${pro.reviews} reviews, customers consistently praise ${pro.name.split(' ')[0]} for high-quality work and punctuality.`;
    });

    // Booking button opens booking modal
    document.getElementById('open-booking-btn').addEventListener('click', () => {
        closeModal();
        openBookingModal(pro);
    });
}

function closeModal() {
    modalOverlay.classList.remove('active');
    document.body.style.overflow = 'auto';
}

closeModalBtn.addEventListener('click', closeModal);
modalOverlay.addEventListener('click', e => { if (e.target === modalOverlay) closeModal(); });

// ─── Booking Modal ────────────────────────────────────────────────────────────
function openBookingModal(pro) {
    // Create or reuse booking modal
    let bm = document.getElementById('booking-modal');
    if (!bm) {
        bm = document.createElement('div');
        bm.id = 'booking-modal';
        bm.className = 'modal-overlay';
        bm.innerHTML = `
            <div class="modal-content glass-card">
                <button class="close-modal" id="close-booking-modal">&times;</button>
                <div id="booking-modal-body"></div>
            </div>`;
        document.body.appendChild(bm);
        document.getElementById('close-booking-modal').addEventListener('click', () => {
            bm.classList.remove('active');
            document.body.style.overflow = 'auto';
        });
        bm.addEventListener('click', e => { if (e.target === bm) { bm.classList.remove('active'); document.body.style.overflow = 'auto'; } });
    }

    document.getElementById('booking-modal-body').innerHTML = `
        <h2 style="margin-bottom:0.25rem;">Book ${pro.name}</h2>
        <p style="margin-bottom:2rem;">${pro.job} · ${pro.price}/hr</p>
        <div style="margin-bottom:1.5rem;">
            <label style="display:block;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;color:var(--text-secondary);margin-bottom:0.5rem;">Service Needed</label>
            <input type="text" id="booking-service" placeholder="e.g. Fix leaking pipe under sink" style="width:100%;background:rgba(0,0,0,0.2);border:1px solid var(--border-color);border-radius:8px;padding:0.875rem 1rem;color:white;font-family:inherit;outline:none;">
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem;">
            <div>
                <label style="display:block;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;color:var(--text-secondary);margin-bottom:0.5rem;">Preferred Date</label>
                <input type="date" id="booking-date" style="width:100%;background:rgba(0,0,0,0.2);border:1px solid var(--border-color);border-radius:8px;padding:0.875rem 1rem;color:white;font-family:inherit;outline:none;">
            </div>
            <div>
                <label style="display:block;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;color:var(--text-secondary);margin-bottom:0.5rem;">Preferred Time</label>
                <select id="booking-time" style="width:100%;background:rgba(15,23,42,0.9);border:1px solid var(--border-color);border-radius:8px;padding:0.875rem 1rem;color:white;font-family:inherit;outline:none;">
                    <option>08:00 AM</option><option>10:00 AM</option><option>12:00 PM</option>
                    <option>02:00 PM</option><option>04:00 PM</option><option>06:00 PM</option>
                </select>
            </div>
        </div>
        <button id="confirm-booking-btn" class="btn btn-primary" style="width:100%;padding:1rem;font-size:1rem;">Confirm Booking Request</button>`;

    bm.classList.add('active');
    document.body.style.overflow = 'hidden';

    document.getElementById('confirm-booking-btn').addEventListener('click', () => {
        const service = document.getElementById('booking-service').value.trim();
        const date    = document.getElementById('booking-date').value;
        const time    = document.getElementById('booking-time').value;
        if (!service || !date) { showToast('Please fill in the service and date.', 'warning'); return; }
        bm.classList.remove('active');
        document.body.style.overflow = 'auto';
        showToast(`✅ Booking request sent to ${pro.name} for ${date} at ${time}!`, 'success', 5000);
    });
}

// ─── AI Smart Search (with toast instead of alert) ────────────────────────────
const smartSearchBtn = document.getElementById('smart-search-btn');
const searchInput    = document.getElementById('search-input');
const aiSearchGroup  = document.querySelector('.ai-search-group');

smartSearchBtn.addEventListener('click', async () => {
    const query = searchInput.value.trim();
    if (!query) { showToast('Please describe your problem first.', 'warning'); return; }

    smartSearchBtn.textContent = 'AI Thinking...';
    smartSearchBtn.style.opacity = '0.7';
    aiSearchGroup.classList.add('thinking');

    try {
        const res  = await fetch('/api/smart-match', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query }) });
        const data = await res.json();

        smartSearchBtn.textContent = 'Find Pros';
        smartSearchBtn.style.opacity = '1';
        aiSearchGroup.classList.remove('thinking');

        if (data.category) {
            showToast(`🔍 AI matched your issue to: <strong>${data.category}</strong>. Showing best pros!`, 'success');
            document.getElementById('professionals').scrollIntoView({ behavior: 'smooth' });

            const firstCard = prosGrid.firstElementChild;
            firstCard.style.transform = 'scale(1.05)';
            firstCard.style.boxShadow = '0 0 20px rgba(139,92,246,0.5)';
            firstCard.style.borderColor = 'var(--accent-secondary)';
            setTimeout(() => { firstCard.style.transform = ''; firstCard.style.boxShadow = ''; firstCard.style.borderColor = ''; }, 3000);
        }
    } catch (err) {
        console.error(err);
        smartSearchBtn.textContent = 'Find Pros';
        smartSearchBtn.style.opacity = '1';
        aiSearchGroup.classList.remove('thinking');
        showToast('Could not connect to AI backend. Is the server running?', 'error');
    }
});

// ─── AI Price Estimator ───────────────────────────────────────────────────────
const aiEstimateBtn       = document.getElementById('ai-estimate-btn');
const estimateModal       = document.getElementById('estimate-modal');
const closeEstimateModal  = document.getElementById('close-estimate-modal');
const uploadArea          = document.getElementById('upload-area');
const estimateFileInput   = document.getElementById('estimate-file-input');
const aiScannerContainer  = document.getElementById('ai-scanner-container');
const aiResult            = document.getElementById('ai-result');

aiEstimateBtn.addEventListener('click', () => {
    estimateModal.classList.add('active');
    document.body.style.overflow = 'hidden';
    uploadArea.style.display = 'block';
    aiScannerContainer.style.display = 'none';
    aiResult.style.display = 'none';
});
closeEstimateModal.addEventListener('click', () => { estimateModal.classList.remove('active'); document.body.style.overflow = 'auto'; });
uploadArea.addEventListener('click', () => estimateFileInput.click());

estimateFileInput.addEventListener('change', async e => {
    const file = e.target.files[0];
    if (!file) return;

    uploadArea.style.display = 'none';
    aiScannerContainer.style.display = 'block';
    aiScannerContainer.querySelector('.uploaded-img').src = URL.createObjectURL(file);

    const formData = new FormData();
    formData.append('image', file);

    try {
        const res = await fetch('/api/estimate', { method: 'POST', body: formData });
        if (!res.ok) throw new Error('API error');
        const data = await res.json();

        document.getElementById('ai-est-cost').innerText  = 'Estimated Cost: '  + data.estimated_cost;
        document.getElementById('ai-est-time').innerText  = 'Estimated Time: '  + data.estimated_time;
        document.getElementById('ai-est-issue').innerText = 'Detected: '        + data.detected_issue;
        aiScannerContainer.style.display = 'none';
        aiResult.style.display = 'block';
    } catch (err) {
        console.error(err);
        showToast('Failed to analyze image. Please ensure the backend is running.', 'error');
        uploadArea.style.display = 'block';
        aiScannerContainer.style.display = 'none';
    }
    estimateFileInput.value = '';
});

// ─── AI Bio Generator ─────────────────────────────────────────────────────────
const aiBioBtn           = document.getElementById('ai-bio-btn');
const bioModal           = document.getElementById('bio-modal');
const closeBioModal      = document.getElementById('close-bio-modal');
const generateBioBtn     = document.getElementById('generate-bio-btn');
const bioResultContainer = document.getElementById('bio-result-container');
const bioResultText      = document.getElementById('bio-result-text');

aiBioBtn.addEventListener('click', () => { bioModal.classList.add('active'); document.body.style.overflow = 'hidden'; bioResultContainer.style.display = 'none'; document.getElementById('bio-input').value = ''; });
closeBioModal.addEventListener('click', () => { bioModal.classList.remove('active'); document.body.style.overflow = 'auto'; });

generateBioBtn.addEventListener('click', async () => {
    const input = document.getElementById('bio-input').value.trim();
    if (!input) { showToast('Please enter some bullet points first.', 'warning'); return; }

    generateBioBtn.textContent = '✨ AI is writing...';
    generateBioBtn.disabled = true;

    try {
        const res  = await fetch('/api/generate-bio', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ points: input }) });
        const data = await res.json();
        generateBioBtn.textContent = 'Generate Bio';
        generateBioBtn.disabled = false;
        bioResultContainer.style.display = 'block';

        const text = data.text || 'Error generating bio.';
        bioResultText.innerHTML = '';
        let i = 0;
        const typing = setInterval(() => {
            if (i < text.length) { bioResultText.innerHTML += text.charAt(i); i++; }
            else clearInterval(typing);
        }, 15);

        // Copy to clipboard button
        const copyBtn = bioResultContainer.querySelector('button');
        if (copyBtn) {
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(text).then(() => showToast('Bio copied to clipboard!', 'success'));
            };
        }
    } catch (err) {
        console.error(err);
        generateBioBtn.textContent = 'Generate Bio';
        generateBioBtn.disabled = false;
        showToast('Error connecting to AI backend.', 'error');
    }
});

// ─── Smart Chatbot (with full conversation history) ───────────────────────────
const chatbotWidget  = document.getElementById('chatbot-widget');
const chatbotBtn     = document.getElementById('chatbot-btn');
const closeChat      = document.getElementById('close-chat');
const sendBtn        = document.getElementById('send-btn');
const chatInput      = document.getElementById('chat-input');
const chatMessages   = document.getElementById('chat-messages');
let conversationHistory = []; // Stores {role, text} pairs

chatbotBtn.addEventListener('click', () => chatbotWidget.classList.add('open'));
closeChat.addEventListener('click', () => chatbotWidget.classList.remove('open'));

function addMessage(text, role) {
    const msg = document.createElement('div');
    msg.className = `message ${role}-message`;
    msg.textContent = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const typing = document.createElement('div');
    typing.className = 'message ai-message typing-indicator';
    typing.id = 'typing-indicator';
    typing.innerHTML = '<span></span><span></span><span></span>';
    chatMessages.appendChild(typing);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

sendBtn.addEventListener('click', handleChatSubmit);
chatInput.addEventListener('keypress', e => { if (e.key === 'Enter') handleChatSubmit(); });

async function handleChatSubmit() {
    const text = chatInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    conversationHistory.push({ role: 'user', text });
    chatInput.value = '';
    showTypingIndicator();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: conversationHistory })
        });
        const data = await res.json();
        removeTypingIndicator();
        const reply = data.text || 'Sorry, I had trouble responding.';
        addMessage(reply, 'ai');
        conversationHistory.push({ role: 'ai', text: reply });
    } catch (err) {
        console.error(err);
        removeTypingIndicator();
        addMessage('Could not connect to the AI backend.', 'ai');
    }
}

// ─── Initialize ───────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    renderCategories();
    renderPros();
});
