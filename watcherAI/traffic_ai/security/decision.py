from watcherAI.traffic_ai.security.rules import DatasetRuleEngine
from watcherAI.traffic_ai.security.llm_outsider import LLMOutsider

rules = DatasetRuleEngine()
llm = LLMOutsider()

def decide(text, ml_label, ml_conf):
    rule_label = rules.check(text)
    if rule_label > 0:
        return rule_label

    llm_label = llm.analyze(text)
    if llm_label > ml_label:
        return llm_label

    if ml_conf > 0.85:
        return ml_label

    return 0