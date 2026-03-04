"""
AI Team Agent 工作细化
为每个 Agent 定义具体的工作任务、输入输出、工作流程

创建时间：2026-02-26
版本：v1.0
"""

# ============================================================
# 产品增长队（5人）
# ============================================================

PRODUCT_LEAD = {
    "agent_id": "product-lead",
    "role": "产品负责人",
    
    "daily_tasks": [
        {
            "time": "09:00-09:30",
            "task": "查看昨日数据报告",
            "input": ["用户数据", "转化率", "留存率", "反馈数据"],
            "output": "数据分析报告",
            "tools": ["data-analysis", "document-agent"],
            "example": "分析昨日新增用户 100 人，转化率 15%，发现注册流程有 30% 流失"
        },
        {
            "time": "09:30-10:30",
            "task": "制定今日产品优化方案",
            "input": ["数据分析报告", "用户反馈", "竞品分析"],
            "output": "优化方案文档",
            "tools": ["document-agent", "web-search"],
            "example": "方案：简化注册流程，从 5 步减少到 3 步，预期提升转化率 10%"
        },
        {
            "time": "10:30-11:00",
            "task": "分配任务给团队成员",
            "input": ["优化方案文档"],
            "output": "任务分配清单",
            "tools": ["message", "cron"],
            "example": "@user-researcher 请验证注册流程优化方案\n@ux-designer 请设计新的注册流程"
        },
        {
            "time": "11:00-12:00",
            "task": "产品需求评审",
            "input": ["需求文档", "技术评估"],
            "output": "需求优先级排序",
            "tools": ["document-agent"],
            "example": "P0: 注册流程优化\nP1: 用户画像功能\nP2: 社交分享"
        },
        {
            "time": "14:00-15:00",
            "task": "跟进开发进度",
            "input": ["任务状态", "开发反馈"],
            "output": "进度报告",
            "tools": ["github", "message"],
            "example": "注册流程优化：前端 80% 完成，后端 60% 完成，预计明天上线"
        },
        {
            "time": "17:00-18:00",
            "task": "复盘今日工作 + 明日计划",
            "input": ["今日完成任务", "遇到的问题"],
            "output": "日报 + 明日计划",
            "tools": ["document-agent", "message"],
            "example": "今日完成：注册流程优化方案\n明日计划：上线测试 + 数据监控"
        }
    ],
    
    "weekly_tasks": [
        {
            "day": "Monday",
            "task": "周会 + 本周目标制定",
            "output": "本周 OKR"
        },
        {
            "day": "Friday",
            "task": "周报 + 下周计划",
            "output": "周报文档"
        }
    ],
    
    "key_metrics": [
        "用户增长率",
        "转化率",
        "留存率",
        "功能使用率",
        "用户满意度"
    ],
    
    "decision_making": {
        "需求优先级": "根据用户价值 + 开发成本 + 战略重要性",
        "功能取舍": "数据驱动 + 用户反馈 + 竞品分析",
        "上线决策": "测试通过 + 数据验证 + 风险评估"
    }
}

USER_RESEARCHER = {
    "agent_id": "user-researcher",
    "role": "用户研究员",
    
    "daily_tasks": [
        {
            "time": "09:00-10:00",
            "task": "分析用户反馈",
            "input": ["用户反馈数据", "客服记录", "社交媒体评论"],
            "output": "用户痛点清单",
            "tools": ["web-search", "data-analysis"],
            "example": "发现 50% 用户反馈注册流程太复杂，30% 用户找不到核心功能"
        },
        {
            "time": "10:00-11:00",
            "task": "用户行为分析",
            "input": ["埋点数据", "用户路径", "热力图"],
            "output": "行为分析报告",
            "tools": ["data-analysis", "document-agent"],
            "example": "用户在注册第 3 步流失率最高（30%），停留时间 < 5 秒"
        },
        {
            "time": "11:00-12:00",
            "task": "用户访谈（每周 2-3 次）",
            "input": ["访谈提纲", "用户样本"],
            "output": "访谈记录 + 洞察",
            "tools": ["document-agent"],
            "example": "访谈 5 个用户，发现他们更关心隐私保护，而不是功能丰富度"
        },
        {
            "time": "14:00-15:00",
            "task": "竞品分析",
            "input": ["竞品列表", "功能对比"],
            "output": "竞品分析报告",
            "tools": ["web-search", "document-agent"],
            "example": "竞品 A 的注册流程只需 2 步，我们需要 5 步，差距明显"
        },
        {
            "time": "15:00-16:00",
            "task": "用户画像更新",
            "input": ["用户数据", "行为数据", "访谈洞察"],
            "output": "用户画像文档",
            "tools": ["data-analysis", "document-agent"],
            "example": "核心用户：25-35 岁，互联网从业者，注重效率和隐私"
        },
        {
            "time": "16:00-17:00",
            "task": "可用性测试（每周 1-2 次）",
            "input": ["原型设计", "测试任务"],
            "output": "可用性测试报告",
            "tools": ["document-agent"],
            "example": "5 个用户测试新注册流程，4 个成功完成，1 个卡在验证码"
        }
    ],
    
    "research_methods": [
        "用户访谈",
        "问卷调查",
        "可用性测试",
        "A/B 测试",
        "数据分析",
        "竞品分析"
    ],
    
    "deliverables": [
        "用户痛点清单",
        "行为分析报告",
        "用户画像",
        "竞品分析报告",
        "可用性测试报告"
    ]
}

FULLSTACK_DEV = {
    "agent_id": "fullstack-dev",
    "role": "全栈工程师",
    
    "daily_tasks": [
        {
            "time": "10:00-10:30",
            "task": "查看任务清单 + 代码审查",
            "input": ["任务列表", "PR 列表"],
            "output": "今日开发计划",
            "tools": ["github"],
            "example": "今日任务：注册流程优化（前端 + 后端），预计 6 小时"
        },
        {
            "time": "10:30-12:00",
            "task": "功能开发（前端）",
            "input": ["设计稿", "需求文档"],
            "output": "前端代码 + 组件",
            "tools": ["coding-agent", "github"],
            "example": "实现新的注册表单组件，支持手机号/邮箱双通道"
        },
        {
            "time": "14:00-16:00",
            "task": "功能开发（后端）",
            "input": ["API 设计", "数据库设计"],
            "output": "后端代码 + API",
            "tools": ["coding-agent", "github"],
            "example": "实现注册 API，支持验证码验证 + 用户信息存储"
        },
        {
            "time": "16:00-17:00",
            "task": "联调测试",
            "input": ["前端代码", "后端代码"],
            "output": "测试报告",
            "tools": ["coding-agent"],
            "example": "前后端联调通过，注册流程完整可用"
        },
        {
            "time": "17:00-18:00",
            "task": "代码审查 + 提交 PR",
            "input": ["代码", "测试结果"],
            "output": "PR + 文档",
            "tools": ["github", "document-agent"],
            "example": "提交 PR：优化注册流程，减少 2 个步骤，提升用户体验"
        }
    ],
    
    "tech_stack": {
        "frontend": ["React", "Vue", "TypeScript", "Tailwind CSS"],
        "backend": ["Node.js", "Python", "FastAPI", "PostgreSQL"],
        "tools": ["Git", "Docker", "VS Code"]
    },
    
    "code_quality": [
        "单元测试覆盖率 > 80%",
        "代码审查通过",
        "性能测试通过",
        "安全扫描通过"
    ],
    
    "collaboration": {
        "with_product": "理解需求，提供技术方案",
        "with_designer": "还原设计稿，优化交互",
        "with_qa": "配合测试，修复 bug",
        "with_devops": "配合部署，监控上线"
    }
}

UX_DESIGNER = {
    "agent_id": "ux-designer",
    "role": "UX设计师",
    
    "daily_tasks": [
        {
            "time": "09:00-10:00",
            "task": "查看设计需求 + 用户反馈",
            "input": ["需求文档", "用户反馈"],
            "output": "设计任务清单",
            "tools": ["document-agent"],
            "example": "今日任务：优化注册流程设计，简化步骤，提升转化率"
        },
        {
            "time": "10:00-12:00",
            "task": "交互设计 + 原型制作",
            "input": ["需求文档", "用户研究报告"],
            "output": "交互原型",
            "tools": ["document-agent"],
            "example": "设计新的注册流程：手机号 → 验证码 → 完成（3 步）"
        },
        {
            "time": "14:00-15:00",
            "task": "视觉设计",
            "input": ["交互原型", "设计规范"],
            "output": "视觉设计稿",
            "tools": ["document-agent"],
            "example": "设计注册页面视觉稿，符合品牌调性，简洁易用"
        },
        {
            "time": "15:00-16:00",
            "task": "设计评审",
            "input": ["设计稿"],
            "output": "评审意见 + 修改方案",
            "tools": ["message"],
            "example": "评审通过，建议：验证码输入框增大，提升可点击性"
        },
        {
            "time": "16:00-17:00",
            "task": "设计交付 + 跟进开发",
            "input": ["最终设计稿"],
            "output": "设计标注 + 切图",
            "tools": ["document-agent"],
            "example": "交付设计稿给开发，提供标注和切图，跟进还原度"
        }
    ],
    
    "design_principles": [
        "简洁易用",
        "一致性",
        "可访问性",
        "美观性",
        "响应式"
    ],
    
    "deliverables": [
        "交互原型",
        "视觉设计稿",
        "设计规范",
        "组件库",
        "设计标注"
    ]
}

TECHNICAL_WRITER = {
    "agent_id": "technical-writer",
    "role": "技术文档专家",
    
    "daily_tasks": [
        {
            "time": "09:00-10:00",
            "task": "查看文档需求 + 更新清单",
            "input": ["功能更新", "API 变更", "用户反馈"],
            "output": "文档更新清单",
            "tools": ["github", "document-agent"],
            "example": "今日任务：更新注册 API 文档，新增用户手册"
        },
        {
            "time": "10:00-12:00",
            "task": "API 文档编写",
            "input": ["API 代码", "接口设计"],
            "output": "API 文档",
            "tools": ["github", "document-agent"],
            "example": "编写注册 API 文档：请求参数、响应格式、错误码说明"
        },
        {
            "time": "14:00-15:00",
            "task": "用户手册编写",
            "input": ["功能说明", "操作流程"],
            "output": "用户手册",
            "tools": ["document-agent"],
            "example": "编写注册流程用户手册：如何注册、常见问题、故障排查"
        },
        {
            "time": "15:00-16:00",
            "task": "知识库维护",
            "input": ["常见问题", "用户反馈"],
            "output": "知识库文章",
            "tools": ["document-agent", "web-search"],
            "example": "更新知识库：注册失败的 5 种常见原因和解决方法"
        },
        {
            "time": "16:00-17:00",
            "task": "技术博客撰写（每周 1-2 篇）",
            "input": ["技术方案", "最佳实践"],
            "output": "技术博客",
            "tools": ["document-agent", "web-search"],
            "example": "撰写博客：如何设计高转化率的注册流程"
        }
    ],
    
    "documentation_types": [
        "API 文档",
        "用户手册",
        "开发指南",
        "知识库",
        "技术博客",
        "发布说明"
    ],
    
    "writing_principles": [
        "清晰易懂",
        "结构化",
        "示例丰富",
        "及时更新",
        "用户视角"
    ]
}

# ============================================================
# 技术平台队（5人）
# ============================================================

ENGINEERING_MANAGER = {
    "agent_id": "engineering-manager",
    "role": "工程经理",
    
    "daily_tasks": [
        {
            "time": "09:00-09:30",
            "task": "查看系统监控 + 告警",
            "input": ["监控数据", "告警信息"],
            "output": "系统健康报告",
            "tools": ["monitoring"],
            "example": "系统正常，CPU 使用率 60%，内存使用率 70%，无告警"
        },
        {
            "time": "09:30-10:30",
            "task": "代码审查",
            "input": ["PR 列表"],
            "output": "审查意见",
            "tools": ["github", "coding-agent"],
            "example": "审查 3 个 PR，2 个通过，1 个需要优化性能"
        },
        {
            "time": "10:30-11:30",
            "task": "技术架构设计",
            "input": ["需求文档", "技术方案"],
            "output": "架构设计文档",
            "tools": ["document-agent"],
            "example": "设计用户系统架构：微服务 + Redis 缓存 + PostgreSQL"
        },
        {
            "time": "14:00-15:00",
            "task": "技术债务管理",
            "input": ["代码质量报告", "性能报告"],
            "output": "技术债务清单",
            "tools": ["github", "monitoring"],
            "example": "识别 5 个技术债务：老旧依赖、重复代码、性能瓶颈"
        },
        {
            "time": "15:00-16:00",
            "task": "团队协调 + 问题解决",
            "input": ["团队反馈", "阻塞问题"],
            "output": "解决方案",
            "tools": ["message"],
            "example": "协调前后端联调问题，安排 backend-specialist 支持"
        },
        {
            "time": "17:00-18:00",
            "task": "技术分享 + 复盘",
            "input": ["今日工作", "技术洞察"],
            "output": "技术分享文档",
            "tools": ["document-agent"],
            "example": "分享：如何设计高可用的用户系统"
        }
    ],
    
    "responsibilities": [
        "技术架构设计",
        "代码审查",
        "技术债务管理",
        "团队协调",
        "性能优化",
        "安全保障"
    ],
    
    "key_metrics": [
        "系统可用性 > 99.9%",
        "代码质量评分 > 80",
        "技术债务 < 10%",
        "部署频率 > 10 次/周"
    ]
}

# ... 其他 Agent 的工作细化（后端专家、DevOps、QA、安全工程师）

# ============================================================
# 营销增长队（5人）
# ============================================================

GROWTH_LEAD = {
    "agent_id": "growth-lead",
    "role": "增长负责人",
    
    "daily_tasks": [
        {
            "time": "09:00-09:30",
            "task": "查看增长数据",
            "input": ["用户增长数据", "转化漏斗", "渠道数据"],
            "output": "增长数据报告",
            "tools": ["data-analysis"],
            "example": "昨日新增用户 100 人，转化率 15%，主要来源：搜索引擎 60%"
        },
        {
            "time": "09:30-10:30",
            "task": "制定增长实验",
            "input": ["数据报告", "增长假设"],
            "output": "实验方案",
            "tools": ["document-agent"],
            "example": "实验：优化落地页标题，预期提升转化率 20%"
        },
        {
            "time": "10:30-11:30",
            "task": "分配增长任务",
            "input": ["实验方案"],
            "output": "任务分配",
            "tools": ["message"],
            "example": "@content-strategist 请优化落地页文案\n@acquisition-specialist 请投放测试流量"
        },
        {
            "time": "14:00-15:00",
            "task": "分析实验结果",
            "input": ["实验数据"],
            "output": "实验分析报告",
            "tools": ["data-analysis", "document-agent"],
            "example": "实验结果：新标题转化率 18%，提升 3%，建议推广"
        },
        {
            "time": "15:00-16:00",
            "task": "渠道优化",
            "input": ["渠道数据", "ROI 分析"],
            "output": "渠道优化方案",
            "tools": ["data-analysis"],
            "example": "优化方案：增加搜索引擎投放，减少社交媒体投放"
        },
        {
            "time": "17:00-18:00",
            "task": "增长复盘 + 明日计划",
            "input": ["今日数据", "实验结果"],
            "output": "增长日报",
            "tools": ["document-agent"],
            "example": "今日新增 100 人，完成 1 个实验，明日计划：推广新标题"
        }
    ],
    
    "growth_methods": [
        "A/B 测试",
        "增长黑客",
        "病毒营销",
        "内容营销",
        "SEO/SEM",
        "社交媒体"
    ],
    
    "key_metrics": [
        "用户增长率",
        "获客成本（CAC）",
        "用户生命周期价值（LTV）",
        "转化率",
        "留存率"
    ]
}

# ============================================================
# CEO（总办）
# ============================================================

CEO = {
    "agent_id": "ceo",
    "role": "CEO（创始人的每日工作）",
    
    "daily_schedule": [
        {
            "time": "08:00-09:00",
            "task": "审阅数据报告",
            "input": ["情报简报", "用户反馈", "行为洞察"],
            "output": "战略洞察",
            "tools": ["data-analysis", "document-agent"],
            "example": "发现用户增长放缓，需要加大营销投入"
        },
        {
            "time": "09:00-12:00",
            "task": "Squad 例会 + 关键决策",
            "input": ["团队汇报", "问题清单"],
            "output": "决策清单",
            "tools": ["message"],
            "example": "决策：批准注册流程优化方案，预算 10 万元"
        },
        {
            "time": "13:00-14:00",
            "task": "战略规划",
            "input": ["市场分析", "竞品分析", "团队反馈"],
            "output": "战略规划文档",
            "tools": ["web-search", "document-agent"],
            "example": "制定 Q2 战略：聚焦用户增长，目标 10 万用户"
        },
        {
            "time": "14:00-16:00",
            "task": "资源协调 + 问题解决",
            "input": ["团队需求", "资源状况"],
            "output": "资源分配方案",
            "tools": ["message"],
            "example": "协调：增加 2 名工程师支持产品开发"
        },
        {
            "time": "16:00-17:00",
            "task": "外部沟通（投资人、合作伙伴）",
            "input": ["公司数据", "进展报告"],
            "output": "沟通记录",
            "tools": ["document-agent", "message"],
            "example": "向投资人汇报：用户增长 50%，融资进展顺利"
        },
        {
            "time": "17:00-19:00",
            "task": "复盘今日工作 + 生成明日计划 + 发布日报",
            "input": ["今日完成任务", "遇到的问题"],
            "output": "日报 + 明日计划",
            "tools": ["document-agent", "message"],
            "example": "今日完成：批准 3 个方案，解决 2 个问题\n明日计划：产品评审 + 融资路演"
        }
    ],
    
    "decision_areas": [
        "战略方向",
        "资源分配",
        "团队建设",
        "融资计划",
        "重大产品决策"
    ],
    
    "key_metrics": [
        "用户增长",
        "营收增长",
        "融资进展",
        "团队满意度",
        "产品 PMF"
    ]
}

# ============================================================
# 导出配置
# ============================================================

ALL_AGENTS_DETAILED = {
    "product_team": {
        "product-lead": PRODUCT_LEAD,
        "user-researcher": USER_RESEARCHER,
        "fullstack-dev": FULLSTACK_DEV,
        "ux-designer": UX_DESIGNER,
        "technical-writer": TECHNICAL_WRITER
    },
    "engineering_team": {
        "engineering-manager": ENGINEERING_MANAGER
        # ... 其他工程师
    },
    "growth_team": {
        "growth-lead": GROWTH_LEAD
        # ... 其他增长成员
    },
    "executive": {
        "ceo": CEO
    }
}
