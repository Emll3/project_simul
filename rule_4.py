def applyRule4(time, slotLength, stdevElectiveDuration):
    alpha = 0.5
    return time - alpha * (stdevElectiveDuration / 60)
