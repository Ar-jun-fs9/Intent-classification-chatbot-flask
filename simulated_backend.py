def simulated_backend_action(intent, order_id):
    """
    Simulate backend actions for a chatbot.
    """
    if intent == "cancel_order":
        return f"Order {order_id} has been cancelled successfully."
    elif intent == "track_order":
        return (
            f"Order {order_id} is currently being processed and will be delivered soon."
        )
    elif intent == "change_order":
        return f"Order {order_id} has been updated as per your request."
    elif intent == "payment_issue":
        return f"Payment issue for order {order_id} has been reported. Our team will contact you."
    else:
        return f"Action for {intent} is completed on order {order_id}."
