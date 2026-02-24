def evaluate_answer(context, question, user_answer):
    prompt = f"""
    Context:
    {context}

    Question:
    {question}

    User Answer:
    {user_answer}

    Score from 0 to 10.
    Provide explanation.
    """

    response = model.generate_content(prompt)
    return response.text