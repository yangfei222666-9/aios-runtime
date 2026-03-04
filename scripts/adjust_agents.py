import re

# 读取文件
with open(r'C:\Users\A\.openclaw\workspace\aios\agent_system\learning_agents.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 调整频率
adjustments = {
    'GitHub_Deep_Analyzer': (168, 72),
    'Architecture_Analyst': (72, 24),
    'Code_Reviewer': (72, 24),
    'Performance_Optimizer': (72, 24),
    'Benchmark_Runner': (168, 72),
    'Documentation_Writer': (72, 24),
    'Demo_Builder': (168, 72),
    'Paper_Writer': (168, 72),
    'Marketing_Writer': (168, 72),
}

for name, (old_hours, new_hours) in adjustments.items():
    pattern = rf'("name": "{name}".*?"interval_hours": ){old_hours}'
    content = re.sub(pattern, rf'\g<1>{new_hours}', content, flags=re.DOTALL)

# 暂停 Community_Manager 和 Integration_Tester
content = re.sub(
    r'("name": "Community_Manager".*?"priority": )"low"',
    r'\1"disabled"',
    content,
    flags=re.DOTALL
)
content = re.sub(
    r'("name": "Integration_Tester".*?"priority": )"low"',
    r'\1"disabled"',
    content,
    flags=re.DOTALL
)

# 写回文件
with open(r'C:\Users\A\.openclaw\workspace\aios\agent_system\learning_agents.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 调整完成')
