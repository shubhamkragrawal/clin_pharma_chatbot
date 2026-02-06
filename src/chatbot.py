import ollama
from indexer import EmbeddingIndexer


class ChatBot:
    def __init__(self, config=None):
        # Default configuration
        if config is None:
            config = {
                'base_url': 'http://localhost:11434',
                'model': 'mistral',
                'timeout': 120,
                'temperature': 0.7,
                'max_tokens': 2000
            }
        
        self.config = config
        self.model_name = config['model']
        self.base_url = config['base_url']
        self.timeout = config.get('timeout', 120)
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2000)
        
        # Initialize Ollama client
        self.client = ollama.Client(host=self.base_url)
        
        self.indexer = EmbeddingIndexer()
        self.conversation_history = []
    
    def get_relevant_context(self, query, n_results=5):
        """Retrieve relevant chunks from vector DB"""
        results = self.indexer.search(query, n_results=n_results)
        
        context_parts = []
        sources = []
        
        if results['documents'] and len(results['documents'][0]) > 0:
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                context_parts.append(doc)
                sources.append(f"{metadata['filename']} (Page {metadata['page']})")
        
        context = "\n\n".join(context_parts)
        return context, sources
    
    def generate_response(self, user_query):
        """Generate response using Ollama"""
        # Get relevant context
        context, sources = self.get_relevant_context(user_query)
        
        if not context:
            return "I couldn't find relevant information in the documents.", []
        
        # Create prompt
        prompt = f"""You are a helpful assistant that answers questions based on the provided context from PDF documents.

Context from documents:
{context}

Question: {user_query}

Answer the question based only on the context provided. If the context doesn't contain enough information to answer the question, say so. Be concise and specific."""
        
        try:
            # Call Ollama with configured parameters
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens,
                }
            )
            
            answer = response['message']['content']
            return answer, sources
            
        except Exception as e:
            return f"Error generating response: {str(e)}", []
    
    def chat(self, user_query):
        """Main chat function"""
        answer, sources = self.generate_response(user_query)
        
        # Store in history
        self.conversation_history.append({
            "query": user_query,
            "answer": answer,
            "sources": sources
        })
        
        return answer, sources
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


if __name__ == "__main__":
    # Test the chatbot
    config = {
        'base_url': 'http://localhost:11434',
        'model': 'mistral',
        'timeout': 120,
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    bot = ChatBot(config=config)
    
    while True:
        query = input("\nYou: ")
        if query.lower() in ['exit', 'quit']:
            break
        
        answer, sources = bot.chat(query)
        print(f"\nBot: {answer}")
        if sources:
            print(f"\nSources: {', '.join(set(sources))}")