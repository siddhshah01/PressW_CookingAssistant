"use client";
import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch("http://localhost:8000/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: "Backend not connected" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">Cooking Assistant</h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about a recipe..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            onClick={handleAsk}
            className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            disabled={loading}
          >
            {loading ? "Loading... (this takes 20-30 seconds)" : "Ask"}
          </button>
        </div>

        {result && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-700">Answer:</h3>
            <p className="bg-gray-100 p-4 rounded whitespace-pre-wrap text-gray-800">
              {result.final_answer || result.error}
            </p>

            {result.cookware_needed && (
              <div className="mt-6">
                <h4 className="text-lg font-semibold mb-2 text-gray-700">Cookware Needed:</h4>
                <ul className="list-disc list-inside text-gray-700">
                  {result.cookware_needed.map((item: string, i: number) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.cookware_missing?.length > 0 && (
              <div className="mt-6 text-red-600">
                <h4 className="text-lg font-semibold mb-2">Missing Cookware:</h4>
                <ul className="list-disc list-inside">
                  {result.cookware_missing.map((item: string, i: number) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
