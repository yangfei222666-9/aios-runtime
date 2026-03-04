# AIOS 防误报补丁设计（最小改动）

## 🎯 目标
在不改变架构的前提下，添加保护层，防止误报和数据异常。

---

## 🔧 补丁 1：修复 0.0秒耗时问题

### 问题
- 任务提交耗时太短（< 0.001秒）
- 统计显示 0.0秒，误导用户

### 解决方案
在 `adaptive_learning.py` 中添加最小粒度保护：

```python
# 在 record_success() 方法中
def record_success(self, ...):
    # 设置最小统计粒度（1ms）
    duration = max(duration, 0.001)
    
    # 原有逻辑...
```

### 验证
- 所有耗时 ≥ 0.001秒
- 显示格式："<0.01秒"（对用户友好）

---

## 🔧 补丁 2：修复"间隔过短"误报

### 问题
- 测试/快速操作被误判为异常
- 正常使用场景触发警告

### 解决方案
在 `predictive_engine.py` 中添加去抖和白名单：

```python
class PredictiveEngine:
    # 添加配置
    RAPID_EXECUTION_THRESHOLD = 5.0  # 5秒阈值
    RAPID_EXECUTION_WHITELIST = [
        "simple_view",  # 简单查询
        "monitor",      # 监控任务
    ]
    
    def detect_anomalies(self) -> List[Dict]:
        anomalies = []
        
        # ... 其他检测 ...
        
        # 检测时间间隔异常（添加保护）
        if len(self.task_history) >= 2:
            last_task = self.task_history[-1]
            prev_task = self.task_history[-2]
            
            last_interval = last_task["timestamp"] - prev_task["timestamp"]
            
            # 白名单检查
            is_whitelisted = (
                last_task["task_type"] in self.RAPID_EXECUTION_WHITELIST or
                prev_task["task_type"] in self.RAPID_EXECUTION_WHITELIST
            )
            
            # 只有非白名单 + 间隔过短才报警
            if not is_whitelisted and last_interval < self.RAPID_EXECUTION_THRESHOLD:
                anomalies.append({
                    "type": "rapid_execution",
                    "interval": last_interval,
                    "message": f"任务执行间隔过短（{last_interval:.1f}秒）",
                    "suggestion": "检查是否有重复触发",
                })
        
        return anomalies
```

### 验证
- 白名单任务不触发警告
- 非白名单 + 间隔 < 5秒才警告
- 正常快速操作不误报

---

## 🔧 补丁 3：JSONL 去重压缩

### 问题
- 每次更新都追加，导致文件重复
- 文件大小无限增长

### 解决方案
在 `adaptive_learning.py` 中添加压缩逻辑：

```python
def _save_success_pattern(self, pattern: ExecutionPattern):
    """保存成功模式（去重）"""
    # 1. 读取所有现有模式
    existing = {}
    if self.success_patterns_file.exists():
        with open(self.success_patterns_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    existing[data['pattern_id']] = data
    
    # 2. 更新当前模式
    existing[pattern.pattern_id] = asdict(pattern)
    
    # 3. 重写文件（去重）
    with open(self.success_patterns_file, 'w', encoding='utf-8') as f:
        for data in existing.values():
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
```

### 验证
- 每个 pattern_id 只有一条记录
- 文件大小稳定（不增长）
- 数据不丢失

---

## 🔧 补丁 4：置信度边界保护

### 问题
- 除零错误（success_count + failure_count = 0）
- 置信度超出 [0, 1] 范围

### 解决方案
在所有置信度计算处添加保护：

```python
# 在 adaptive_learning.py 中
def _calculate_confidence(self, success: int, failure: int) -> float:
    """安全的置信度计算"""
    total = success + failure
    if total == 0:
        return 0.0
    
    confidence = success / total
    # 限制在 [0, 1] 范围
    return max(0.0, min(1.0, confidence))
```

### 验证
- 无除零错误
- 置信度始终在 [0, 1]

---

## 🔧 补丁 5：冷启动保护

### 问题
- 无数据时某些功能崩溃
- 空列表/字典访问错误

### 解决方案
在所有数据访问处添加空检查：

```python
# 在 predictive_engine.py 中
def predict_next_task(self) -> Optional[Dict]:
    """预测下一个任务（添加空检查）"""
    if len(self.task_history) < 2:
        return None  # 提前返回
    
    # ... 原有逻辑 ...
```

### 验证
- 冷启动不崩溃
- 返回 None 或空列表（不是异常）

---

## 📊 补丁优先级

| 补丁 | 优先级 | 预计耗时 | 风险 |
|------|--------|----------|------|
| 1. 0.0秒耗时 | P0 | 5分钟 | 低 |
| 2. 间隔误报 | P0 | 10分钟 | 低 |
| 3. JSONL去重 | P1 | 15分钟 | 中 |
| 4. 置信度保护 | P1 | 10分钟 | 低 |
| 5. 冷启动保护 | P2 | 5分钟 | 低 |

**总耗时：** ~45分钟

---

## 🚀 实施顺序

1. **立即修复（P0）：**
   - 补丁 1：0.0秒耗时
   - 补丁 2：间隔误报

2. **今天完成（P1）：**
   - 补丁 3：JSONL去重
   - 补丁 4：置信度保护

3. **明天完成（P2）：**
   - 补丁 5：冷启动保护
   - 端到端回归测试

---

**补丁设计版本：** v1.0  
**创建时间：** 2026-03-02 15:57  
**设计原则：** 最小改动，最大保护
