"""
测试 Superpowers Mode
"""

import json
from aios.sdk.superpowers import SuperpowersMode, superpower


def test_basic():
    """测试基础功能"""
    print("=" * 60)
    print("测试 1: 基础功能")
    print("=" * 60)
    
    result = superpower("测试 Superpowers 模式")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert result["success"] == True
    assert "task_id" in result
    print("✅ 基础功能测试通过\n")


def test_with_context():
    """测试带上下文"""
    print("=" * 60)
    print("测试 2: 带上下文")
    print("=" * 60)
    
    result = superpower(
        "分析数据",
        context={"data": [1, 2, 3, 4, 5]}
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert result["success"] == True
    print("✅ 上下文测试通过\n")


def test_custom_params():
    """测试自定义参数"""
    print("=" * 60)
    print("测试 3: 自定义参数")
    print("=" * 60)
    
    result = superpower(
        "复杂任务",
        max_steps=20,
        timeout=600
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert result["success"] == True
    print("✅ 自定义参数测试通过\n")


def test_class_usage():
    """测试类用法"""
    print("=" * 60)
    print("测试 4: 类用法")
    print("=" * 60)
    
    mode = SuperpowersMode()
    result = mode.execute("测试类用法")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert result["success"] == True
    print("✅ 类用法测试通过\n")


def test_error_handling():
    """测试错误处理"""
    print("=" * 60)
    print("测试 5: 错误处理")
    print("=" * 60)
    
    # 故意触发超时
    result = superpower(
        "超时任务",
        max_steps=1000,
        timeout=1  # 1秒超时
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert result["success"] == False
    assert "error" in result
    print("✅ 错误处理测试通过\n")


if __name__ == "__main__":
    print("\n🚀 开始测试 Superpowers Mode\n")
    
    try:
        test_basic()
        test_with_context()
        test_custom_params()
        test_class_usage()
        test_error_handling()
        
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
