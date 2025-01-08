// src/app/api/ask/route.ts
import { NextResponse } from 'next/server';
import OpenAI from 'openai';
import { Pinecone } from '@pinecone-database/pinecone';

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Initialize Pinecone client
const pinecone = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY!
});

const SYSTEM_PROMPT = `You are a knowledgeable running shoe expert. 
Use the provided context and your knowledge to suggest similar running shoes. Your answer should contain just a few running shoes and one brief bullet point with the reasoning for the suggestion.

Format your response exactly like this example:
- **Nike Pegasus 41**
  - A solid entry-level model with good stability and comfort.
- **Nike Invincible 3**
  - Maximum cushioning and bounce for recovery runs.

Use 2-4 shoe recommendations, each with:
- Model name in bold between two newlines
- Description on a new indented line starting with a bullet point
- Keep descriptions concise (one sentence)
- Don't add any concluding text after recommendations`;

export async function POST(request: Request) {
  console.log('Received API request');
  
  try {
    const { question } = await request.json();
    console.log('Received question:', question);

    if (!question || typeof question !== 'string') {
      console.error('Invalid question format:', question);
      return NextResponse.json(
        { error: 'Invalid question format' },
        { status: 400 }
      );
    }

    // Get embedding for the question
    console.log('Getting embedding for question...');
    const embeddingResponse = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: question
    });
    
    // Query Pinecone
    console.log('Querying Pinecone...');
    const index = pinecone.Index('running-shoes');
    const queryResponse = await index.query({
      vector: embeddingResponse.data[0].embedding,
      topK: 3,
      includeMetadata: true
    });

    console.log('Match scores:', queryResponse.matches?.map(m => ({
      score: m.score,
      title: m.metadata?.title,
      snippet: typeof m.metadata?.chunk_text === 'string' ? 
      m.metadata.chunk_text.slice(0, 100) + '...' : 
      'No text available'
    })));

    // Filter matches based on score
    const SIMILARITY_THRESHOLD = 0.3;  // Adjust this value as needed
    const relevantMatches = queryResponse.matches?.filter(match => match.score && match.score > SIMILARITY_THRESHOLD) || [];

    // Check if we found any relevant matches
    if (relevantMatches.length === 0) {
      console.log('No relevant matches found (similarity scores too low)');
      return NextResponse.json({
        answer: "I couldn't find any relevant shoe recommendations based on your query. could you please try inputting a different shoe?",
        sources: []
      });
    }

    // Prepare context from relevant chunks
    const context = relevantMatches
      .map(match => match.metadata?.chunk_text || '')
      .join('\n\n');
    
    console.log('Getting shoe recommendations...');
    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: `Context:\n${context}\n\nUser Question: ${question}\n\nPlease provide recommendations based on the context above.` }
      ],
      temperature: 0.7
    });

    const answer = response.choices[0].message.content;
    console.log('Processed answer:', answer);

    // Get unique video sources
    const sources = queryResponse.matches
      .filter((match, index, self) => 
        index === self.findIndex(m => m.metadata?.video_id === match.metadata?.video_id)
      )
      .map(match => ({
        title: match.metadata?.title || '',
        video_id: match.metadata?.video_id || ''
      }));

    // Return formatted response
    const finalResponse = {
      answer,
      sources
    };
    console.log('Returning response:', JSON.stringify(finalResponse, null, 2));
    
    return NextResponse.json(finalResponse);
    
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    const errorStack = err instanceof Error ? err.stack : 'No stack trace';
    const errorType = err instanceof Error ? err.constructor.name : 'Unknown';
    
    console.error('Request error:', errorMessage);
    console.error('Error stack:', errorStack);
    
    return NextResponse.json(
      { 
        error: 'Failed to process request', 
        details: errorMessage,
        type: errorType
      },
      { status: 500 }
    );
  }
}