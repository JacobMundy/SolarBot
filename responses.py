def handle_response(message) -> str:
    formatted_message = message.lower()

    if formatted_message == "test":
        return "Test"
