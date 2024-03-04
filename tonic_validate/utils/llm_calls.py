import logging
from typing import List
from tonic_validate.classes.exceptions import ContextLengthException
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


def similarity_score_call(
    question: str, reference_answer: str, llm_answer: str, openai_service: OpenAIService
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
    openai_service: OpenAIService
        The OpenAI Service which allows for communication with the OpenAI API.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(
        f"Asking {openai_service.model} for similarity score for question: {question}"
    )
    main_message = (
        "Considering the reference answer and the new answer to the following "
        "question, on a scale of 0 to 5, where 5 means the same and 0 means not at all "
        "similar, how similar in meaning is the new answer to the reference answer? "
        "Respond with just a number and no additional text."
    )
    main_message += f"\nQUESTION: {question}\n"
    main_message += f"REFERENCE ANSWER: {reference_answer}\n"
    main_message += f"NEW ANSWER: {llm_answer}\n"

    try:
        response_message = openai_service.get_response(main_message)
    except ContextLengthException as e:
        question_tokens = openai_service.get_token_count(question)
        reference_answer_tokens = openai_service.get_token_count(reference_answer)
        llm_answer_tokens = openai_service.get_token_count(llm_answer)
        total_tokens = openai_service.get_token_count(main_message)
        base_prompt_tokens = (
            total_tokens - question_tokens - reference_answer_tokens - llm_answer_tokens
        )
        raise ContextLengthException(
            "Similarity score prompt too long to score item. OpenAI returned the following error message"
            "\n----------"
            f"\n{e}"
            "\n----------"
            "\nSee details below for breakdown of token counts"
            f"\nQuestion tokens: {question_tokens}"
            f"\nReference answer tokens: {reference_answer_tokens}"
            f"\nNew answer tokens: {llm_answer_tokens}"
            f"\nBase prompt tokens: {base_prompt_tokens}"
            f"\nTotal tokens: {total_tokens}"
        ) from e

    return response_message


def answer_consistent_with_context_call(
    answer: str, context_list: List[str], openai_service: OpenAIService
) -> str:
    """Sends prompt for answer consistency binary score and returns response.

    Parameters
    ----------
    answer: str
        The answer that was generated by the RAG system.
    context_list: List[str]
        Retrieved context used by the RAG system to make answer.
    openai_service: OpenAIService
        The OpenAI Service which allows for communication with the OpenAI API.

    Returns
    -------
    str
        Response from OpenAI API.
    """

    logger.debug(f"Asking {openai_service.model} whether answer hallucinates")
    main_message = (
        "Consider the following list of context and answer. The answer answers a "
        "user's query using the context. Determine whether the answer contains any "
        "information that cannot be attributed to the information in the list of "
        "context. If the answer contains information that cannot be attributed to the "
        "context then respond with false. Otherwise respond with true. Respond with "
        "either true or false and no additional text."
    )
    for i, context in enumerate(context_list):
        main_message += f"\n\nCONTEXT {i}:\n{context}\nEND OF CONTEXT {i}"
    main_message += f"\n\nANSWER: {answer}"

    try:
        response_message = openai_service.get_response(main_message)
    except ContextLengthException as e:
        answer_tokens = openai_service.get_token_count(answer)
        context_tokens = 0
        for context in context_list:
            context_tokens += openai_service.get_token_count(context)
        total_tokens = openai_service.get_token_count(main_message)
        base_prompt_tokens = total_tokens - context_tokens - answer_tokens
        raise ContextLengthException(
            "Consistency prompt too long to score item. OpenAI returned the following error message"
            "\n----------"
            f"\n{e}"
            "\n----------"
            "\nSee details below for breakdown of token counts"
            f"\nAnswer tokens: {answer_tokens}"
            f"\nContext tokens: {context_tokens}"
            f"\nBase prompt tokens: {base_prompt_tokens}"
            f"\nTotal tokens: {total_tokens}"
        ) from e

    return response_message


def context_relevancy_call(
    question: str, context: str, openai_service: OpenAIService
) -> str:
    """Sends prompt to get context relevance to Open AI API and returns response.

    Parameters
    ----------
    question: str
        The question that was asked.
    context: str
        One piece of context retrieved by RAG system.
    openai_service: OpenAIService
        The OpenAI Service which allows for communication with the OpenAI API.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(
        f"Asking {openai_service.model} for context relevance for question {question}"
    )
    main_message = (
        "Considering the following question and context, determine whether the context "
        "is relevant for answering the question. If the context is relevant for "
        "answering the question, respond with true. If the context is not relevant for "
        "answering the question, respond with false. Respond with either true or false "
        "and no additional text."
    )
    main_message += f"\nQUESTION: {question}\n"
    main_message += f"CONTEXT: {context}\n"

    try:
        response_message = openai_service.get_response(main_message)
    except ContextLengthException as e:
        question_tokens = openai_service.get_token_count(question)
        context_tokens = openai_service.get_token_count(context)
        total_tokens = openai_service.get_token_count(main_message)
        base_prompt_tokens = total_tokens - question_tokens - context_tokens
        raise ContextLengthException(
            "Relevance prompt too long to score item. OpenAI returned the following error message"
            "\n----------"
            f"\n{e}"
            "\n----------"
            "\nSee details below for breakdown of token counts"
            f"\nQuestion tokens: {question_tokens}"
            f"\nContext tokens: {context_tokens}"
            f"\nBase prompt tokens: {base_prompt_tokens}"
            f"\nTotal tokens: {total_tokens}"
        ) from e

    return response_message


def answer_contains_context_call(
    answer: str, context: str, openai_service: OpenAIService
) -> str:
    """Sends prompt for whether answer contains context and returns response.

    Parameters
    ----------
    answer: str
        The answer that was generated by the RAG system.
    context: str
        One piece of context retrieved by RAG system.
    openai_service: OpenAIService
        The OpenAI Service which allows for communication with the OpenAI API.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(f"Asking {openai_service.model} whether answer contains context")
    main_message = (
        "Considering the following answer and context, determine whether the answer "
        "contains information derived from the context. If the answer contains "
        "information derived from the context, respond with true. If the answer does "
        "not contain information derived from the context, respond with false. "
        "Respond with either true or false and no additional text."
    )
    main_message += f"\nANSWER: {answer}\n"
    main_message += f"CONTEXT: {context}\n"

    try:
        response_message = openai_service.get_response(main_message)
    except ContextLengthException as e:
        answer_tokens = openai_service.get_token_count(answer)
        context_tokens = openai_service.get_token_count(context)
        total_tokens = openai_service.get_token_count(main_message)
        base_prompt_tokens = total_tokens - answer_tokens - context_tokens
        raise ContextLengthException(
            "Contains context prompt too long to score item. OpenAI returned the following error message"
            "\n----------"
            f"\n{e}"
            "\n----------"
            "\nSee details below for breakdown of token counts"
            f"\nAnswer tokens: {answer_tokens}"
            f"\nContext tokens: {context_tokens}"
            f"\nBase prompt tokens: {base_prompt_tokens}"
            f"\nTotal tokens: {total_tokens}"
        ) from e

    return response_message


def main_points_call(answer: str, openai_service: OpenAIService) -> str:
    """Sends prompt for main points in answer to Open AI API and returns response.

    Parameters
    ----------
    answer: str
        The answer that was generated by the RAG system.
    openai_service: OpenAIService
        The OpenAI Service which allows for communication with the OpenAI API.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(
        f"Asking {openai_service.model} for bullet list of main points in answer"
    )
    main_message = (
        "Using a bulleted list in markdown (so each bullet is a '*'), write down the "
        "main points in the following answer to a user's query. Respond with the "
        "bulleted list and no additional text. Only use a single '*' for each bullet "
        "and do not use a '*' anywhere in your response except for the bullets."
    )
    main_message += f"\nANSWER: {answer}"

    try:
        response_message = openai_service.get_response(main_message)
    except ContextLengthException as e:
        answer_tokens = openai_service.get_token_count(answer)
        total_tokens = openai_service.get_token_count(main_message)
        base_prompt_tokens = total_tokens - answer_tokens
        raise ContextLengthException(
            "Main points prompt too long to score item. OpenAI returned the following error message"
            "\n----------"
            f"\n{e}"
            "\n----------"
            "\nSee details below for breakdown of token counts"
            f"\nAnswer tokens: {answer_tokens}"
            f"\nBase prompt tokens: {base_prompt_tokens}"
            f"\nTotal tokens: {total_tokens}"
        ) from e

    return response_message


def statement_derived_from_context_call(
    statement: str, context_list: List[str], openai_service: OpenAIService
) -> str:
    """Sends prompt for whether statement is derived from context and returns response.

    Parameters
    ----------
    statement: str
        The statement to be checked.
    context_list: List[str]
        List of retrieved context to see if statement is derived from this context.
    openai_service: OpenAIService
        The OpenAI Service which allows for communication with the OpenAI API.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(
        f"Asking {openai_service.model} whether statement is derived from context"
    )
    main_message = (
        "Considering the following statement and then list of context, determine "
        "whether the statement can be derived from the context. If the statement can "
        "be derived from the context response with true. Otherwise response with "
        "false. Respond with either true or false and no additional text."
    )
    main_message += f"\n\nSTATEMENT:\n{statement}\nEND OF STATEMENT"
    for i, context in enumerate(context_list):
        main_message += f"\n\nCONTEXT {i}:\n{context}\nEND OF CONTEXT {i}"

    try:
        response_message = openai_service.get_response(main_message)
    except ContextLengthException as e:
        statement_tokens = openai_service.get_token_count(statement)
        context_tokens = 0
        for context in context_list:
            context_tokens += openai_service.get_token_count(context)
        total_tokens = openai_service.get_token_count(main_message)
        base_prompt_tokens = total_tokens - context_tokens - statement_tokens
        raise ContextLengthException(
            "Derived from context prompt too long to score item. OpenAI returned the following error message"
            "\n----------"
            f"\n{e}"
            "\n----------"
            "\nSee details below for breakdown of token counts"
            f"\nStatement tokens: {statement_tokens}"
            f"\nContext tokens: {context_tokens}"
            f"\nBase prompt tokens: {base_prompt_tokens}"
            f"\nTotal tokens: {total_tokens}"
        ) from e

    return response_message


def contains_duplicate_information(
    statement: str, openai_service: OpenAIService
) -> str:
    """Sends prompt for whether statement contains duplicate information and returns response.

    Parameters
    ----------
    statement: str
        The statement to be checked.
    openai_service: OpenAIService
        The OpenAI Service which allows for communication with the OpenAI API.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    logger.debug(
        f"Asking {openai_service.model} whether statement contains duplicate information"
    )
    main_message = (
        "Considering the following statement, determine whether the statement contains "
        "duplicate information. If the statement contains duplicate information, respond "
        "with 'true'. If the statement does not contain duplicate information, respond "
        "with 'false'. Respond with either 'true' or 'false' and no additional text."
    )
    main_message += f"\n\nSTATEMENT:\n{statement}\nEND OF STATEMENT"

    try:
        response_message = openai_service.get_response(main_message)
    except ContextLengthException as e:
        statement_tokens = openai_service.get_token_count(statement)
        total_tokens = openai_service.get_token_count(main_message)
        base_prompt_tokens = total_tokens - statement_tokens
        raise ContextLengthException(
            "Duplicate information prompt too long to score item. OpenAI returned the following error message"
            "\n----------"
            f"\n{e}"
            "\n----------"
            "\nSee details below for breakdown of token counts"
            f"\nStatement tokens: {statement_tokens}"
            f"\nBase prompt tokens: {base_prompt_tokens}"
            f"\nTotal tokens: {total_tokens}"
        ) from e

    return response_message
