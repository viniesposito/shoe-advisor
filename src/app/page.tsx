"use client";

import React, { useState } from "react";
import { Loader2, ExternalLink } from "lucide-react";
import { ShoeIcon } from "./components/ShoeIcon";

interface Recommendation {
  model: string;
  description: string;
}

interface Source {
  title: string;
  video_id: string;
}

function hasRecommendations(text: string): boolean {
  return text.includes("**") && text.includes("-");
}

function parseResponse(text: string): Recommendation[] {
  if (!hasRecommendations(text)) {
    return [];
  }

  const sections = text.split("\n");
  const recommendations: Recommendation[] = [];
  let currentModel = "";

  for (const section of sections) {
    const trimmedSection = section.trim();
    if (trimmedSection.startsWith("-") && trimmedSection.includes("**")) {
      const modelMatch = trimmedSection.match(/\*\*(.*?)\*\*/);
      if (modelMatch) {
        currentModel = modelMatch[1].trim();
      }
    } else if (trimmedSection.startsWith("-") && currentModel) {
      const description = trimmedSection.replace(/^-\s*/, "").trim();
      recommendations.push({
        model: currentModel,
        description: description,
      });
      currentModel = "";
    }
  }

  return recommendations;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [data, setData] = useState<{
    answer: string;
    sources: Source[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setRecommendations([]);
    setData(null);

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "no-cache, no-store, must-revalidate",
          Pragma: "no-cache",
        },
        body: JSON.stringify({ question: query }),
      });

      const responseData = await res.json();

      if (responseData.error) {
        setError(responseData.error);
        return;
      }

      setData(responseData);
      const parsed = parseResponse(responseData.answer);
      setRecommendations(parsed);
    } catch (err) {
      setError("Failed to get recommendations. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#2D3047] px-4 py-8 md:py-12 font-mono lowercase flex flex-col">
      {/* Title Section */}
      <div className="max-w-2xl mx-auto text-center mb-8 md:mb-12">
        <h1 className="text-2xl md:text-4xl font-bold mb-3 md:mb-4 text-[#FF9F1C]">
          running shoe finder
        </h1>
        <p className="text-[#E4D9FF] text-base md:text-md">
          enter your favorite shoes, discover your next pair.
        </p>
      </div>

      {/* Search Section */}
      <div className="max-w-xl mx-auto mb-16 md:mb-32 w-full px-4">
        <form
          onSubmit={handleSubmit}
          className="flex flex-col md:flex-row gap-3"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="nike pegasus, brooks ghost..."
            className="w-full md:flex-1 px-4 md:px-6 py-3 md:py-4 rounded-full border-2 border-[#FF9F1C] bg-[#1F2132] text-white placeholder:text-[#E4D9FF]/50 focus:outline-none focus:ring-2 focus:ring-[#FF9F1C] focus:border-transparent text-base"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading}
            className="group w-full md:w-auto px-6 md:px-8 py-3 md:py-4 bg-[#FF9F1C] text-[#2D3047] rounded-full hover:bg-[#FFB849] disabled:opacity-50 transition-colors flex items-center justify-center gap-2 font-bold"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} /> searching...
              </>
            ) : (
              <>
                <ShoeIcon
                  size={20}
                  className="transition-transform group-hover:scale-125 duration-200"
                />
              </>
            )}
          </button>
        </form>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-[#E63946] text-white rounded-lg text-center text-sm md:text-base">
            {error}
          </div>
        )}
      </div>

      {/* Track and Results Section */}
      {(recommendations.length > 0 || (data?.answer && !loading)) && (
        <div className="relative max-w-3xl mx-auto flex-1 min-h-[500px] mb-16 md:mb-24">
          {/* Track Container */}
          <div className="absolute -inset-8 md:-inset-20 -rotate-6">
            {/* Lane Lines - now in orange with decreasing opacity */}
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="absolute border-[2px] md:border-[3px] rounded-[200px]"
                style={{
                  top: `${i * 12}px`,
                  right: `${i * 12}px`,
                  bottom: `${i * 12}px`,
                  left: `${i * 12}px`,
                  borderColor: `rgba(176, 51, 17, ${0.7 - i * 0.1})`,
                }}
              />
            ))}
          </div>

          {/* Results Container */}
          <div className="relative mx-4 md:mx-12 bg-[#1F2132]/90 backdrop-blur-sm rounded-3xl md:rounded-[60px] p-4 md:p-8 shadow-2xl">
            {/* No recommendations message */}
            {!loading && recommendations.length === 0 && data?.answer && (
              <div className="min-h-[300px] md:min-h-[400px] text-[#E4D9FF] flex items-center justify-center text-center text-base md:text-lg p-4 md:p-8">
                {data.answer}
              </div>
            )}

            {/* Recommendations */}
            {recommendations.length > 0 && (
              <div className="space-y-6 md:space-y-8">
                {/* Recommendations Cards */}
                <div className="grid gap-4 md:gap-6">
                  {recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      className="bg-[#2D3047] p-4 md:p-6 rounded-xl md:rounded-2xl border-2 border-[#FF9F1C]/20 hover:border-[#FF9F1C]/40 transition-colors"
                    >
                      <h3 className="text-[#FF9F1C] text-lg md:text-xl font-bold mb-2 md:mb-3">
                        {rec.model}
                      </h3>
                      <p className="text-[#E4D9FF] leading-relaxed text-sm md:text-base">
                        {rec.description}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Sources Section */}
                {data?.sources && data.sources.length > 0 && (
                  <div className="pt-6 md:pt-8 border-t-2 border-[#FF9F1C]/20">
                    <h3 className="text-[#FF9F1C] font-bold mb-3 md:mb-4 text-sm md:text-base">
                      you might find these videos interesting:
                    </h3>
                    <ul className="space-y-2 md:space-y-3">
                      {data.sources.map((source, idx) => (
                        <li key={idx} className="flex items-start gap-2 group">
                          <ExternalLink
                            size={16}
                            className="mt-1 flex-shrink-0 text-[#FF9F1C]"
                          />
                          <a
                            href={`https://youtube.com/watch?v=${source.video_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs md:text-sm text-[#E4D9FF] group-hover:text-[#FF9F1C] transition-colors"
                          >
                            {source.title.toLowerCase()}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
