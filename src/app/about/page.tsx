"use client";

import Link from "next/link";
import { ArrowLeft, Github } from "lucide-react";

export default function About() {
  return (
    <main className="min-h-screen bg-[#2D3047] px-4 py-8 md:py-12 font-mono lowercase">
      <div className="max-w-2xl mx-auto">
        {/* Back Button */}
        <Link
          href="/"
          className="inline-flex items-center text-[#ff8884] hover:text-[#fff8f0] mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          back to shoe finder
        </Link>

        {/* Title */}
        <h1 className="text-2xl md:text-4xl font-bold mb-8 text-[#FF9F1C]">
          about this project
        </h1>

        {/* Content */}
        <div className="space-y-6 text-[#E4D9FF]">
          <p>
            running shoe finder uses AI to help you narrow down your search for
            your next pair of running shoes.
          </p>

          <div>
            <h2 className="text-[#FF9F1C] text-lg mb-2">how it works</h2>
            <p>
              this uses AI to analyze thousands of running shoe reviews from
              running YouTube channels. when you enter a shoe, the system finds
              relevant comparisons and alternatives to suggest shoes that match
              the inputted shoe.
            </p>
          </div>

          <div>
            <h2 className="text-[#FF9F1C] text-lg mb-2">tech stack</h2>
            <p>
              built with next.js, python, openai, and pinecone. this uses RAG
              (retrieval augmented generation) to provide shoe recommendations
              based on real expert reviews.
            </p>
          </div>

          {/* GitHub Link */}
          <div className="pt-4">
            <a
              href="https://github.com/viniesposito/shoe-advisor"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-[#ff8884] hover:text-[#fff8f0] transition-colors"
            >
              <Github className="w-5 h-5 mr-2" />
              view source code on github
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}
