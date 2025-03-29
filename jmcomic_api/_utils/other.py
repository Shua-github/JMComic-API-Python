def get_object_members(
    obj,
    max_depth=20,
    current_depth=0,
    seen=None,
    seen_values=None,
):
    # 初始化集合
    if seen is None:
        seen = set()
    if seen_values is None:
        seen_values = set()

    # 基本类型直接返回
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # 防止递归过深
    if current_depth >= max_depth:
        return str(obj)

    # 防止重复处理相同对象
    obj_id = id(obj)
    if obj_id in seen:
        return None
    seen.add(obj_id)

    # 处理字典
    if isinstance(obj, dict):
        members = {}
        for k, v in obj.items():
            processed_value = get_object_members(
                v,
                max_depth,
                current_depth + 1,
                seen,
                seen_values,
            )
            try:
                value_hash = repr(processed_value)  # 使用 repr 确保可哈希
                if value_hash not in seen_values and processed_value not in (
                    None,
                    {},
                    [],
                    "",
                ):
                    members[k] = processed_value
                    seen_values.add(value_hash)
            except TypeError:
                # 遇到不可哈希类型，使用字符串表示形式
                members[k] = str(processed_value)
        return members

    # 处理列表、元组、集合等可迭代对象
    if isinstance(obj, (list, tuple, set)):
        result = []
        for item in obj:
            processed_item = get_object_members(
                item,
                max_depth,
                current_depth + 1,
                seen,
                seen_values,
            )
            try:
                item_hash = repr(processed_item)
                if item_hash not in seen_values and processed_item not in (
                    None,
                    {},
                    [],
                    "",
                ):
                    result.append(processed_item)
                    seen_values.add(item_hash)
            except TypeError:
                result.append(str(processed_item))
        return result

    # 处理其他对象
    members = {}
    for name in dir(obj):
        if name.startswith("__") and name.endswith("__"):
            continue

        try:
            attr = getattr(obj, name)
            processed_attr = get_object_members(
                attr,
                max_depth,
                current_depth + 1,
                seen,
                seen_values,
            )

            try:
                attr_hash = repr(processed_attr)
                if attr_hash not in seen_values and processed_attr not in (
                    None,
                    {},
                    [],
                    "",
                ):
                    members[name] = processed_attr
                    seen_values.add(attr_hash)
            except TypeError:
                members[name] = str(processed_attr)
        except Exception as e:
            members[name] = f"<error: {e}>"

    return members
