# Running Shoe Finder 👟

I was spending too much time watching running shoe reviews on YouTube so I had GPT watch all of them so you don't have to.

<p align="center"> 
    <img src="/assets/app_screnshot.png" width="200">
</p>

## Features

- **Smart Recommendations**: Enter your favorite running shoes and get personalized suggestions based on real expert reviews
- **AI-Powered Analysis**: Uses GPT-4 and advanced embedding search to understand shoe characteristics and find relevant matches
- **Expert Sources**: Pulls data from trusted YouTube running channels to ensure high-quality recommendations

## Tech Stack

### Web Application

- **Frontend**: Next.js 14 with App Router, TailwindCSS, TypeScript
- **API Routes**: Next.js API routes for handling requests
- **Deployment**: Vercel

### Data Processing (One-time Setup)

Python scripts are used only for initial data collection and processing:

- YouTube transcript collection
- Text chunking and embedding generation
- Vector database population

The live application itself runs entirely on Next.js and doesn't require Python.

### Core Services

- **OpenAI**: GPT-4 and Embeddings API
- **Pinecone**: Vector database for storing and searching review embeddings
- **YouTube Data API**: Used only during data collection

## How It Works

1. **Data Collection** (Done beforehand using Python):

   - Collect running shoe reviews from expert YouTube channels
   - Process transcripts into meaningful chunks
   - Generate embeddings and store in Pinecone

2. **Live Application Flow**:
   - User inputs a shoe name
   - Next.js API route searches Pinecone for relevant reviews
   - GPT-4 analyzes the context and generates personalized recommendations
   - Results are displayed with explanations and source videos

## Local Development

### Prerequisites

- Node.js 18+
- OpenAI API Key
- Pinecone API Key

For data collection (optional):

- Python 3.13+
- YouTube Data API Key

### Setup

1. Clone the repository:

```bash
git clone https://github.com/viniesposito/shoe-advisor
cd shoe-advisor
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
```

4. Run the development server:

```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

### Data Collection (Optional)

If you want to collect fresh data:

1. Set up Python environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Add to your `.env`:

```env
YOUTUBE_API_KEY=your_key_here
```

3. Run collection scripts:

```bash
python src/lib/youtube_transcript_getter.py
python src/lib/process_transcripts.py
python src/lib/pinecone_setup.py
```

## Contributing

Contributions are welcome! Whether it's:

- Adding new features
- Fixing bugs
- Improving documentation
- Suggesting improvements

Please feel free to create an issue or submit a pull request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Running shoe reviews sourced from awesome YouTube channels:
  - Kofuzi
  - Seth James DeMoor
  - Ben Parkes
  - The Run Testers
  - Believe in the Run
- Built with Next.js and various open-source tools

## Contact

Project Link: [https://github.com/viniesposito/shoe-advisor](https://github.com/viniesposito/shoe-advisor)
