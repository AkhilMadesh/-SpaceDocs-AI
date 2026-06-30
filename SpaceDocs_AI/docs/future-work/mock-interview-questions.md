# Mock Interview Questions — SpaceDocs AI

Practice answering these out loud before presenting this project in interviews.

## RAG Fundamentals
1. What is Retrieval-Augmented Generation, and why is it preferable to
   fine-tuning for this use case?
2. Walk me through what happens, step by step, from a user uploading a PDF
   to receiving an answer.
3. Why do you chunk documents instead of embedding the entire PDF as one
   vector?
4. How did you choose your chunk size and overlap values? What tradeoffs
   did you consider?

## Embeddings & Vector Search
5. What is an embedding, and how does semantic similarity search differ
   from keyword search?
6. Why did you choose BGE-small-en-v1.5 over OpenAI or Gemini embeddings?
   (See ADR-002.)
7. What does cosine similarity measure, and why is it suitable here?

## System Design
8. Why ChromaDB instead of Pinecone or FAISS? (See ADR-001.) What would you
   change if this needed to scale to 10,000 documents?
9. How is your codebase structured to make it easy to swap out the
   embedding model or vector database later?
10. How would you handle multiple users uploading documents simultaneously?

## Guardrails & Reliability
11. How does your system avoid hallucinating answers about topics not in
    the uploaded documents? (See ADR-003.)
12. What is your out-of-domain similarity threshold, and how did you decide
    on that value?
13. What's the difference between your "pre-generation" guardrail and your
    "prompt-level" guardrail? Why use both?

## Evaluation
14. How did you evaluate the quality of your RAG system? What metrics did
    you use?
15. What is RAGAS, and what do faithfulness, answer relevancy, context
    precision, and context recall each measure?
16. What was your hallucination rate, and how did you measure it?

## Tradeoffs & Limitations
17. What are the current limitations of your system, and how would you
    address them given more time?
18. If you had to support scanned/image-only PDFs, what would you add?
19. How would this system need to change to support documents in multiple
    languages?

## Behavioral / Process
20. What was the most difficult bug you encountered, and how did you debug
    it?
21. How did you structure your 5-week timeline across the 14 phases?
22. What would you build next if this became a 3-year project? (See the
    Third-Year Extension Roadmap in the README.)
