"use client";

export default function Output({ result }) {
  if (!result) return null;

  const { status, clr_table, canonical_items, parsing_steps, first_follow, error } = result;

  const tableStyle = "border border-gray-700 px-4 py-2";
  const thStyle = "bg-gray-700 text-white font-semibold";

  return (
    <div className="bg-black text-white min-h-screen px-6 py-10 space-y-6">
      <h1 className="text-3xl font-bold text-green-400 text-center">{status}</h1>

      {/* First & Follow Sets */}
      <section className="bg-gray-800 p-4 rounded-md shadow-md overflow-x-auto">
        <h2 className="text-xl font-semibold mb-2">First & Follow Sets</h2>
        <table className="min-w-full border-collapse">
          <thead>
            <tr>
              <th className={`${tableStyle} ${thStyle}`}>Non-Terminal</th>
              <th className={`${tableStyle} ${thStyle}`}>First</th>
              <th className={`${tableStyle} ${thStyle}`}>Follow</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(first_follow).map(([nonTerminal, sets], i) => (
              <tr key={i}>
                <td className={tableStyle}>{nonTerminal}</td>
                <td className={tableStyle}>{sets.first.join(', ')}</td>
                <td className={tableStyle}>{sets.follow.join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      
      {/* Parse Table */}
      <section className="bg-gray-900 p-4 rounded-md shadow-md overflow-x-auto">
        <h2 className="text-xl font-semibold mb-2 text-white">CLR(1) Parse Table</h2>
        <table className="min-w-full border-collapse text-white">
          <thead>
            <tr>
              <th className="border px-2 py-1">State</th>
              {Array.from(
                new Set(
                  Object.values(clr_table).flatMap(row => Object.keys(row))
                )
              )
                .sort()
                .map(symbol => (
                  <th key={symbol} className="border px-2 py-1">{symbol}</th>
                ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(clr_table).map(([state, actions]) => (
              <tr key={state}>
                <td className="border px-2 py-1">{state}</td>
                {Array.from(
                  new Set(
                    Object.values(clr_table).flatMap(row => Object.keys(row))
                  )
                )
                  .sort()
                  .map(symbol => (
                    <td key={symbol} className="border px-2 py-1 text-center">
                      {Array.isArray(actions[symbol])
                        ? actions[symbol].join(', ')
                        : actions[symbol] || ''}
                    </td>
                  ))}
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Canonical Items */}
      <section className="bg-gray-800 p-4 rounded-md shadow-md">
        <h2 className="text-xl font-semibold mb-2">Canonical Items</h2>
        <table className="table-auto w-full text-left border border-gray-700">
          <thead>
            <tr className="bg-gray-700">
              <th className="p-2 border border-gray-600">State No</th>
              <th className="p-2 border border-gray-600">Items</th>
            </tr>
          </thead>
          <tbody>
            {canonical_items.map((state, index) => (
              <tr key={index}>
                <td className="p-2 border border-gray-600">{state.state_no}</td>
                <td className="p-2 border border-gray-600">
                  <ul className="list-disc pl-4">
                    {state.items.map((rule, i) => (
                      <li key={i}>{rule}</li>
                    ))}
                  </ul>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Parsing Steps */}
      <section className="bg-gray-800 p-4 rounded-md shadow-md overflow-x-auto">
        <h2 className="text-xl font-semibold mb-2">Parsing Steps</h2>
        <table className="min-w-full border-collapse">
          <thead>
            <tr>
              <th className={`${tableStyle} ${thStyle}`}>Step</th>
              <th className={`${tableStyle} ${thStyle}`}>Stack</th>
              <th className={`${tableStyle} ${thStyle}`}>Input</th>
              <th className={`${tableStyle} ${thStyle}`}>Action</th>
            </tr>
          </thead>
          <tbody>
            {parsing_steps.map((step, index) => (
              <tr key={index}>
                <td className={tableStyle}>{index}</td>
                <td className={tableStyle}>{step.stack}</td>
                <td className={tableStyle}>{step.input}</td>
                <td className={tableStyle}>{step.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>


      {/* Error Section */}
      {error && (
        <section className="bg-red-800 p-4 rounded-md shadow-md">
          <h2 className="text-xl font-semibold mb-2 text-red-300">Error</h2>
          <pre>{error}</pre>
        </section>
      )}
    </div>
  );
}
