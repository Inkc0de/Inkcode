// firebase.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyBiRP_PJH38Gu5awnyOSW2qBCS0Hx3xOvQ",
    authDomain: "inkcode-cadec.firebaseapp.com",
    projectId: "inkcode-cadec",
    storageBucket: "inkcode-cadec.appspot.com",
    messagingSenderId: "342069436728",
    appId: "1:342069436728:web:63adcd0ef4fd65b7b821cd",
    measurementId: "G-3L6ZJ1GK2V"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Export authentication module
export const auth = getAuth(app);

