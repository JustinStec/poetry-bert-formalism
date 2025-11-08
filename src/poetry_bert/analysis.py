#!/usr/bin/env python3
"""
Text Embedding Analysis Script

This script processes text data using sentence transformers to:
1. Load the mini L6 sentence transformers model
2. Generate embeddings for lists of text strings
3. Calculate various cosine similarity metrics
4. Save results and embeddings
"""

import pandas as pd
import numpy as np
import json
import pickle
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')


class TextEmbeddingAnalyzer:
    """Class to handle text embedding analysis with sentence transformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the analyzer with a sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        print(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully!")
    
    def generate_embeddings(self, text_list: List[str]) -> np.ndarray:
        """
        Function 1: Generate embeddings for a list of text strings.
        
        Args:
            text_list: List of text strings to encode
            
        Returns:
            numpy array of embeddings
        """
        if not text_list or len(text_list) == 0:
            return np.array([])
        
        # Generate embeddings
        embeddings = self.model.encode(text_list, convert_to_numpy=True)
        return embeddings
    
    def save_embeddings(self, embeddings: np.ndarray, filepath: str) -> None:
        """
        Function 2: Save embeddings to a pickle file.
        
        Args:
            embeddings: numpy array of embeddings
            filepath: path to save the pickle file
        """
        with open(filepath, 'wb') as f:
            pickle.dump(embeddings, f)
        print(f"Embeddings saved to {filepath}")
    
    def consecutive_cosine_similarities(self, embeddings: np.ndarray) -> Tuple[float, float]:
        """
        Function 3: Calculate mean and std of consecutive cosine similarities.
        
        Args:
            embeddings: numpy array of embeddings
            
        Returns:
            tuple of (mean, std) of consecutive cosine similarities
        """
        if len(embeddings) < 2:
            return np.nan, np.nan
        
        similarities = []
        for i in range(len(embeddings) - 1):
            # Calculate cosine similarity between consecutive embeddings
            sim = cosine_similarity(
                embeddings[i].reshape(1, -1), 
                embeddings[i + 1].reshape(1, -1)
            )[0, 0]
            similarities.append(sim)
        
        return np.mean(similarities), np.std(similarities)
    
    def first_last_cosine_similarity(self, embeddings: np.ndarray) -> float:
        """
        Function 4: Calculate cosine similarity between first and last embeddings.
        
        Args:
            embeddings: numpy array of embeddings
            
        Returns:
            cosine similarity between first and last embeddings
        """
        if len(embeddings) < 2:
            return np.nan
        
        first_embedding = embeddings[0].reshape(1, -1)
        last_embedding = embeddings[-1].reshape(1, -1)
        
        similarity = cosine_similarity(first_embedding, last_embedding)[0, 0]
        return similarity
    
    def semantic_breadth(self, embeddings: np.ndarray) -> float:
        """
        Function 5: Calculate semantic breadth - mean cosine similarity 
        of each embedding to the averaged embedding of the list.
        
        Args:
            embeddings: numpy array of embeddings
            
        Returns:
            mean cosine similarity to averaged embedding
        """
        if len(embeddings) == 0:
            return np.nan
        
        # Calculate the mean embedding
        mean_embedding = np.mean(embeddings, axis=0).reshape(1, -1)
        
        # Calculate cosine similarity of each embedding to the mean
        similarities = []
        for embedding in embeddings:
            sim = cosine_similarity(
                embedding.reshape(1, -1), 
                mean_embedding
            )[0, 0]
            similarities.append(sim)
        
        return np.mean(similarities)


def load_and_process_data(csv_filepath: str, analyzer: TextEmbeddingAnalyzer) -> pd.DataFrame:
    """
    Load CSV data and process text lists using json.loads.

    Args:
        csv_filepath: path to the CSV file
        analyzer: TextEmbeddingAnalyzer instance

    Returns:
        processed DataFrame
    """
    print(f"Loading data from {csv_filepath}")
    df = pd.read_csv(csv_filepath)

    # Parse the lines column using json.loads
    print("Parsing lines column with json.loads...")
    df['text_parsed'] = df['lines'].apply(json.loads)

    return df


def process_row(row, analyzer: TextEmbeddingAnalyzer) -> dict:
    """
    Process a single row to generate embeddings and calculate metrics.
    
    Args:
        row: pandas Series representing a row
        analyzer: TextEmbeddingAnalyzer instance
        
    Returns:
        dictionary with calculated metrics
    """
    text_list = row['text_parsed']
    
    # Generate embeddings
    embeddings = analyzer.generate_embeddings(text_list)
    
    # Calculate metrics
    consecutive_mean, consecutive_std = analyzer.consecutive_cosine_similarities(embeddings)
    first_last_sim = analyzer.first_last_cosine_similarity(embeddings)
    semantic_breadth_score = analyzer.semantic_breadth(embeddings)
    
    return {
        'embeddings': embeddings,
        'consecutive_cosine_mean': consecutive_mean,
        'consecutive_cosine_std': consecutive_std,
        'first_last_cosine_similarity': first_last_sim,
        'semantic_breadth': semantic_breadth_score
    }


def main():
    """Main function to run the text embedding analysis."""
    
    # Initialize the analyzer with mini L6 model
    analyzer = TextEmbeddingAnalyzer('all-MiniLM-L6-v2')
    
    # Load and process the data
    csv_filepath = '/Users/justin/Repos/AI Project/Data/poetry_all_clean.csv'
    df = load_and_process_data(csv_filepath, analyzer)
    test_mode=True
    if test_mode:
        df=df[:10]
        print('test mode!')
        print(df)
    # Process each ro
    print("Processing rows and calculating metrics...")
    results = []
    embeddings_list = []
    
    for idx, row in df.iterrows():
        print(f"Processing row {idx + 1}/{len(df)}")
        result = process_row(row, analyzer)
        results.append(result)
        embeddings_list.append(result['embeddings'])
    
    # Add results to dataframe
    df['embeddings'] = embeddings_list
    df['consecutive_cosine_mean'] = [r['consecutive_cosine_mean'] for r in results]
    df['consecutive_cosine_std'] = [r['consecutive_cosine_std'] for r in results]
    df['first_last_cosine_similarity'] = [r['first_last_cosine_similarity'] for r in results]
    df['semantic_breadth'] = [r['semantic_breadth'] for r in results]
    
    # Save embeddings as pickle file
    print("Saving embeddings to pickle file...")
    all_embeddings = df['embeddings'].tolist()
    analyzer.save_embeddings(all_embeddings, '/Users/justin/Repos/AI Project/Data/embeddings.pkl')
    
    # Save final CSV without embeddings column
    print("Saving results to CSV...")
    df_final = df.drop(['embeddings', 'text_parsed'], axis=1)
    df_final.to_csv('/Users/justin/Repos/AI Project/Data/results_with_metrics.csv', index=False)
    
    print("Analysis complete!")
    print(f"Results saved to: results_with_metrics.csv")
    print(f"Embeddings saved to: embeddings.pkl")
    
    # Display summary statistics
    print("\nSummary Statistics:")
    print(df_final[['consecutive_cosine_mean', 'consecutive_cosine_std', 
                   'first_last_cosine_similarity', 'semantic_breadth']].describe())


if __name__ == "__main__":
    main()