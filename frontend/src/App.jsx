import React, { useState, useRef, useEffect } from "react";
import axios from "./API";

const App = () => {
    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState("");
    const [enlargedImage, setEnlargedImage] = useState(null); // For modal
    const chatContainerRef = useRef(null);

    const handleSend = async () => {
        if (!userInput.trim()) return;

        setMessages((prev) => [...prev, { role: "user", content: userInput }]);
        const userMessage = userInput;
        setUserInput("");

        try {
            const { data } = await axios.post("/chat", { user_input: userMessage });

            const botMessages = Array.isArray(data.response)
                ? [
                      {
                          role: "assistant",
                          content: data.response.map((url, idx) => (
                              <img
                                  key={idx}
                                  src={url}
                                  alt={`Image ${idx}`}
                                  className="image-thumbnail"
                                  onClick={() => setEnlargedImage(url)} // Open modal
                              />
                          )),
                      },
                  ]
                : [{ role: "assistant", content: data.response }];

            setMessages((prev) => [...prev, ...botMessages]);
        } catch (error) {
            try {
                const { data } = await axios.get("/facts");
                console.log(data);
                setMessages((prev) => [
                    ...prev,
                    { role: "assistant", content: `Oops! Either breed doesn't exist or there is some spelling error. Please try again. Meanwhile, here is a fun fact about cats: ${data.fact}` },
                ]);
            } catch (factError) {
                console.error(factError);
                setMessages((prev) => [
                    ...prev,
                    { role: "assistant", content: "Oops! Something went wrong. Please try again later." },
                ]);
            }
            console.error(error);
        }
    };

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <div className="chat-container">
            <header className="chat-header">CatGPT</header>
            <main ref={chatContainerRef} className="chat-body">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`chat-message ${
                            msg.role === "user" ? "user-message" : "bot-message"
                        }`}
                    >
                        {Array.isArray(msg.content) ? (
                            <div className="image-container">{msg.content}</div>
                        ) : (
                            <p>{msg.content}</p>
                        )}
                    </div>
                ))}
            </main>
            <footer className="chat-footer">
                <input
                    type="text"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="Type a message..."
                    onKeyPress={(e) => {
                        if (e.key === "Enter") {
                            handleSend();
                        }
                    }}
                    className="chat-input"
                />
                <button onClick={handleSend} className="chat-send-button">
                    Send
                </button>
            </footer>

            {/* Modal for enlarged image */}
            {enlargedImage && (
                <div className="image-modal" onClick={() => setEnlargedImage(null)}>
                    <div className="modal-content">
                        <img src={enlargedImage} alt="Enlarged view" className="image-full" />
                    </div>
                </div>
            )}
        </div>
    );
};

export default App;
