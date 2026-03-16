"""
AI Risk Scorer — computes automation potential for job tasks and skills.

Uses heuristic rules based on task characteristics to estimate how
automatable each skill/task is (0.0 = impossible to automate, 1.0 = fully automatable).
"""

HIGHLY_AUTOMATABLE_KEYWORDS = [
    "data entry", "filing", "sorting", "copying", "recording",
    "calculating", "tabulating", "bookkeeping", "scheduling",
    "transcribing", "proofreading", "checking", "verifying",
    "monitoring instruments", "inspecting", "scanning",
    "classifying", "coding data", "compiling", "routine",
    "repetitive", "standardized", "processing claims",
    "processing orders", "processing transactions",
    "word processing", "spreadsheet", "database entry",
]

MODERATELY_AUTOMATABLE_KEYWORDS = [
    "analyzing data", "interpreting data", "statistical",
    "programming", "software", "testing", "quality control",
    "drafting", "technical writing", "translating",
    "customer service", "answering questions", "information",
    "research", "reviewing", "evaluating", "assessing",
    "diagnosing", "planning", "organizing", "coordinating",
    "operating equipment", "operating machinery",
    "accounting", "auditing", "financial analysis",
    "market research", "forecasting",
]

LOW_AUTOMATION_KEYWORDS = [
    "counseling", "therapy", "mentoring", "coaching",
    "negotiating", "persuading", "mediating", "arbitrating",
    "leading", "managing people", "supervising", "motivating",
    "creative", "designing", "composing", "choreographing",
    "performing", "acting", "singing", "artistic",
    "strategic planning", "innovation", "vision",
    "empathy", "emotional", "interpersonal",
    "physical therapy", "surgery", "emergency",
    "teaching", "training", "educating", "instructing",
    "public speaking", "presenting",
]

VERY_LOW_AUTOMATION_KEYWORDS = [
    "emergency response", "crisis", "unpredictable",
    "complex surgery", "fine motor", "dexterity",
    "athletic", "dance", "acrobatic",
    "spiritual", "pastoral", "religious",
    "judicial", "legal judgment", "sentencing",
    "diplomatic", "political", "policy making",
    "psychotherapy", "psychiatric",
]


def score_task_automation(task_description: str) -> float:
    text = task_description.lower()

    for kw in VERY_LOW_AUTOMATION_KEYWORDS:
        if kw in text:
            return 0.15

    for kw in LOW_AUTOMATION_KEYWORDS:
        if kw in text:
            return 0.30

    for kw in HIGHLY_AUTOMATABLE_KEYWORDS:
        if kw in text:
            return 0.90

    for kw in MODERATELY_AUTOMATABLE_KEYWORDS:
        if kw in text:
            return 0.60

    return 0.50


def score_skill_automation(skill_name: str, skill_category: str) -> float:
    text = skill_name.lower()
    cat = skill_category.lower()

    if cat == "ability":
        physical_abilities = ["arm-hand steadiness", "manual dexterity", "finger dexterity",
                              "trunk strength", "stamina", "flexibility", "gross body"]
        cognitive_abilities = ["oral comprehension", "written comprehension",
                               "oral expression", "written expression",
                               "originality", "fluency of ideas", "problem sensitivity"]
        for pa in physical_abilities:
            if pa in text:
                return 0.25
        for ca in cognitive_abilities:
            if ca in text:
                return 0.35

    if cat == "knowledge":
        automatable_knowledge = ["clerical", "administrative", "mathematics",
                                  "computers", "telecommunications"]
        human_knowledge = ["psychology", "sociology", "therapy", "counseling",
                           "philosophy", "fine arts", "law", "medicine"]
        for ak in automatable_knowledge:
            if ak in text:
                return 0.70
        for hk in human_knowledge:
            if hk in text:
                return 0.30

    if cat == "skill":
        tech_skills = ["programming", "technology design", "troubleshooting",
                       "equipment maintenance", "repairing", "quality control"]
        social_skills = ["social perceptiveness", "persuasion", "negotiation",
                         "instructing", "service orientation", "coordination"]
        for ts in tech_skills:
            if ts in text:
                return 0.55
        for ss in social_skills:
            if ss in text:
                return 0.20

    return score_task_automation(text)


def compute_career_automation_index(skills: list[dict]) -> float:
    if not skills:
        return 50.0

    weighted_sum = 0.0
    weight_total = 0.0

    for skill in skills:
        importance = skill.get("importance_score", 50.0)
        automation = skill.get("automation_potential", 0.5)
        weighted_sum += importance * automation
        weight_total += importance

    if weight_total == 0:
        return 50.0

    return (weighted_sum / weight_total) * 100
