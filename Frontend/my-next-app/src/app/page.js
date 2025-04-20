"use client";

import { useState } from 'react';

export default function Home() {
  const [rules, setRules] = useState(['']);

  const handleInputChange = (index, value) => {
    const newRules = [...rules];
    newRules[index] = value;
    setRules(newRules);
  };

  const addRuleInput = () => {
    setRules([...rules, '']);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Prepare payload
    const payload = {
      productions: rules,
      firstfollow: {
        // Example structure - replace with actual FIRST/FOLLOW data if available
        S: { first: ['a'], follow: ['$'] },
        A: { first: ['b'], follow: ['c'] },
      },
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
      alert("CLR States received! Check console.");

    } catch (error) {
      console.error("Error:", error);
      alert("Something went wrong!");
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>CLR Parser</h1>
      <form onSubmit={handleSubmit}>
        {rules.map((rule, index) => (
          <div key={index} style={{ marginBottom: '1rem' }}>
            <input
              type="text"
              placeholder={`Grammar Rule ${index + 1}`}
              value={rule}
              onChange={(e) => handleInputChange(index, e.target.value)}
              style={{
                padding: '0.5rem',
                width: '300px',
                fontSize: '1rem',
              }}
            />
          </div>
        ))}

        <button type="button" onClick={addRuleInput} style={{ marginRight: '1rem' }}>
          ➕ Add Rule
        </button>

        <button type="submit">Submit</button>
      </form>
    </div>
  );
}
