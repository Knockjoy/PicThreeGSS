# copyright (c) 2025 Yuuki Furuta

import copy

class InnerInstance:
    def __init__(self, value):
        self.value = value

class OuterInstance:
    def __init__(self, name, inner_obj):
        self.name = name
        self.inner_obj = inner_obj

# 元のインスタンスを作成
inner1 = InnerInstance(10)
outer1 = OuterInstance("Original Outer", inner1)

print(f"Original outer1 ID: {id(outer1)}")
print(f"Original outer1.inner_obj ID: {id(outer1.inner_obj)}")
print(f"Original outer1.inner_obj.value: {outer1.inner_obj.value}")

print("-" * 30)

# deepcopyを実行
outer_deep_copy = copy.deepcopy(outer1)

print(f"Deep copy outer_deep_copy ID: {id(outer_deep_copy)}")
print(f"Deep copy outer_deep_copy.inner_obj ID: {id(outer_deep_copy.inner_obj)}")
print(f"Deep copy outer_deep_copy.inner_obj.value: {outer_deep_copy.inner_obj.value}")

print("-" * 30)

# コピーされたオブジェクトの値を変更
outer_deep_copy.name = "Copied Outer"
outer_deep_copy.inner_obj.value = 20

print(f"After modifying deep copy:")
print(f"Original outer1.name: {outer1.name}")
print(f"Original outer1.inner_obj.value: {outer1.inner_obj.value}")
print(f"Deep copy outer_deep_copy.name: {outer_deep_copy.name}")
print(f"Deep copy outer_deep_copy.inner_obj.value: {outer_deep_copy.inner_obj.value}")