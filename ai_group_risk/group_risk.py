def check_group_risk(smishing_type: str | None, urls: list[str]) -> bool:
    HIGH_FREQUENCY_TYPES = {"택배사칭", "기관사칭", "금융사기"}
    if smishing_type in HIGH_FREQUENCY_TYPES:
        return True
    if len(urls) >= 2:
        return True
    return False
