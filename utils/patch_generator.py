

import os

USE_LLM = False  # True karo agar Anthropic API key set ho aur real AI-generated patch chahiye


TEMPLATES = {
    "NullReferenceError": {
        "explanation": "card_token null/undefined tha jab validate_card() ne isay access kiya.",
        "patch": '''
def get_token(payment_details):
    # FIX: null-check add kiya gaya taake undefined card_token pe crash na ho
    if not payment_details or "card_token" not in payment_details:
        raise ValueError("card_token missing - request rejected before processing")
    return payment_details["card_token"]
''',
    },
    "DatabaseError": {
        "explanation": "DB connection ya query timeout ho rahi thi, retry logic missing tha.",
        "patch": '''
def execute_query(query, retries=3):
    # FIX: retry with exponential backoff add kiya gaya
    import time
    for attempt in range(retries):
        try:
            return db.execute(query)
        except DatabaseTimeoutError:
            time.sleep(2 ** attempt)
    raise DatabaseTimeoutError("Query failed after retries")
''',
    },
    "UpstreamServerError": {
        "explanation": "Downstream payment-service se 500 aa raha tha, router ne graceful fallback nahi diya.",
        "patch": '''
def forward_request(request):
    # FIX: circuit breaker + graceful error response add kiya gaya
    try:
        return payment_service.forward(request)
    except UpstreamServiceError:
        return JsonResponse({"error": "Payment service unavailable, please retry"}, status=503)
''',
    },
}


def generate_patch(root_cause):
    """
    root_cause: dict jaisa {agent, file, line, error_type, raw_message}
    Returns: dict with explanation + patch code
    """
    error_type = root_cause.get("error_type")

    if USE_LLM:
        return _generate_patch_via_llm(root_cause)

    template = TEMPLATES.get(error_type)
    if not template:
        return {
            "explanation": "Root cause identify nahi ho saka, manual review chahiye.",
            "patch": None,
        }

    return {
        "explanation": template["explanation"],
        "patch": template["patch"].strip(),
        "target_file": root_cause.get("file"),
        "target_line": root_cause.get("line"),
    }


def _generate_patch_via_llm(root_cause):
    """
    Real Anthropic API call - jab aap apni key set karein (env var ANTHROPIC_API_KEY)
    Uncomment aur 'anthropic' package install karein: pip install anthropic --break-system-packages
    """
    # import anthropic
    # client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    # message = client.messages.create(
    #     model="claude-sonnet-4-6",
    #     max_tokens=500,
    #     messages=[{
    #         "role": "user",
    #         "content": f"Is bug ka secure fix likho: {root_cause}"
    #     }]
    # )
    # return {"explanation": "AI-generated", "patch": message.content[0].text}
    raise NotImplementedError("LLM mode enable karne ke liye upar wala code uncomment karein aur API key set karein.")