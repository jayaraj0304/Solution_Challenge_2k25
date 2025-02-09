window.addEventListener("load", (event) => {
    console.log("Hello Gemini Realtime Demo!");

    setAvailableCamerasOptions();
    setAvailableMicrophoneOptions();
});

const PROXY_URL = "ws://localhost:8080";
const PROJECT_ID = "[]"; // enter your project id here
const MODEL = "gemini-2.0-flash-exp";
const API_HOST = "us-central1-aiplatform.googleapis.com";

const accessTokenInput ="[]";// enter your access token here
const projectInput ='[]';// enter your project id here
const systemInstructionsInput = "You are a highly intelligent, real-time AI Cooking Assistant, designed to offer expert and personalized guidance to users for a variety of cooking tasks. Your goal is to assist users by providing clear, step-by-step instructions for recipes, suggesting meal ideas based on available ingredients, dietary preferences, or time constraints, and offering helpful cooking tips that improve culinary skills. You can also recommend ingredient substitutions for missing items or dietary restrictions, making sure that the dish remains delicious. Whether it's providing real-time tips on cooking techniques, explaining food science, or identifying ingredients from images, you offer guidance through text, voice, and image inputs. Your communication is always friendly, engaging, and supportive, ensuring that both beginners and experienced cooks feel confident and motivated in the kitchen. You maintain a balance of concise yet detailed responses, ensuring safety in food handling and avoiding medical or nutritional advice. With your wide range of capabilities, you help users explore cooking with confidence and creativity, improving their cooking skills and making the process enjoyable.";

CookieJar.init("accessTokenInput");
CookieJar.init("projectInput");
CookieJar.init("systemInstructionsInput");

const disconnected = document.getElementById("disconnected");
const connecting = document.getElementById("connecting");
const connected = document.getElementById("connected");
const speaking = document.getElementById("speaking");

const micBtn = document.getElementById("micBtn");
const micOffBtn = document.getElementById("micOffBtn");
const cameraBtn = document.getElementById("cameraBtn");
const screenBtn = document.getElementById("screenBtn");

const cameraSelect = document.getElementById("cameraSource");
const micSelect = document.getElementById("audioSource");

const geminiLiveApi = new GeminiLiveAPI(PROXY_URL, PROJECT_ID, MODEL, API_HOST);

geminiLiveApi.onErrorMessage = (message) => {
    showDialogWithMessage(message);
    setAppStatus("disconnected");
};

function getSelectedResponseModality() {
    // return "AUDIO";
    const radioButtons = document.querySelectorAll(
        'md-radio[name="responseModality"]',
    );

    let selectedValue;
    for (const radioButton of radioButtons) {
        if (radioButton.checked) {
            selectedValue = radioButton.value;
            break;
        }
    }
    return selectedValue;
}

function getSystemInstructions() {
    return systemInstructionsInput;
}

function connectBtnClick() {
    setAppStatus("connecting");

    geminiLiveApi.responseModalities = getSelectedResponseModality();
    geminiLiveApi.systemInstructions = getSystemInstructions();

    geminiLiveApi.onConnectionStarted = () => {
        setAppStatus("connected");
        startAudioInput();
    };

    geminiLiveApi.setProjectId(projectInput);
    geminiLiveApi.connect(accessTokenInput);
}

const liveAudioOutputManager = new LiveAudioOutputManager();

geminiLiveApi.onReceiveResponse = (messageResponse) => {
    if (messageResponse.type == "AUDIO") {
        liveAudioOutputManager.playAudioChunk(messageResponse.data);
    } else if (messageResponse.type == "TEXT") {
        console.log("Gemini said: ", messageResponse.data);
        newModelMessage(messageResponse.data);
    }
};

const liveAudioInputManager = new LiveAudioInputManager();

liveAudioInputManager.onNewAudioRecordingChunk = (audioData) => {
    geminiLiveApi.sendAudioMessage(audioData);
};

function addMessageToChat(message) {
    const textChat = document.getElementById("text-chat");
    const newParagraph = document.createElement("p");
    newParagraph.textContent = message;
    textChat.appendChild(newParagraph);
}

function newModelMessage(message) {
    addMessageToChat(">> " + message);
}

function newUserMessage() {
    const textMessage = document.getElementById("text-message");
    addMessageToChat("User: " + textMessage.value);
    geminiLiveApi.sendTextMessage(textMessage.value);

    textMessage.value = "";
}

function startAudioInput() {
    liveAudioInputManager.connectMicrophone();
}

function stopAudioInput() {
    liveAudioInputManager.disconnectMicrophone();
}

function micBtnClick() {
    console.log("micBtnClick");
    stopAudioInput();
    micBtn.hidden = true;
    micOffBtn.hidden = false;
}

function micOffBtnClick() {
    console.log("micOffBtnClick");
    startAudioInput();

    micBtn.hidden = false;
    micOffBtn.hidden = true;
}

const videoElement = document.getElementById("video");
const canvasElement = document.getElementById("canvas");

const liveVideoManager = new LiveVideoManager(videoElement, canvasElement);

const liveScreenManager = new LiveScreenManager(videoElement, canvasElement);

liveVideoManager.onNewFrame = (b64Image) => {
    geminiLiveApi.sendImageMessage(b64Image);
};

liveScreenManager.onNewFrame = (b64Image) => {
    geminiLiveApi.sendImageMessage(b64Image);
};

function startCameraCapture() {
    liveScreenManager.stopCapture();
    liveVideoManager.startWebcam();
}

function startScreenCapture() {
    liveVideoManager.stopWebcam();
    liveScreenManager.startCapture();
}

function cameraBtnClick() {
    startCameraCapture();
    console.log("cameraBtnClick");
}

function screenShareBtnClick() {
    startScreenCapture();
    console.log("screenShareBtnClick");
}

function newCameraSelected() {
    console.log("newCameraSelected ", cameraSelect.value);
    liveVideoManager.updateWebcamDevice(cameraSelect.value);
}

function newMicSelected() {
    console.log("newMicSelected", micSelect.value);
    liveAudioInputManager.updateMicrophoneDevice(micSelect.value);
}

function disconnectBtnClick() {
    setAppStatus("disconnected");
    geminiLiveApi.disconnect();
    stopAudioInput();
}

function showDialogWithMessage(messageText) {
    const dialog = document.getElementById("dialog");
    const dialogMessage = document.getElementById("dialogMessage");
    dialogMessage.innerHTML = messageText;
    dialog.show();
}

async function getAvailableDevices(deviceType) {
    const allDevices = await navigator.mediaDevices.enumerateDevices();
    const devices = [];
    allDevices.forEach((device) => {
        if (device.kind === deviceType) {
            devices.push({
                id: device.deviceId,
                name: device.label || device.deviceId,
            });
        }
    });
    return devices;
}

async function getAvailableCameras() {
    return await this.getAvailableDevices("videoinput");
}

async function getAvailableAudioInputs() {
    return await this.getAvailableDevices("audioinput");
}

function setMaterialSelect(allOptions, selectElement) {
    allOptions.forEach((optionData) => {
        const option = document.createElement("md-select-option");
        option.value = optionData.id;

        const slotDiv = document.createElement("div");
        slotDiv.slot = "headline";
        slotDiv.innerHTML = optionData.name;
        option.appendChild(slotDiv);

        selectElement.appendChild(option);
    });
}

async function setAvailableCamerasOptions() {
    const cameras = await getAvailableCameras();
    const videoSelect = document.getElementById("cameraSource");
    setMaterialSelect(cameras, videoSelect);
}

async function setAvailableMicrophoneOptions() {
    const mics = await getAvailableAudioInputs();
    const audioSelect = document.getElementById("audioSource");
    setMaterialSelect(mics, audioSelect);
}

function setAppStatus(status) {
    disconnected.hidden = true;
    connecting.hidden = true;
    connected.hidden = true;
    speaking.hidden = true;

    switch (status) {
        case "disconnected":
            disconnected.hidden = false;
            break;
        case "connecting":
            connecting.hidden = false;
            break;
        case "connected":
            connected.hidden = false;
            break;
        case "speaking":
            speaking.hidden = false;
            break;
        default:
    }
}
