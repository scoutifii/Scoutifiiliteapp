const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const startStreamButton = document.getElementById('startStream');
const micBtn = document.getElementById('mic-btn');
const cameraBtn = document.getElementById('camera-btn');
const screenBtn = document.getElementById('screen-btn');
const leaveBtn = document.getElementById('leave-btn');

//-------- Session/Config --------//
const APP_ID = '465f6d93a6ab47d794a425f03718ef4f'
const CHANNEL = "Scoutifii Stream"
const TOKEN = '007eJxTYFBzfTGldtfxics89cKLojPDNv/80LFmzgOzz3q77raI7pivwGBiZppmlmJpnGiWmGRinmJuaZJoYmSaZmBsbmiRmmaSNn8jZ2ZDICPDlfZZjIwMEAjiCzAEJ+eXlmSmZWYqBJcUpSbmMjAAAJ9pJi4='
let UID = sessionStorage.getItem('profile') || (window.CURRENT_PROFILE_ID ? String(window.CURRENT_PROFILE_ID) : '');
let PROFILE = sessionStorage.getItem('profile') || (window.CURRENT_PROFILE_ID ? String(window.CURRENT_PROFILE_ID) : '');

let constraints = {
    encoderConfig: {
        width: {min:640, ideal:1920, max:1920},
        height: {min:480, ideal:1080, max:1080},
    },
    audio: true
}

// ====== Agora Client ======
const client = AgoraRTC.createClient({ mode: 'live', codec: 'vp8' });
// For broadcaster role in "live" mode (needed for low-latency)
client.setClientRole && client.setClientRole('host');

let localTracks = {
  mic: null,
  cam: null
};
let published = false;

let localStream;
let mediaRecorder;
let recordedChunks = [];
let isRecording = false;
let peerConnection;
let currentPreviewStream;
const signalingServer = new WebSocket('ws://127.0.0.1:8000/ws/webrtc/');

function chooseSupportedMime() {
  if (MediaRecorder.isTypeSupported('video/webm;codecs=vp9')) return 'video/webm;codecs=vp9';
  if (MediaRecorder.isTypeSupported('video/webm;codecs=vp8')) return 'video/webm;codecs=vp8';
  if (MediaRecorder.isTypeSupported('video/webm')) return 'video/webm';
  return '';
}

// ICE servers for STUN/TURN
const configuration = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
};


// Handle messages from the signaling server
// signalingServer.onmessage = async (message) => {
//   const data = JSON.parse(message.data);

//   if (data.type === 'offer') {
//     // Set remote description and create an answer
//     await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
//     const answer = await peerConnection.createAnswer();
//     await peerConnection.setLocalDescription(answer);
//     signalingServer.send(JSON.stringify({ type: 'answer', answer }));
//   } else if (data.type === 'answer') {
//     // Set remote description
//     await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
//   } else if (data.type === 'ice-candidate') {
//     // Add ICE candidate
//     await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
//   }
// };

//Save the stream to the DB

function startRecording(stream) {
  if (!stream) return;
  recordedChunks = [];
  const mime = chooseSupportedMime();
  // Choose a mime type supported by the browser
  // const mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
  //   ? 'video/webm;codecs=vp9'
  //   : 'video/webm;codecs=vp8';

  mediaRecorder = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
  mediaRecorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) recordedChunks.push(e.data);
  };
  mediaRecorder.onstop = uploadRecording;
  mediaRecorder.start(); // optionally pass timeslice ms to get periodic chunks
  isRecording = true;
  startStreamButton.textContent = 'Stop Live';
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    isRecording = false;
    startStreamButton.textContent = 'Start Live';
  }
}

async function uploadRecording() {
  const blob = new Blob(recordedChunks, { type: recordedChunks[0]?.type || 'video/webm' });
  if (!blob || blob.size === 0) {
    console.error('No recorded data');
    alert('No recording captured.');
    return;
  }
  // let UID = Number(sessionStorage.getItem('UID')) || 0;
  const file = new File([blob], `recording_${Date.now()}.webm`, { type: blob.type });
  const formData = new FormData();
  formData.append('recording', file);
  formData.append('title', `Live ${new Date().toISOString()}`);
  formData.append('is_live', 'true');
  formData.append('profile_id', PROFILE || String(window.CURRENT_PROFILE_ID || '')); 
  formData.append('uid', UID.toString());

  await getBlobDurationSeconds(blob).then(d => {
    formData.append('duration_seconds', String(Math.round(d)));
  }).catch(() => { /* ignore */ });

  // CSRF
  const csrfToken = 
    document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
    document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;

  try {
    const resp = await fetch('/live', {
      method: 'POST',
      headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
      body: formData,
      credentials: 'same-origin'
    });

    const text = await resp.text();
     if (!resp.ok) {
      console.error('Upload failed:', resp.status, text);
      alert(`Upload failed: ${resp.status}`);
      return;
    }
    
    // Try to parse JSON; if it fails, log the server HTML (likely CSRF or template)
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      console.error('Expected JSON but got:', text.slice(0, 500));
      alert('Server did not return JSON. Check backend view.');
      return;
    }
    
    alert('Recording saved!');
    console.log('Saved recording:', data);
  } catch (e) {
    console.error('Upload error', e);
    alert('Upload failed. See console.');
  }
}

function getBlobDurationSeconds(blob) {
  return new Promise((resolve, reject) => {
    const el = document.createElement('video');
    el.preload = 'metadata';
    el.onloadedmetadata = () => {
      URL.revokeObjectURL(el.src);
      resolve(el.duration || 0);
    };
    el.onerror = reject;
    el.src = URL.createObjectURL(blob);
  });
}

async function createLocalTracks() {
  const micTrack = await AgoraRTC.createMicrophoneAudioTrack();
  const camTrack = await AgoraRTC.createCameraVideoTrack({
    encoderConfig
  });
  localTracks.mic = micTrack;
  localTracks.cam = camTrack;

  // Create a preview stream for the recorder/UI from mic+cam
  const previewStream = new MediaStream();
  if (camTrack && camTrack.getMediaStreamTrack) {
    previewStream.addTrack(camTrack.getMediaStreamTrack());
  }
  if (micTrack && micTrack.getMediaStreamTrack) {
    previewStream.addTrack(micTrack.getMediaStreamTrack());
  }
  currentPreviewStream = previewStream;
  localVideo.srcObject = currentPreviewStream;
}

async function publishLocalTracks() {
  if (published) return;
  await client.publish([localTracks.mic, localTracks.cam].filter(Boolean));
  published = true;
}

async function unpublishAndClose() {
  try {
    if (published) {
      await client.unpublish([localTracks.mic, localTracks.cam].filter(Boolean));
    }
  } catch (e) {
    console.warn('Unpublish error', e);
  }
  [localTracks.mic, localTracks.cam].forEach(t => {
    try { t?.stop(); t?.close?.(); } catch {}
  });
  localTracks.mic = null;
  localTracks.cam = null;
  published = false;
}


// Start streaming
startStreamButton?.addEventListener('click', async () => {
  try {
    // Join Agora
    const tokenToUse = (typeof TOKEN === 'string' && TOKEN.trim().length > 0) ? TOKEN : null;
    await client.setClientRole?.('host'); // ensure role before join
    await client.join(APP_ID, CHANNEL, tokenToUse, UID);
    
    console.log('Joining Agora:', { APP_ID: APP_ID.slice(0, 6) + '…', CHANNEL, hasToken: !!tokenToUse, UID });

    // Prepare tracks and preview
    await createLocalTracks();

    // Publish to Agora (followers can watch via Agora SDK on viewer pages)
    await publishLocalTracks();

    // Start local recording for VOD
    if (!isRecording) startRecording(currentPreviewStream);
    else stopRecording();

    // Optional: notify your backend that live started (room/channel association)
    await liveStreamRegister();

  } catch (error) {
    console.error('Start stream error:', error);
    alert('Failed to start stream. Check console.');
  }
  // localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  // localVideo.srcObject = localStream;
  // if (!isRecording) startRecording();
  // else stopRecording();

  // peerConnection = new RTCPeerConnection(configuration);

  // // Add local stream tracks to the peer connection
  // localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

  // // Handle remote stream
  // peerConnection.ontrack = (event) => {
  //   remoteVideo.srcObject = event.streams[0];
  // };

  // // Send ICE candidates to the signaling server
  // peerConnection.onicecandidate = (event) => {
  //   if (event.candidate) {
  //     signalingServer.send(JSON.stringify({ type: 'ice-candidate', candidate: event.candidate }));
  //   }
  // };

  // // Create an offer and send it to the signaling server
  // const offer = await peerConnection.createOffer();
  // await peerConnection.setLocalDescription(offer);
  // signalingServer.send(JSON.stringify({ type: 'offer', offer }));
});


micBtn?.addEventListener('click', async(e) => {
  if (!localTracks.mic) return;
  const muted = localTracks.mic.isMuted ? localTracks.mic.isMuted() : localTracks.mic._enabled === false;
  // Agora microphone track exposes setEnabled or setMuted depending on SDK version
  if (localTracks.mic.setMuted) {
    await localTracks.mic.setMuted(!muted);
  } else if (localTracks.mic.setEnabled) {
    await localTracks.mic.setEnabled(muted);
  }
  const nowEnabled = localTracks.mic._enabled !== false && !(localTracks.mic.isMuted && localTracks.mic.isMuted());
  micBtn.classList.toggle('muted', !nowEnabled);
  e.currentTarget.style.backgroundColor = nowEnabled
    ? 'rgba(255, 80, 80, 1)'  // red
    : '#fff'; 
});

cameraBtn?.addEventListener('click', async(e) => {
  if (!localTracks.cam) return;
  // Toggle video publishing and preview
  const isEnabled = localTracks.cam.isPlaying ? true : true; // Using track enable instead of playing state
  // For Agora SDK, use setEnabled or setMuted on the underlying MediaStreamTrack
  const track = localTracks.cam.getMediaStreamTrack?.();
  if (!track) return;
  track.enabled = !track.enabled;

  cameraBtn.classList.toggle('off', !track.enabled);
  e.currentTarget.style.backgroundColor = track.enabled
    ? 'rgba(255, 80, 80, 1)'  // red
    : '#fff'; 
  localVideo.srcObject = null;
  localVideo.srcObject = currentPreviewStream;
});

screenBtn?.addEventListener('click', async () => {
  try {
    const screen = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
    const screenVideoTrack = screen.getVideoTracks()[0];

    // Replace the published video track in Agora
    if (localTracks.cam && localTracks.cam.replaceTrack) {
      await localTracks.cam.replaceTrack(screenVideoTrack);
    } else {
      // Fallback: unpublish camera, create a new custom video track from screen
      await client.unpublish(localTracks.cam);
      const screenCustom = AgoraRTC.createCustomVideoTrack({ mediaStreamTrack: screenVideoTrack });
      localTracks.cam = screenCustom;
      await client.publish(localTracks.cam);
    }

    // Update preview and recording source
    const stream = new MediaStream();
    stream.addTrack(screenVideoTrack);
    const micTrack = currentPreviewStream.getAudioTracks()[0];
    if (micTrack) stream.addTrack(micTrack);
    currentPreviewStream = stream;
    localVideo.srcObject = null;
    localVideo.srcObject = currentPreviewStream;

    // When screen share stops, switch back to camera
    screenVideoTrack.addEventListener('ended', async () => {
      const camera = await navigator.mediaDevices.getUserMedia({ video: true });
      const camTrack = camera.getVideoTracks()[0];

      if (localTracks.cam && localTracks.cam.replaceTrack) {
        await localTracks.cam.replaceTrack(camTrack);
      } else {
        await client.unpublish(localTracks.cam);
        const camCustom = AgoraRTC.createCustomVideoTrack({ mediaStreamTrack: camTrack });
        localTracks.cam = camCustom;
        await client.publish(localTracks.cam);
      }

      // Rebuild preview with camera + previous mic
      const backStream = new MediaStream();
      backStream.addTrack(camTrack);
      const mic = currentPreviewStream.getAudioTracks()[0] || (await navigator.mediaDevices.getUserMedia({ audio: true })).getAudioTracks()[0];
      if (mic) backStream.addTrack(mic);
      currentPreviewStream = backStream;
      localVideo.srcObject = currentPreviewStream;
    });
  } catch (e) {
    console.warn('Screen share cancelled', e);
  }
});

leaveBtn?.addEventListener('click', async(e) => {
 try {
    stopRecording();
    await unpublishAndClose();
    await client.leave();
  } catch (e) {
    console.warn('Leave error', e);
  } finally {
    try {
      const tracks = currentPreviewStream?.getTracks() || [];
      tracks.forEach(t => t.stop());
    } catch {}
    window.location.href = '/dashboard';
  }
});

// ====== Backend registration (optional but recommended) ======
async function liveStreamRegister() {
  try {
    const resp = await fetch('live_stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile: PROFILE, channel_name: CHANNEL, UID })
    });
    // It's fine if backend returns info about stream; you can use it to show title/name
    // const stream = await resp.json();
  } catch (e) {
    console.warn('Failed to register live stream start', e);
  }
}