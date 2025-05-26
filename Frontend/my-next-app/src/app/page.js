"use client";

import { useState } from "react";
import Output from "../components/parser_output/page";


export default function Home() {
  const [code, setCode] = useState("");
  const [parserType, setParserType] = useState("CLR");
  const [displayedGrammar, setDisplayedGrammar] = useState('');
  const [selectedGrammar, setSelectedGrammar] = useState('main/input_grammar_7.txt');
  const [grammarText, setGrammarText] = useState('');
  const [resultData, setResultData] = useState(null);



  const loadGrammar = async (grammarName) => {
    try {
      const res = await fetch(`/${grammarName}.txt`);
      const text = await res.text();
      setDisplayedGrammar(grammarName);
      setGrammarText(text);  
    } catch (err) {
      console.error("Failed to load grammar:", err);
      alert("Could not load the selected grammar file.");
    }
  };
  
  
  
  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      code: code,
      grammar: selectedGrammar,
    };
  try {
      if(parserType == "CLR"){
      const res = await fetch("http://127.0.0.1:8000/parse_CLR/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      setResultData(data);
      }
      else{
        const res = await fetch("http://127.0.0.1:8000/parse_CLR/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      setResultData(data);
      }


      // ⬇️ Nicely format and log full response
      console.log("🟢 Parsing Result Received from Backend:");
      console.log("Status:", resultData.status);
      console.log("\n🔹 First & Follow Sets:");
      console.table(resultData.first_follow);

      console.log("\n🔹 Canonical Items:");
      resultData.canonical_items.forEach((item, index) => {
        console.log(`Item ${index}:`, item);
      });

      console.log("\n🔹 CLR Table:");
      Object.entries(resultData.clr_table).forEach(([state, actions]) => {
        console.log(`State ${state}:`, actions);
      });

      console.log("\n🔹 Parsing Steps:");
      resultData.parsing_steps.forEach((step, index) => {
        console.log(`Step ${index}:`, step);
      });

      console.log("\n🔹 Error Code:", resultData.error);

      alert(`${parserType} Parsing Completed. Check console for detailed output.`);
     
    } catch (error) {
      console.error("❌ Error in request:", error);
      alert("Something went wrong!");
    }
  };


  const dropdownStyle = {
    width: "100%",
    padding: "0.5rem",
    color: "#444",
    fontSize: "1rem",
    fontWeight: "bold",
    borderRadius: "6px",
    border: "1px solid #ccc",
    marginBottom: "1.5rem",
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f4f4f9", fontFamily: "Arial, sans-serif" }}>
      {/* Header */}
      <header
  style={{
    background: "#121212",
    color: "white",
    padding: "1.2rem 2rem",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    boxShadow: "0 4px 8px rgba(0,0,0,0.15)",
    fontFamily: "'Poppins', sans-serif",
    borderBottom: "1px solid #2c2c3c",
  }}
>
  <div
    style={{
      flex: 1,
      textAlign: "center",
      fontSize: "2rem",
      fontWeight: 600,
      letterSpacing: "1px",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      gap: "0.8rem",
       color: "white",
      textShadow:
      "0 0 5px orange, 0 0 10px orange, 0 0 15px orange, 0 0 20px green,0 0 25px green",
    }}
  >
    <img
      src="./logo.png"
      alt="Parser Visualizer Logo"
      style={{ height: "35px", width: "35px" }}
    />
    Parser Visualizer
  </div>

  <div style={{ display: "flex", gap: "1rem" }}>
    {/* Future space for user avatar, theme toggle, or settings button */}
  </div>
</header>




      
      <div style={{ padding: '1rem' , backgroundColor:'#121212' }}>
        

       
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '1rem' }}>
        <button
  onClick={() => loadGrammar('grammar1')}
  style={{
    padding: '0.5rem 1rem',
    backgroundColor: '#004080',
    color: 'white',
    border: "4px solid #2c2c3c",
    borderRadius: '4px',
    cursor: 'pointer',
  }}
>
  Grammar 1
</button>

<button
  onClick={() => loadGrammar('grammar2')}
  style={{
    padding: '0.5rem 1rem',
    backgroundColor: '#004080',
    color: 'white',
     border: "4px solid #2c2c3c",
    borderRadius: '4px',
    cursor: 'pointer',
  }}
>
  Grammar 2
</button>

        </div>

       
        {grammarText && (
  <pre
    style={{
      background: 'white',
      color: 'black',
      padding: '2rem',
      border: "4px solid #2c2c3c",
      borderRadius: '6px',
      margin: '0 auto 2rem',
      maxWidth: '700px',
      whiteSpace: 'pre-wrap',
      fontFamily: 'Courier New, monospace'
    }}
  >
    {grammarText}
  </pre>
)}


      </div>

      
      <main style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "2rem 1rem" , backgroundColor: "#121212" }}>
        <form
          onSubmit={handleSubmit}
          style={{
            backgroundColor: "#1e1e2f",
            padding: "2rem",
            border: "6px solid #2c2c3c",
            borderRadius: "10px",
            boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
            width: "100%",
            maxWidth: "700px",
          }}
        >
         
          <div style={{ textAlign: 'center', marginBottom: "1.5rem" }}>
            <label htmlFor="grammar-select" style={{ marginRight: '0.5rem', fontWeight: "bold", color: "#444"}}>Choose Grammar:</label>
            <select
              id="grammar-select"
              value={selectedGrammar}
              onChange={(e) => setSelectedGrammar(e.target.value)}
              style={{padding: '0.5rem',
  border: '2px solid #2c2c3c',
  backgroundColor: '#000',
  color: '#00ffff',
  borderRadius: '5px',
  fontFamily: "'Poppins', sans-serif"}}
            >
              <option value="main/input_grammar_7.txt">Grammar 1</option>
              <option value="main/grammar2.txt">Grammar 2</option>
            </select>
          </div>

          
          <label style={{ display: "block", fontSize: "1.1rem", marginBottom: "0.5rem", color: "#444",width: '100%',
  padding: '0.8rem',
  border: '2px solid #00ffff',
  backgroundColor: '#000',
  color: '#00ffff',
  fontFamily: "'Fira Code', monospace",
  borderRadius: '6px',
  outline: 'none',
  boxShadow: '0 0 8px #00ffff inset',
  resize: 'vertical' }}>
            Input code to be checked:
          </label>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={10}
            style={{
              width: "100%",
              padding: "0.8rem",
              fontSize: "1rem",
              border: "2px solid #00ffff",
              borderRadius: "6px",
              resize: "vertical",
              backgroundColor: "#fdfdfd",
              marginBottom: "1.5rem",
              width: '100%',
              backgroundColor: '#000',
              color: '#00ffff',
              fontFamily: "'Fira Code', monospace",
              outline: 'none',
              boxShadow: '0 0 8px #00ffff inset',
              resize: 'vertical'
            }}
            placeholder="Type your grammar/code here..."
          />

          
          <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "bold", color: "#444" }}>
            Select Parser Type:
          </label>
          <select
            value={parserType}
            onChange={(e) => setParserType(e.target.value)}
            style={{padding: '0.5rem',
  border: '2px solid #00ffff',
  backgroundColor: '#000',
  color: '#00ffff',
  borderRadius: '5px',
  fontFamily: "'Poppins', sans-serif"}}
          >
            <option value="CLR">CLR</option>
            <option value="SLR">SLR</option>
          </select>

          
          <div style={{ textAlign: "center" }}>
            <button
              type="submit"
              style={{
                fontSize: "1rem",
                cursor: "pointer",
                padding: '0.6rem 1.2rem',
                background: 'linear-gradient(45deg, #00ff99, #00ffff)',
                border: '2px solid #00ffcc',
                color: 'black',
                borderRadius: '6px',
                fontWeight: 'bold',
              }}
            >
              Submit
            </button>
          </div>
        </form>
      </main>
      {resultData && <Output result={resultData} />}
    </div>
  );
}

