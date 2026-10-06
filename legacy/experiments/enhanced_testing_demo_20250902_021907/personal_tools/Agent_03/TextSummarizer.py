def execute(parameters, context=None):
    from transformers import pipeline
    try:
        text = parameters.get('text', '')
        max_length = parameters.get('max_length', 150)
        min_length = parameters.get('min_length', 40)
        if not isinstance(text, str) or not text.strip():
            return {"error": "Input text must be a non-empty string."}
        summarizer = pipeline("summarization")
        summary_list = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        summary_text = summary_list[0]['summary_text']
        return {
            "summary": summary_text,
            "original_length": len(text),
            "summary_length": len(summary_text)
        }
    except Exception as e:
        return {"error": str(e)}