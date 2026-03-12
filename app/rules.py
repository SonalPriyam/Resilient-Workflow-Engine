import operator
from jsonpath_ng import parse

class RuleEvaluator:
    
    OPERATORS = {
        ">=": operator.ge,
        "<=": operator.le,
        ">": operator.gt,
        "<": operator.lt,
        "==": operator.eq,
        "!=": operator.ne,
        "contains": lambda a, b: b in a
    }

    @staticmethod
    def evaluate(data: dict, condition_str: str) -> bool:
        try:
            parts = condition_str.split(" ")
            path_query = parts[0]
            op_str = parts[1]
            target_value = " ".join(parts[2:])
            
            jsonpath_expr = parse(path_query)
            matches = jsonpath_expr.find(data)
            
            if not matches:
                return False
            
            actual_value = matches[0].value
            
            typed_target = type(actual_value)(target_value.strip("'\""))
            
            if op_str in RuleEvaluator.OPERATORS:
                return RuleEvaluator.OPERATORS[op_str](actual_value, typed_target)
            
            return False
        except Exception as e:
            print(f"Error evaluating rule '{condition_str}': {e}")
            return False