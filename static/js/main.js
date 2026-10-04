// State
let comebacksState = [];
let mediaRecorder;
let audioChunks = [];
let activeTab = 'type'; // 'type' or 'record'

// Tab Handling
function openTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    
    document.getElementById(tabId).classList.add('active');
    
    if (tabId === 'type-tab') {
        document.querySelector('.tab-btn:nth-child(1)').classList.add('active');
        activeTab = 'type';
    } else {
        document.querySelector('.tab-btn:nth-child(2)').classList.add('active');
        activeTab = 'record';
    }
}

// Audio Recording
const recordBtn = document.getElementById('record-btn');
const stopBtn = document.getElementById('stop-btn');
const recordingStatus = document.getElementById('recording-status');

if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    recordBtn.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            
            mediaRecorder.ondataavailable = e => {
                audioChunks.push(e.data);
            };
            
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = [];
                await transcribeAudio(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            mediaRecorder.start();
            recordBtn.disabled = true;
            stopBtn.disabled = false;
            recordingStatus.innerText = 'Recording...';
            recordingStatus.style.color = '#ff4444';
        } catch (err) {
            console.error(err);
            recordingStatus.innerText = 'Microphone access denied or not available.';
        }
    });

    stopBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            recordBtn.disabled = false;
            stopBtn.disabled = true;
            recordingStatus.innerText = 'Transcribing...';
            recordingStatus.style.color = '#888';
        }
    });
} else {
    recordingStatus.innerText = 'Audio recording not supported in this browser.';
    recordBtn.disabled = true;
}

async function transcribeAudio(blob) {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.webm');
    formData.append('input_language', document.getElementById('input-language').value);
    
    try {
        const response = await fetch('/api/transcribe', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('transcribed-text-container').style.display = 'block';
            document.getElementById('transcribed-text').value = data.text;
            recordingStatus.innerText = 'Transcription complete.';
            recordingStatus.style.color = '#4ade80';
        } else {
            recordingStatus.innerText = 'Error: ' + (data.error || 'Unknown error');
        }
    } catch (err) {
        recordingStatus.innerText = 'Transcription failed.';
        console.error(err);
    }
}

// Generate Comebacks
document.getElementById('generate-btn').addEventListener('click', async () => {
    let bullyText = '';
    if (activeTab === 'type') {
        bullyText = document.getElementById('bully-text').value.trim();
    } else {
        bullyText = document.getElementById('transcribed-text').value.trim();
    }
    
    if (!bullyText) {
        alert("Please enter or record what the bully said first!");
        return;
    }
    
    const outputLang = document.getElementById('output-language').value;
    const numComebacks = document.getElementById('num-comebacks').value;
    const style = document.querySelector('input[name="style"]:checked').value;
    
    // UI changes
    document.getElementById('loading-spinner').style.display = 'block';
    document.getElementById('results-container').innerHTML = '';
    document.getElementById('tts-section').style.display = 'none';
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                bully_text: bullyText,
                output_language: outputLang,
                num_comebacks: numComebacks,
                preferred_style: style
            })
        });
        
        const data = await response.json();
        document.getElementById('loading-spinner').style.display = 'none';
        
        if (response.ok) {
            comebacksState = data.comebacks;
            renderComebacks(comebacksState);
            setupTTS(comebacksState.length);
        } else {
            document.getElementById('results-container').innerHTML = `<div class="status-msg" style="color:#ff4444;">Error: ${data.error}</div>`;
        }
    } catch (err) {
        document.getElementById('loading-spinner').style.display = 'none';
        document.getElementById('results-container').innerHTML = `<div class="status-msg" style="color:#ff4444;">Request failed.</div>`;
        console.error(err);
    }
});

const styleColors = {
    'savage': ['#ff4444', '#ff6b6b'],
    'funny': ['#ffaa00', '#ffd93d'],
    'cool_unbothered': ['#00d2ff', '#7ee8fa'],
    'intellectual': ['#a855f7', '#c084fc'],
    'movie_reference': ['#22c55e', '#4ade80']
};

function renderComebacks(comebacks) {
    const container = document.getElementById('results-container');
    if (!comebacks || comebacks.length === 0) {
        container.innerHTML = '<div class="placeholder-msg">No comebacks generated. Try again!</div>';
        return;
    }
    
    let html = '';
    comebacks.forEach((cb, i) => {
        const style = cb.style || 'savage';
        const colors = styleColors[style] || styleColors['savage'];
        const label = cb.style_label || style.replace('_', ' ').toUpperCase();
        const actor = cb.actor_ref ? `<span class="actor-badge">Actor: ${cb.actor_ref}</span>` : '';
        
        html += `
        <div class="comeback-card" style="border-left-color: ${colors[0]};">
            <div class="comeback-header">
                <span class="comeback-style" style="color: ${colors[1]}">${label}</span>
                <span class="comeback-index">#${i+1} ${actor}</span>
            </div>
            <p class="comeback-text">${cb.text}</p>
        </div>
        `;
    });
    
    container.innerHTML = html;
}

// TTS Setup
function setupTTS(numComebacks) {
    if (numComebacks > 0) {
        document.getElementById('tts-section').style.display = 'block';
        const select = document.getElementById('tts-index');
        select.innerHTML = '';
        for (let i = 1; i <= numComebacks; i++) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.innerText = i;
            select.appendChild(opt);
        }
    }
}

document.getElementById('speak-btn').addEventListener('click', async () => {
    const idx = parseInt(document.getElementById('tts-index').value) - 1;
    if (idx < 0 || idx >= comebacksState.length) return;
    
    const text = comebacksState[idx].text;
    const lang = document.getElementById('tts-language').value;
    const voice = document.getElementById('tts-voice').value;
    
    const btn = document.getElementById('speak-btn');
    btn.innerText = 'Preparing Audio...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/speak', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                tts_language: lang,
                voice_gender: voice
            })
        });
        
        const data = await response.json();
        btn.innerText = 'Read This Comeback';
        btn.disabled = false;
        
        if (response.ok) {
            const playerContainer = document.getElementById('audio-player-container');
            const player = document.getElementById('audio-player');
            
            // Add a cache buster so browser fetches fresh audio
            player.src = data.audio_url + '?t=' + new Date().getTime();
            playerContainer.style.display = 'block';
            player.play();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (err) {
        btn.innerText = 'Read This Comeback';
        btn.disabled = false;
        alert('Failed to fetch audio.');
        console.error(err);
    }
});
