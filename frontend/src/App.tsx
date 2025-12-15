import React, { useState } from "react";

type Issue = {
  index: number;
  span: { start: number; end: number };
  issue_type: string;
  explanation_zh: string;
  suggestion: string;
};

type Score = {
  grammar: number;
  vocabulary: number;
  fluency: number;
  overall: number;
};

type Feedback = {
  original: string;
  minimal_correction: string;
  natural_version: string;
  issues: Issue[];
  score: Score;
};

export const App: React.FC = () => {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    setFeedback(null);

    try {
      const res = await fetch("http://localhost:8000/api/grammar/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sentence: input,
          task_type: "quick_fix",
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.detail?.message || "Request failed");
      }

      const data: Feedback = await res.json();
      setFeedback(data);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <header className="header">
        <h1>LingoBridge · Quick Fix</h1>
        <p className="subtitle">
          Correct one English sentence in 30 seconds. The AI will grade you and
          explain the mistakes.
        </p>
      </header>

      <main className="content">
        <section className="card">
          <form onSubmit={handleSubmit}>
            <label className="label">
              Enter one English sentence (it may contain mistakes):
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                rows={4}
                placeholder="e.g. Yesterday I go to park with my friend."
              />
            </label>
            <button type="submit" disabled={loading}>
              {loading ? "Analyzing..." : "Submit & check"}
            </button>
          </form>
          {error && <div className="error">Error: {error}</div>}
        </section>

        {feedback && (
          <section className="card">
            <h2>Result</h2>
            <div className="result-block">
              <h3>Minimal correction</h3>
              <p>{feedback.minimal_correction}</p>
            </div>
            <div className="result-block">
              <h3>More natural version</h3>
              <p>{feedback.natural_version}</p>
            </div>
            <div className="scores">
              <div>
                <span>Grammar</span>
                <strong>{feedback.score.grammar}</strong>
              </div>
              <div>
                <span>Vocabulary</span>
                <strong>{feedback.score.vocabulary}</strong>
              </div>
              <div>
                <span>Fluency</span>
                <strong>{feedback.score.fluency}</strong>
              </div>
              <div>
                <span>Overall</span>
                <strong>{feedback.score.overall}</strong>
              </div>
            </div>

            {feedback.issues.length > 0 && (
              <div className="issues">
                <h3>Issue details</h3>
                <ol>
                  {feedback.issues.map((issue) => (
                    <li key={issue.index}>
                      <strong>{issue.issue_type}</strong> -{" "}
                      <span>{issue.explanation_zh}</span>
                      <div className="suggestion">
                        Suggestion: <code>{issue.suggestion}</code>
                      </div>
                    </li>
                  ))}
                </ol>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
};


