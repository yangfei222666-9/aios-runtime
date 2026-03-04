#!/usr/bin/env python3
"""GitHub 学习脚本 - 每天学习 AIOS/Agent/Skill 相关知识"""
import json
import time
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent.parent
STATE_FILE = WORKSPACE / "memory" / "selflearn-state.json"
MEMORY_DIR = WORKSPACE / "memory"

def load_state():
    """加载状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_state(state):
    """保存状态"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def should_run(state):
    """检查是否需要运行（每天一次）"""
    last_run = state.get('last_github_learning')
    if not last_run:
        return True
    
    # 检查是否超过 24 小时
    last_time = datetime.fromisoformat(last_run)
    now = datetime.now()
    return (now - last_time).total_seconds() > 86400

def search_github(keywords):
    """搜索 GitHub（使用 web_search 工具）"""
    # TODO: 调用 web_search 工具
    # 这里先返回模拟数据
    return [
        {
            'name': 'AutoGPT',
            'url': 'https://github.com/Significant-Gravitas/AutoGPT',
            'stars': 165000,
            'description': 'An experimental open-source attempt to make GPT-4 fully autonomous.',
            'topics': ['agent', 'autonomous', 'gpt-4']
        },
        {
            'name': 'LangChain',
            'url': 'https://github.com/langchain-ai/langchain',
            'stars': 89000,
            'description': 'Building applications with LLMs through composability',
            'topics': ['agent', 'llm', 'chain']
        },
        {
            'name': 'MetaGPT',
            'url': 'https://github.com/geekan/MetaGPT',
            'stars': 42000,
            'description': 'Multi-Agent Framework',
            'topics': ['multi-agent', 'framework', 'collaboration']
        }
    ]

def analyze_project(project):
    """分析项目（提取核心思路）"""
    insights = []
    
    # 分析 topics
    topics = project.get('topics', [])
    if 'multi-agent' in topics:
        insights.append('多 Agent 协作')
    if 'self-improving' in topics or 'evolution' in topics:
        insights.append('自我进化')
    if 'event-driven' in topics:
        insights.append('事件驱动架构')
    
    return {
        'name': project['name'],
        'url': project['url'],
        'stars': project['stars'],
        'insights': insights
    }

def compare_with_ours(projects):
    """对比我们的 AIOS"""
    advantages = []
    gaps = []
    ideas = []
    
    # 我们的优势
    advantages.append('零依赖，可打包可复制')
    advantages.append('完整的自我进化闭环（Self-Improving Loop）')
    advantages.append('事件驱动架构（EventBus + Scheduler + Reactor）')
    
    # 我们的缺口
    for proj in projects:
        if proj['stars'] > 10000:
            gaps.append(f"缺少社区生态（{proj['name']} 有 {proj['stars']} stars）")
    
    # 可以借鉴的思路
    ideas.append('建立 Agent 市场（类似 Docker Hub）')
    ideas.append('简化架构（从 317 个文件降到 100 个以内）')
    ideas.append('增加"杀手级场景"demo')
    
    return {
        'advantages': advantages,
        'gaps': gaps,
        'ideas': ideas
    }

def log_to_memory(insights, comparison):
    """记录到 memory/YYYY-MM-DD.md"""
    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = MEMORY_DIR / f"{today}.md"
    
    content = f"\n## GitHub 学习（{datetime.now().strftime('%H:%M')}）\n\n"
    content += "### 发现的项目\n"
    for insight in insights:
        content += f"- **{insight['name']}** ({insight['stars']} ⭐)\n"
        content += f"  - {insight['url']}\n"
        if insight['insights']:
            content += f"  - 核心思路：{', '.join(insight['insights'])}\n"
    
    content += "\n### 对比我们的 AIOS\n"
    content += "**优势：**\n"
    for adv in comparison['advantages']:
        content += f"- {adv}\n"
    
    content += "\n**缺口：**\n"
    for gap in comparison['gaps']:
        content += f"- {gap}\n"
    
    content += "\n**可以借鉴：**\n"
    for idea in comparison['ideas']:
        content += f"- {idea}\n"
    
    # 追加到文件
    if memory_file.exists():
        with open(memory_file, 'a', encoding='utf-8') as f:
            f.write(content)
    else:
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write(f"# {today}\n\n")
            f.write(content)

def main():
    """主函数"""
    state = load_state()
    
    # 检查是否需要运行
    if not should_run(state):
        print("GITHUB_LEARNING_OK")
        return
    
    # 搜索 GitHub
    keywords = ['AIOS', 'Agent System', 'Self-Improving', 'Multi-Agent', 'Skill System']
    projects = []
    
    for keyword in keywords[:2]:  # 每天搜索 2 个关键词
        results = search_github(keyword)
        projects.extend(results)
    
    # 去重（按 URL）
    seen = set()
    unique_projects = []
    for proj in projects:
        if proj['url'] not in seen:
            seen.add(proj['url'])
            unique_projects.append(proj)
    
    # 分析项目
    insights = [analyze_project(proj) for proj in unique_projects[:5]]  # 只分析前 5 个
    
    # 对比我们的 AIOS
    comparison = compare_with_ours(insights)
    
    # 记录到 memory
    log_to_memory(insights, comparison)
    
    # 更新状态
    state['last_github_learning'] = datetime.now().isoformat()
    save_state(state)
    
    # 输出
    insight_count = sum(len(i['insights']) for i in insights)
    if insight_count > 0:
        print(f"GITHUB_LEARNING_INSIGHTS:{insight_count}")
    else:
        print("GITHUB_LEARNING_OK")

if __name__ == '__main__':
    main()
