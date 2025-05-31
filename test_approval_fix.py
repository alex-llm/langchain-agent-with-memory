"""
测试审批系统修复
验证审批请求是否正确创建并保存到session state
"""

import streamlit as st
import time

# 模拟 session state
class MockSessionState:
    def __init__(self):
        self.pending_approvals = []
        self.has_new_approval = False
        self.approval_ui_shown = False
    
    def get(self, key, default=None):
        return getattr(self, key, default)

# 模拟审批请求函数
def mock_request_approval(action_description, action_func, session_state):
    """模拟 _request_approval 方法"""
    if not hasattr(session_state, 'pending_approvals'):
        session_state.pending_approvals = []
    
    approval_id = len(session_state.pending_approvals)
    timestamp = int(time.time() * 1000)
    
    approval = {
        'id': approval_id,
        'timestamp': timestamp,
        'description': action_description,
        'action': action_func,
        'status': 'pending'
    }
    session_state.pending_approvals.append(approval)
    
    # 设置新审批标志
    session_state.has_new_approval = True
    
    print(f"🔍 DEBUG: 创建了新的审批请求 - ID: {approval_id}, 状态: {approval['status']}, 描述: {action_description}")
    print(f"🔍 DEBUG: 当前总审批数量: {len(session_state.pending_approvals)}")
    
    return f"我已经提交了{action_description}以供批准。请检查上面的批准部分以批准或拒绝此操作。"

# 测试函数
def test_approval_system():
    print("=== 测试审批系统修复 ===")
    
    # 创建模拟session state
    mock_session = MockSessionState()
    
    # 测试创建审批请求
    def mock_calculator():
        return "15 * 23 = 345"
    
    print("\n1. 测试创建审批请求:")
    result = mock_request_approval("Calculate: 15 * 23", mock_calculator, mock_session)
    print(f"返回结果: {result}")
    
    print(f"\n2. 检查session state状态:")
    print(f"   - pending_approvals 数量: {len(mock_session.pending_approvals)}")
    print(f"   - has_new_approval: {mock_session.has_new_approval}")
    print(f"   - approval_ui_shown: {mock_session.approval_ui_shown}")
    
    print(f"\n3. 审批请求详情:")
    for i, approval in enumerate(mock_session.pending_approvals):
        print(f"   审批 {i}:")
        print(f"     - ID: {approval['id']}")
        print(f"     - 描述: {approval['description']}")
        print(f"     - 状态: {approval['status']}")
        print(f"     - 时间戳: {approval['timestamp']}")
    
    # 测试统计pending状态的数量
    pending_count = sum(1 for approval in mock_session.pending_approvals if approval.get('status') == 'pending')
    print(f"\n4. Pending状态操作数量: {pending_count}")
    
    # 测试审批一个操作
    print(f"\n5. 测试执行审批:")
    if mock_session.pending_approvals:
        approval = mock_session.pending_approvals[0]
        try:
            result = approval['action']()
            approval['status'] = 'approved'
            print(f"   审批执行成功: {result}")
            print(f"   状态已更新为: {approval['status']}")
        except Exception as e:
            print(f"   审批执行失败: {e}")
    
    # 再次检查状态
    pending_count = sum(1 for approval in mock_session.pending_approvals if approval.get('status') == 'pending')
    approved_count = sum(1 for approval in mock_session.pending_approvals if approval['status'] == 'approved')
    print(f"\n6. 最终状态:")
    print(f"   - Pending: {pending_count}")
    print(f"   - Approved: {approved_count}")
    print(f"   - Total: {len(mock_session.pending_approvals)}")

if __name__ == "__main__":
    test_approval_system() 