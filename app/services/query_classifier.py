def classify_query(question: str) -> str:
    q = question.lower().strip()

    greetings = ["hi", "hello", "hey", "hii", "good morning", "good evening"]
    summary_words = ["summary", "summarize", "overview", "brief", "short note"]
    analysis_words = ["analyze", "analysis", "explain document", "key points", "main points"]

    if q in greetings:
        return "greeting"

    if any(word in q for word in summary_words):
        return "summary"

    if any(word in q for word in analysis_words):
        return "analysis"

    return "question"