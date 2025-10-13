const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const startStreamButton = document.getElementById('startStream');

let localStream;
let peerConnection;
const signalingServer = new WebSocket('ws://127.0.0.1:8000/ws/webrtc/');

// ICE servers for STUN/TURN
const configuration = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
};

// Start streaming
startStreamButton.addEventListener('click', async () => {
  localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  localVideo.srcObject = localStream;

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