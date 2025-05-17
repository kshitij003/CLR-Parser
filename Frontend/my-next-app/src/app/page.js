"use client";

import { useState } from "react";

export default function Home() {
  const [code, setCode] = useState("");
  const [parserType, setParserType] = useState("CLR");
  const [displayedGrammar, setDisplayedGrammar] = useState('');
  const [selectedGrammar, setSelectedGrammar] = useState('grammar1');
  const [grammarText, setGrammarText] = useState('');


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
      parser: parserType,
    };



    try {
      const res = await fetch("http://localhost:8000/api/clr_states/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      console.log("Response from backend:", data);
      alert(`${parserType} Parsing Completed. Check console for results.`);
    } catch (error) {
      console.error("Error:", error);
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
    <div style={{ minHeight: "100vh", backgroundColor: "#f4f6f8", fontFamily: "Arial, sans-serif" }}>
      {/* Header */}
      <header
        style={{
          backgroundColor: "#003366",
          color: "white",
          padding: "1rem 2rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        }}
      >
        <div style={{ flex: 1, textAlign: "center", fontSize: "1.7rem", fontWeight: "bold" }}>
          Parser Visualizer
        </div>
        <div>
         
        </div>
      </header>




      
      <div style={{ padding: '1rem' }}>
        

       
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '1rem' }}>
        <button
  onClick={() => loadGrammar('grammar1')}
  style={{
    padding: '0.5rem 1rem',
    backgroundColor: '#004080',
    color: 'white',
    border: 'none',
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
    border: 'none',
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

      
      <main style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "2rem 1rem" }}>
        <form
          onSubmit={handleSubmit}
          style={{
            backgroundColor: "white",
            padding: "2rem",
            borderRadius: "10px",
            boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
            width: "100%",
            maxWidth: "700px",
          }}
        >
         
          <div style={{ textAlign: 'center', marginBottom: "1.5rem" }}>
            <label htmlFor="grammar-select" style={{ marginRight: '0.5rem', fontWeight: "bold", color: "#444" }}>Choose Grammar:</label>
            <select
              id="grammar-select"
              value={selectedGrammar}
              onChange={(e) => setSelectedGrammar(e.target.value)}
              style={dropdownStyle}
            >
              <option value="grammar1">Grammar 1</option>
              <option value="grammar2">Grammar 2</option>
            </select>
          </div>

          
          <label style={{ display: "block", fontSize: "1.1rem", marginBottom: "0.5rem", color: "#444" }}>
            Input code to be checked:
          </label>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={10}
            style={{
              width: "100%",
              padding: "1rem",
              fontSize: "1rem",
              border: "1px solid #ccc",
              borderRadius: "6px",
              resize: "vertical",
              color: "black",
              backgroundColor: "#fdfdfd",
              fontFamily: "Courier New, monospace",
              marginBottom: "1.5rem",
            }}
            placeholder="Type your grammar/code here..."
          />

          
          <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "bold", color: "#444" }}>
            Select Parser Type:
          </label>
          <select
            value={parserType}
            onChange={(e) => setParserType(e.target.value)}
            style={dropdownStyle}
          >
            <option value="CLR">CLR</option>
            <option value="SLR">SLR</option>
          </select>

          
          <div style={{ textAlign: "center" }}>
            <button
              type="submit"
              style={{
                padding: "0.75rem 2rem",
                fontSize: "1rem",
                backgroundColor: "#003366",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
              }}
            >
              Submit
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
