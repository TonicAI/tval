import logging
from typing import List

from tval.openai_api_util import get_single_message

logger = logging.getLogger()

NEWLINE_INDENT_STRING = "\n    "


def ask_for_similarity_score(
    question: str, reference_answer: str, llm_answer: str, model: str
) -> str:
    """Sends prompt for answer similarity score to OpenAI API, and returns response.

    Parameters
    ----------
    question: str
        The question that was asked.
    reference_answer: str
        The answer that was expected.
    llm_answer: str
        The answer that was generated by the RAG system.
    model: str
        Name of the LLM model to use as the LLM evaluator.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(f"Asking {model} for similarity score for question: {question}")
    main_message = """
    Considering the reference answer and the new answer to the following question, on
    a scale of 0 to 5, where 5 means the same and 0 means not similar, how similar in
    meaning is the new answer to the reference answer? Respond with just a number and
    no additional text.
    """.replace(
        NEWLINE_INDENT_STRING, " "
    ).strip()
    main_message += f"\nQUESTION: {question}\n"
    main_message += f"REFERENCE ANSWER: {reference_answer}\n"
    main_message += f"NEW ANSWER: {llm_answer}\n"

    response_message = get_single_message(main_message, model, temperature=0.0)

    return response_message


def ask_whether_answer_is_consistent_with_context(
    answer: str, context_list: List[str], model: str
) -> str:
    """Sends prompt for answer consistency binary score and returns response.

    Parameters
    ----------
    answer: str
        The answer that was generated by the RAG system.
    context_list: List[str]
        Retrieved context used by the RAG system to make answer.
    model: str
        Name of the LLM model to use as the LLM evaluator.

    Returns
    -------
    str
        Response from OpenAI API.
    """

    logger.debug(f"Asking {model} whether answer hallucinates")
    main_message = """
    Considering the following list of context and then answer, which answers a
    user's query using the context, determine whether the answer contains any
    information that can not be attributed to the intormation in the list of
    context. If the answer contains information that cannot be attributed to the
    context then respond with true. Otherwise response with false. Response with
    either true or false and no additional text.
    """.replace(
        NEWLINE_INDENT_STRING, " "
    ).strip()
    for i, context in enumerate(context_list):
        main_message += f"\n\nCONTEXT {i}:\n{context}\nEND OF CONTEXT {i}"
    main_message += f"\n\nANSWER: {answer}"

    response_message = get_single_message(main_message, model, temperature=0.0)

    return response_message


def ask_whether_context_is_relevant(question: str, context: str, model: str) -> str:
    """Sends prompt to get context relevance to Open AI API and returns response.

    Parameters
    ----------
    question: str
        The question that was asked.
    context: str
        One piece of context retrieved by RAG system.
    model: str
        Name of the LLM model to use as the LLM evaluator.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(f"Asking {model} for context relevance for question {question}")
    main_message = """
    Considering the following question and context, determine whether the context
    is relevant for answering the question. If the context is relevant for answering
    the question, responsd with true. If the context is not relevant for answering
    the question, respond with false. Respond with either true or false and no
    additinal text.
    """.replace(
        NEWLINE_INDENT_STRING, " "
    ).strip()
    main_message += f"\nQUESTION: {question}\n"
    main_message += f"CONTEXT: {context}\n"

    response_message = get_single_message(main_message, model, temperature=0.0)

    return response_message


def ask_whether_answer_contains_context(answer: str, context: str, model: str) -> str:
    """Sends prompt for whether answer contains context and returns response.

    Parameters
    ----------
    answer: str
        The answer that was generated by the RAG system.
    context: str
        One piece of context retrieved by RAG system.
    model: str
        Name of the LLM model to use as the LLM evaluator.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(f"Asking {model} whether answer contains context")
    main_message = """
    Considering the following answer and context, determine whether the answer
    contains information derived from the context. If the answer contains
    information derived from the context, respond with true. If the answer does not
    contain information derived from the context, respond with false.  Respond with
    either true or false and no additinal text.
    """.replace(
        NEWLINE_INDENT_STRING, " "
    ).strip()
    main_message += f"\nANSWER: {answer}\n"
    main_message += f"CONTEXT: {context}\n"

    response_message = get_single_message(main_message, model, temperature=0.0)

    return response_message


def ask_for_main_points(answer: str, model: str) -> str:
    """Sends prompt for main points in answer to Open AI API and returns response.

    Parameters
    ----------
    answer: str
        The answer that was generated by the RAG system.
    model: str
        Name of the LLM model to use as the LLM evaluator.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(f"Asking {model} for bullet list of main points in answer")
    main_message = """
    Write down in a bulleted list using markdown (so each bullet is a "*"), the main
    points in the following answer to a user's query. Respond with the bulleted list
    and no additional text. Only use a single "*" for each bullet and do not use a "*"
    anywhere in your response except for the bullets.
    """.replace(
        NEWLINE_INDENT_STRING, " "
    ).strip()
    main_message += f"\nANSWER: {answer}"

    response_message = get_single_message(main_message, model, temperature=0.0)

    return response_message


def ask_whether_statement_derived_from_context(
    statement: str, context_list: List[str], model: str
) -> str:
    """Sends prompt for whether statement is derived from context and returns response.

    Parameters
    ----------
    statement: str
        The statement to be checked.
    context_list: List[str]
        List of retrieved context to see if statement is derived from this context.
    model: str
        Name of the LLM model to use as the LLM evaluator.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(f"Asking {model} whether statement is derived from context")
    main_message = """
    Considering the following statement and then list of context, determine whether the
    statement can be derived from the context. If the statement can be derived from the
    context response with true. Otherwise response with false. Respond with either true
    or false and no additional text.
    """.replace(
        NEWLINE_INDENT_STRING, " "
    ).strip()
    main_message += f"\n\nSTATEMENT:\n{statement}\nEND OF STATEMENT"
    for i, context in enumerate(context_list):
        main_message += f"\n\nCONTEXT {i}:\n{context}\nEND OF CONTEXT {i}"

    response_message = get_single_message(main_message, model, temperature=0.0)

    return response_message
