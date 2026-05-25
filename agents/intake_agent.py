"""
agents/intake_agent.py
Reads incoming WhatsApp message, classifies task, routes to correct agent.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tools import vision
from agents import oos_agent, duplicate_agent, new_product_agent


def run(image_paths: list[str], text_message: str = "") -> dict:
    """
    Main router. Receives image(s) and text from WhatsApp message.
    Classifies the task and dispatches to the right agent.

    Args:
        image_paths:   List of image file paths attached to the WhatsApp message
        text_message:  Any text in the WhatsApp message

    Returns:
        Result dict from the dispatched agent
    """
    print("\n" + "="*50)
    print("[Intake Agent] New message received")
    print(f"  Images: {len(image_paths)}")
    print(f"  Text:   '{text_message[:100]}'")
    print("="*50)

    if not image_paths:
        return {"success": False, "error": "No images received"}

    primary_image = image_paths[0]

    # Step 1: Classify task
    print("\n  Classifying task...")
    classification = vision.classify_task(primary_image, text_message)
    task       = classification.get("task", "unknown")
    confidence = classification.get("confidence", 0)
    reason     = classification.get("reason", "")

    print(f"  Task: {task} ({confidence*100:.0f}% confidence)")
    print(f"  Reason: {reason}")

    if confidence < 0.6:
        return {
            "success": False,
            "error": f"Low confidence classification ({confidence*100:.0f}%). Task unclear.",
            "task": task,
            "reason": reason,
        }

    # Step 2: Dispatch to correct agent
    if task == "oos":
        return oos_agent.run(
            image_path=primary_image,
            text_hint=text_message,
        )

    elif task == "duplicate":
        return duplicate_agent.run(
            image_path=primary_image,
            text_hint=text_message,
        )

    elif task == "new_product":
        # Pass ALL images — new_product_agent classifies them internally
        # (screenshot vs clean product photo) using GPT-4o vision
        return new_product_agent.run(
            image_paths=image_paths,
            text_hint=text_message,
        )

    else:
        return {
            "success": False,
            "error": f"Unknown task type: '{task}'. Please check the message format.",
            "raw_classification": classification,
        }
