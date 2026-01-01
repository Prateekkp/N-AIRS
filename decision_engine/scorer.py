def decide(score, reasons, cfg):
    # Threshold-based action selection
    if score >= cfg["buy_score"]:      # >= 3
        action = "BUY"
    elif score <= cfg["sell_score"]:   # <= -2
        action = "SELL"
    else:
        # Trend conflict scenario
        if "RSI_OVERBOUGHT" in reasons and "MACD_BULLISH" in reasons:
            action = "WATCH"
        else:
            action = "HOLD"

    confidence = cfg["actions"][action]["base_confidence"]
    return action, confidence, reasons
