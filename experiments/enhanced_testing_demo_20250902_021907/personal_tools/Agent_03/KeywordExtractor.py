def execute(parameters, context=None):
    """KeywordExtractor: Extracts top keywords from input text using frequency analysis."""
    import re
    from collections import Counter

    try:
        text = parameters.get('text', '')
        top_n = parameters.get('top_n', 10)
        language = parameters.get('language', 'en')

        # Basic stopwords list for English; extend as needed
        stopwords = {
            'en': {
                'a', 'an', 'the', 'and', 'or', 'but', 'if', 'while', 'with', 'to', 'of', 'in', 'on', 'for', 'by', 'as', 'at', 'from'
            }
        }

        # Normalize text: lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)

        # Tokenize
        tokens = text.split()

        # Remove stopwords
        filtered_tokens = [t for t in tokens if t not in stopwords.get(language, set()) and len(t) > 1]

        # Count frequencies
        counts = Counter(filtered_tokens)

        # Get top N keywords
        most_common = counts.most_common(top_n)

        # Prepare result
        result = [{"keyword": word, "score": float(freq) / len(filtered_tokens)} for word, freq in most_common]

        return {"keywords": result}
    except Exception as e:
        return {"error": str(e)}