import ast
from codecutter.astwalk import walk

# ---------------------------------- UTILS ----------------------------------- #


def string_to_expression_value(string):
    module = ast.parse(string)
    expression = module.body[0]
    return expression.value  # type: ignore


def container_replace_item(container, index, old_item, new_item):
    if isinstance(container, list):
        if not isinstance(new_item, list):
            new_items = [new_item]
        else:
            new_items = new_item

        # List indexes could change during processing, update index
        index = None
        for i, item in enumerate(container):
            if item is old_item:
                index = i
                break

        if index is None:
            raise Exception("Could not find old item from the container")

        container[:] = container[:index] + new_items + container[index + 1 :]

    else:
        setattr(container, index, new_item)


# ---------------------------- INTERNAL MODIFIERS ---------------------------- #


def remove_all_decorators(function_tree):
    function_tree.decorator_list.clear()


# -------------------------------- MODIFIERS --------------------------------- #


def replace_variables(variables):
    def wrapped(function_tree):
        changed = False
        for container, index, item in list(walk(function_tree)):
            if isinstance(item, ast.Name):
                if item.id in variables.keys():
                    container_replace_item(
                        container,
                        index,
                        item,
                        string_to_expression_value(variables[item.id]),
                    )
                    changed = True

        return changed

    return wrapped


def replace_shortcircuit_constants(function_tree):
    changed = False

    for container, index, item in list(walk(function_tree)):
        if isinstance(item, ast.BoolOp):
            has_constant = False
            comparison_item = None
            for comparison_item in item.values:
                if isinstance(comparison_item, ast.Constant):
                    has_constant = True
                    break

            if has_constant and comparison_item is not None:
                constant_value = comparison_item.value  # type: ignore

                if isinstance(item.op, ast.And):
                    if constant_value:
                        # Replace And(True, A, B, ...) with And(A, B, ...)
                        container_replace_item(
                            item.values, None, comparison_item, []
                        )
                        pass
                    else:
                        # Replace And(False, A, B, ...) with False
                        container_replace_item(
                            container,
                            index,
                            item,
                            string_to_expression_value("False"),
                        )

                    changed = True

                elif isinstance(item.op, ast.Or):
                    if constant_value:
                        # Replace Or(True, A, B, ...) with True
                        container_replace_item(
                            container,
                            index,
                            item,
                            string_to_expression_value("True"),
                        )

                    else:
                        # Replace Or(False, A, B, ...) with Or(A, B, ...)
                        container_replace_item(
                            item.values, None, comparison_item, []
                        )

                    changed = True

    return changed


def replace_constant_ifs(function_tree):
    changed = False

    for container, index, item in list(walk(function_tree)):
        if isinstance(item, ast.If):
            if isinstance(item.test, ast.Constant):
                if item.test.value:
                    replace_with = item.body
                else:
                    replace_with = item.orelse
                container_replace_item(container, index, item, replace_with)
                changed = True

    return changed
