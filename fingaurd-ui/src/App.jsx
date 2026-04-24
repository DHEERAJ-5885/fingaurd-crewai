import { useState } from "react";
import axios from "axios";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";

function App() {
  const [data, setData] = useState({
    balance: "",
    rent: "",
    food: "",
    upcoming: "",
    spend: "",
    future_spend: "",
    months: "",
  });

  const [result, setResult] = useState(null);
  const [isListening, setIsListening] = useState(false);

  const { transcript, resetTranscript } = useSpeechRecognition();

  // 🔢 NUMBER EXTRACTOR (STRONG)
  const extractNumber = (text) => {
    if (!text) return null;

    text = text.toLowerCase();

    // 5k, 10k
    const kMatch = text.match(/(\d+)\s*k/);
    if (kMatch) return parseInt(kMatch[1]) * 1000;

    // 5 thousand
    const tMatch = text.match(/(\d+)\s*thousand/);
    if (tMatch) return parseInt(tMatch[1]) * 1000;

    // digits
    const nums = text.match(/\d+/g);
    if (nums) return parseInt(nums.join(""));

    return null;
  };

  // 🧠 SMART VOICE PARSER
  const handleVoice = (text) => {
    const num = extractNumber(text);
    if (!num) return;

    const t = text.toLowerCase();

    if (t.includes("balance") || t.includes("have") || t.includes("salary")) {
      setData((p) => ({ ...p, balance: num }));
    } else if (t.includes("rent") || t.includes("room")) {
      setData((p) => ({ ...p, rent: num }));
    } else if (t.includes("food") || t.includes("eat")) {
      setData((p) => ({ ...p, food: num }));
    } else if (t.includes("upcoming") || t.includes("expense")) {
      setData((p) => ({ ...p, upcoming: num }));
    } else if (t.includes("future")) {
      setData((p) => ({ ...p, future_spend: num }));
    } else if (t.includes("month")) {
      setData((p) => ({ ...p, months: num }));
    } else if (t.includes("spend") || t.includes("use")) {
      setData((p) => ({ ...p, spend: num }));
    } else {
      // fallback auto fill
      const keys = Object.keys(data);
      for (let key of keys) {
        if (!data[key]) {
          setData((p) => ({ ...p, [key]: num }));
          break;
        }
      }
    }
  };

  // 🎤 TOGGLE MIC (STABLE)
  const toggleListening = () => {
    if (!isListening) {
      resetTranscript();
      SpeechRecognition.startListening({
        continuous: true,
        language: "en-IN",
      });
      setIsListening(true);
    } else {
      SpeechRecognition.stopListening();
      setIsListening(false);

      if (transcript) {
        handleVoice(transcript.toLowerCase());
      }
    }
  };

  // 🧠 API CALL
  const analyze = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/analyze", {
        balance: Number(data.balance),
        rent: Number(data.rent),
        food: Number(data.food),
        upcoming: Number(data.upcoming),
        spend: Number(data.spend),
        future_spend: Number(data.future_spend),
        months: Number(data.months),
      });

      setResult(res.data);
    } catch (err) {
      alert("Backend not running or CORS issue");
    }
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 to-black min-h-screen text-white flex flex-col items-center justify-center gap-6 p-6">

      <h1 className="text-4xl font-bold tracking-wide">💰 FinGuard</h1>

      {/* 🎤 MIC */}
      <button
        onClick={toggleListening}
        className={`p-6 rounded-full text-3xl shadow-lg transition ${
          isListening ? "bg-red-500 scale-110" : "bg-green-500"
        }`}
      >
        🎤
      </button>

      <p className="text-sm text-gray-400">
        {isListening ? "Listening... click again to stop" : "Click mic & speak"}
      </p>

      {/* 📝 INPUTS */}
      <div className="grid grid-cols-2 gap-4">
        {Object.keys(data).map((key) => (
          <input
            key={key}
            placeholder={key}
            value={data[key]}
            onChange={(e) =>
              setData({ ...data, [key]: e.target.value })
            }
            className="p-3 w-44 bg-slate-800 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        ))}
      </div>

      {/* 🚀 BUTTON */}
      <button
        onClick={analyze}
        className="bg-blue-600 px-8 py-3 rounded-lg hover:bg-blue-700 shadow"
      >
        Analyze
      </button>

      {/* 📊 RESULT */}
      {result && (
        <div className="mt-6 text-center space-y-3 bg-slate-800 p-6 rounded-xl w-96 shadow-lg">

          <p className="text-lg">💰 Remaining: {result.remaining}</p>
          <p>⚠️ Risk: {result.risk}</p>
          <p>📊 Decision: {result.final_decision}</p>

          <div className="text-gray-300 text-sm mt-3">
            {result.final_decision === "SAFE"
              ? "You're financially stable. Your expenses are well balanced and sustainable."
              : "Warning: Your spending exceeds safe limits. Adjust expenses to avoid future issues."}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;