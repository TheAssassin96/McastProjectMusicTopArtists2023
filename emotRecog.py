import text2emotion as te
from sklearn.feature_extraction.text import TfidfVectorizer

# Define the song lyric

def analyze_lyric(lyric):
    # Tokenize the lyric
    tokens = lyric.split()
    # Vectorize the tokens using TF-IDF
    vectorizer = TfidfVectorizer()
    vectorizer.fit_transform(tokens)
    vectorized_lyric = vectorizer.transform([lyric]).toarray()
    # Use the text2emotion library to predict the emotions in the lyric
    emotions = te.get_emotion(lyric)
    # Print the predicted emotions and the vectorized lyric
    # give me the most common emotion    
    return emotions

    
