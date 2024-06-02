{
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.4",
    "body": [
        {
            "type": "TextBlock",
            "text": "Approval Request",
            "weight": "Bolder",
            "size": "Large",
        },
        {
            "type": "TextBlock",
            "text": "Please review and approve the following request:",
            "wrap": true,
        },
        {
            "type": "TextBlock",
            "text": "Request Details:",
            "weight": "Bolder",
            "spacing": "Medium",
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Requester:", "value": "John Doe"},
                {"title": "Request Date:", "value": "2022-01-01"},
                {"title": "Request Type:", "value": "Expense Report"},
                {"title": "Amount:", "value": "$100.00"},
            ],
        },
    ],
    "actions": [
        {"type": "Action.Submit", "title": "Approve", "data": {"action": "approve"}},
        {"type": "Action.Submit", "title": "Reject", "data": {"action": "reject"}},
    ],
}
