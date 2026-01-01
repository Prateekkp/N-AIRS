def apply_rules(row, cfg):
    score = 0
    reasons = []

    # RSI logic
    if row["rsi_14"] < cfg["rsi_buy"]:
        score += 2          # Oversold = strong bullish
        reasons.append("RSI_OVERSOLD")
    elif row["rsi_14"] > cfg["rsi_sell"]:
        score -= 2
        reasons.append("RSI_OVERBOUGHT")

    # MACD trend
    if row["macd"] > row["macd_signal"]:
        score += 1.5        # Slight boost to help reach 3
        reasons.append("MACD_BULLISH")
    else:
        score -= 1.5
        reasons.append("MACD_BEARISH")

    return score, reasons
