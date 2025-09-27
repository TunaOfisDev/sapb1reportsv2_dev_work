# backend/productconfigv2/services/rule_engine.py

from ..models import Rule


def is_valid_combination(product_family_id, selections):
    """
    Kullanıcının yaptığı seçimlerin geçerli olup olmadığını kontrol eder.
    Seçimler, {"Engine": "500cc", "Color": "Red"} gibi gelir.
    Deny kurallardan biri eşleşirse geçersizdir.
    """
    rules = Rule.objects.filter(product_family_id=product_family_id, is_active=True)

    for rule in rules:
        if rule.rule_type == "deny" and _match_conditions(rule.conditions, selections):
            return False
    return True


def apply_rules(product_family_id, selections):
    """
    Seçimlere göre 'disable' aksiyonlarını döner. (örn: bazı seçenekleri devre dışı bırak)
    selections: {"Engine": "500cc", "Color": "Red"}
    return: ["Color=Blue", "Fuel=Diesel"]
    """
    rules = Rule.objects.filter(product_family_id=product_family_id, is_active=True)
    disabled_options = set()

    for rule in rules:
        if _match_conditions(rule.conditions, selections):
            if rule.rule_type == "deny":
                disables = rule.actions.get("disable", [])
                disabled_options.update(disables)

    return list(disabled_options)


def _match_conditions(rule_conditions, selections):
    """
    Koşullar birebir eşleşmeli.
    Örnek:
    rule_conditions = {"Engine": "500cc", "Color": "Red"}
    selections = {"Engine": "500cc", "Color": "Red", "Fuel": "Enj"}
    """
    for spec_name, expected_option in rule_conditions.items():
        selected_option = selections.get(spec_name)
        if selected_option != expected_option:
            return False
    return True


def create_rule_from_template(product_family, rule_type, name, conditions, actions, user=None):
    """
    Admin üzerinden kolay kural tanımlamak için.
    conditions: {"Engine": "500cc"}
    actions: {"disable": ["Fuel=Diesel"]}
    """
    return Rule.objects.create(
        product_family=product_family,
        rule_type=rule_type,
        name=name,
        conditions=conditions,
        actions=actions,
        created_by=user,
        updated_by=user
    )
