const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const startStreamButton = document.getElementById('startStream');
const micBtn = document.getElementById('mic-btn');
const cameraBtn = document.getElementById('camera-btn');
const screenBtn = document.getElementById('screen-btn');
const leaveBtn = document.getElementById('leave-btn');

let localStream;
let mediaRecorder;
let recordedChunks = [];
let isRecording = false;
let peerConnection;
const signalingServer = new WebSocket('ws://127.0.0.1:8000/ws/webrtc/');

// ICE servers for STUN/TURN
const configuration = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
};

// Start streaming
startStreamButton?.addEventListener('click', async () => {
  localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  localVideo.srcObject = localStream;
  if (!isRecording) startRecording();
  else stopRecording();

  peerConnection = new RTCPeerConnection(configuration);

  // Add local stream tracks to the peer connection
  localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

  // Handle remote stream
  peerConnection.ontrack = (event) => {
    remoteVideo.srcObject = event.streams[0];
  };

  // Send ICE candidates to the signaling server
  peerConnection.onicecandidate = (event) => {
    if (event.candidate) {
      signalingServer.send(JSON.stringify({ type: 'ice-candidate', candidate: event.candidate }));
    }
  };

  // Create an offer and send it to the signaling server
  const offer = await peerConnection.createOffer();
  await peerConnection.setLocalDescription(offer);
  signalingServer.send(JSON.stringify({ type: 'offer', offer }));
});

// Handle messages from the signaling server
signalingServer.onmessage = async (message) => {
  const data = JSON.parse(message.data);

  if (data.type === 'offer') {
    // Set remote description and create an answer
    await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    signalingServer.send(JSON.stringify({ type: 'answer', answer }));
  } else if (data.type === 'answer') {
    // Set remote description
    await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
  } else if (data.type === 'ice-candidate') {
    // Add ICE candidate
    await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
  }
};

//Save the stream to the DB
async function saveStreamToDatabase(title, streamUrl) {
  const response = await fetch('/api/save-stream/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, stream_url: streamUrl, is_live: true })
  });
  const result = await response.json();
  console.log(result.message);
}

function startRecording() {
  if (!localStream) return;
  recordedChunks = [];
  // Choose a mime type supported by the browser
  const mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
    ? 'video/webm;codecs=vp9'
    : 'video/webm;codecs=vp8';

  mediaRecorder = new MediaRecorder(localStream, { mimeType: mime });
  mediaRecorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) recordedChunks.push(e.data);
  };
  mediaRecorder.onstop = uploadRecording;
  mediaRecorder.start(); // optionally pass timeslice ms to get periodic chunks
  isRecording = true;
  startStreamButton.textContent = 'Stop Recording';
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    isRecording = false;
    startStreamButton.textContent = 'Start Recording';
  }
}

async function uploadRecording() {
  const blob = new Blob(recordedChunks, { type: recordedChunks[0]?.type || 'video/webm' });
  const file = new File([blob], `recording_${Date.now()}.webm`, { type: blob.type });

  const formData = new FormData();
  formData.append('recording', file);
  formData.append('title', `Live ${new Date().toISOString()}`);

  // CSRF
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  try {
    const resp = await fetch('/live/', {
      method: 'POST',
      headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
      body: formData,
      credentials: 'same-origin'
    });
    if (!resp.ok) throw new Error(`Upload failed ${resp.status}`);
    const data = await resp.json();
    alert('Recording saved!');
    console.log('Saved recording:', data);
  } catch (e) {
    console.error('Upload error', e);
    alert('Upload failed. See console.');
  }
}

micBtn?.addEventListener('click', (e) => {
  if (!localStream) return;
  const track = localStream.getAudioTracks()[0];
  if (!track) return;
  track.enabled = !track.enabled;
  micBtn.classList.toggle('muted', !track.enabled);
  e.currentTarget.style.backgroundColor = track.enabled
    ? 'rgba(255, 80, 80, 1)'  // red
    : '#fff'; 
});

cameraBtn?.addEventListener('click', (e) => {
  if (!localStream) return;
  const track = localStream.getVideoTracks()[0];
  if (!track) return;
  track.enabled = !track.enabled;
  cameraBtn.classList.toggle('off', !track.enabled);
  e.currentTarget.style.backgroundColor = track.enabled
    ? 'rgba(255, 80, 80, 1)'  // red
    : '#fff'; 
});

screenBtn?.addEventListener('click', async () => {
  try {
    const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
    // Replace video track in the local stream for recording/preview
    const videoTrack = screenStream.getVideoTracks()[0];
    const sender = null; // if using RTCPeerConnection, replace sender track here
    // For preview
    const [oldTrack] = localStream.getVideoTracks();
    if (oldTrack) localStream.removeTrack(oldTrack);
    localStream.addTrack(videoTrack);
    localVideo.srcObject = null;
    localVideo.srcObject = localStream;

    screenStream.getVideoTracks()[0].addEventListener('ended', () => {
      // Switch back to camera when screen share ends
      navigator.mediaDevices.getUserMedia({ video: true }).then(cameraStream => {
        const cameraTrack = cameraStream.getVideoTracks()[0];
        const [current] = localStream.getVideoTracks();
        if (current) localStream.removeTrack(current);
        localStream.addTrack(cameraTrack);
        localVideo.srcObject = localStream;
      });
    });
  } catch (e) {
    console.warn('Screen share cancelled', e);
  }
});

leaveBtn?.addEventListener('click', () => {
  // Stop all tracks and reset
  localStream?.getTracks().forEach(t => t.stop());
  stopRecording();
  window.location.href = '/dashboard'; // or another page
});