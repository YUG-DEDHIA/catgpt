import axios from "axios";

// Create Axios instance for backend communication
const instance = axios.create({
  baseURL: "http://127.0.0.1:8000", // Ensure this matches your backend URL
});

export default instance;
