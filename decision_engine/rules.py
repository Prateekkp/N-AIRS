def apply_rules(row, cfg):
    score = 0.0
    reasons = []

    # =========================
    # RSI: Mean Reversion Logic
    # =========================
    if row["rsi_14"] <= cfg["rsi_buy"]:
        score += 2.0
        reasons.append("RSI_OVERSOLD")

    elif row["rsi_14"] >= cfg["rsi_sell"]:
        score -= 2.0
        reasons.append("RSI_OVERBOUGHT")

    # =========================
    # MACD: Momentum Confirmation
    # =========================
    if row["macd"] > row["macd_signal"]:
        score += 1.5
        reasons.append("MACD_BULLISH")
    else:
        # Weak trend ≠ bearish
        score -= 0.5
        reasons.append("MACD_WEAK")

    # =========================
    # Trend Regime Filter
    # =========================
    if row["sma_20"] > row["ema_50"]:
        score += 0.5
        reasons.append("UPTREND_REGIME")
    else:
        score -= 0.5
        reasons.append("DOWNTREND_REGIME")

    return round(score, 2), reasons
