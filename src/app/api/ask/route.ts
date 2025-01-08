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
    const index = pinecone.Index('shoe-videos');
    const queryResponse = await index.query({
      vector: embeddingResponse.data[0].embedding,
      topK: 3,
      includeMetadata: true
    });

    // Prepare context from relevant chunks
    const context = queryResponse.matches
      .map(match => match.metadata?.chunk_text || '')
      .join('\n\n');
    
    console.log('Getting shoe recommendations...');
    const response = await openai.chat.completions.create({
      model: "gpt-4-turbo-preview",
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