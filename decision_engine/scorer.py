def decide(score, reasons, cfg):
    """
    Production-aligned decision logic
    Config-respecting (no new keys introduced)
    """

    buy_score = cfg["buy_score"]
    sell_score = cfg["sell_score"]

    if score >= buy_score:
        action = "BUY"

    elif score <= sell_score:
        action = "SELL"

    # WATCH = close to BUY but not confirmed
    elif (buy_score - 1.0) <= score < buy_score:
        action = "WATCH"

    else:
        action = "HOLD"

    # =========================
    # Confidence Scaling
    # =========================
    base_conf = cfg["actions"][action]["base_confidence"]

    confidence = min(
        0.95,
        round(base_conf + abs(score) * 0.05, 2)
    )

    return action, confidence, reasons
