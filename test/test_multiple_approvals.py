"""
测试多次审批请求的情况
模拟用户报告的"第三次会出现不审批直接执行"的问题
"""

import time

# 模拟 session state
class MockSessionState:
    def __init__(self):
        self.pending_approvals = []
        self.has_new_approval = False
        self.force_approval_check = False
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
    
    # 详细调试信息
    print(f"🔍 DEBUG: 创建了新的审批请求 - ID: {approval_id}, 状态: {approval['status']}, 描述: {action_description}")
    print(f"🔍 DEBUG: 当前总审批数量: {len(session_state.pending_approvals)}")
    print(f"🔍 DEBUG: 创建前 has_new_approval 状态: {session_state.get('has_new_approval', False)}")
    print(f"🔍 DEBUG: 创建前 approval_ui_shown 状态: {session_state.get('approval_ui_shown', False)}")
    
    # 设置新审批标志
    session_state.has_new_approval = True
    session_state.force_approval_check = True
    
    print(f"🔍 DEBUG: 创建后设置 has_new_approval = True")
    print(f"🔍 DEBUG: 创建后设置 force_approval_check = True")
    
    return f"我已经提交了{action_description}以供批准。请检查上面的批准部分以批准或拒绝此操作。"

def mock_ui_check(session_state):
    """模拟UI检查逻辑"""
    print(f"\n--- 开始UI检查 ---")
    print(f"has_new_approval: {session_state.get('has_new_approval', False)}")
    print(f"force_approval_check: {session_state.get('force_approval_check', False)}")
    print(f"approval_ui_shown: {session_state.get('approval_ui_shown', False)}")
    
    # 检查has_new_approval标志
    if session_state.get('has_new_approval', False):
        session_state.has_new_approval = False
        print("✅ 检测到 has_new_approval，应该触发 st.rerun()")
        return True
    
    # 检查force_approval_check标志
    if session_state.get('force_approval_check', False):
        print("🔍 检测到 force_approval_check 标志，强制检查审批状态")
        session_state.force_approval_check = False
        if any(approval.get('status') == 'pending' for approval in session_state.pending_approvals):
            print("✅ 发现待审批操作，应该触发 st.rerun()")
            return True
    
    # 最终保障检查
    current_pending = sum(1 for approval in session_state.pending_approvals if approval.get('status') == 'pending')
    if current_pending > 0 and not session_state.get('approval_ui_shown', False):
        print(f"🔍 最终保障检查 - 发现 {current_pending} 个待审批操作，强制显示UI")
        session_state.approval_ui_shown = True
        return True
    
    print("❌ 没有检测到需要显示审批UI的条件")
    return False

def mock_approve_action(session_state, approval_id):
    """模拟审批同意操作"""
    print(f"\n--- 执行审批同意 ID: {approval_id} ---")
    
    for approval in session_state.pending_approvals:
        if approval['id'] == approval_id:
            result = approval['action']()
            approval['status'] = 'approved'
            
            # 仅在所有待审批操作都处理完成后才重置UI标志
            remaining_pending = sum(1 for a in session_state.pending_approvals if a.get('status') == 'pending' and a['id'] != approval['id'])
            if remaining_pending == 0:
                session_state.approval_ui_shown = False
            
            print(f"🔍 DEBUG: 审批 {approval['id']} 已同意，剩余待审批: {remaining_pending}")
            print(f"✅ 审批操作执行成功: {result}")
            return True
    
    print(f"❌ 未找到 ID {approval_id} 的审批请求")
    return False

def test_multiple_approvals():
    print("=== 测试多次审批请求情况 ===")
    
    # 创建模拟session state
    mock_session = MockSessionState()
    
    # 模拟三次计算请求
    calculations = [
        ("Calculate: 15 * 23", lambda: "15 * 23 = 345"),
        ("Calculate: 50 + 30", lambda: "50 + 30 = 80"),
        ("Calculate: 100 / 4", lambda: "100 / 4 = 25")
    ]
    
    for i, (desc, func) in enumerate(calculations, 1):
        print(f"\n{'='*60}")
        print(f"第 {i} 次计算请求: {desc}")
        print(f"{'='*60}")
        
        # 1. 创建审批请求
        result = mock_request_approval(desc, func, mock_session)
        print(f"审批请求返回: {result}")
        
        # 2. 模拟UI检查
        ui_should_show = mock_ui_check(mock_session)
        
        if ui_should_show:
            print("✅ UI应该显示审批按钮")
        else:
            print("❌ UI不会显示审批按钮 - 这是问题！")
        
        # 3. 显示当前状态
        pending_count = sum(1 for approval in mock_session.pending_approvals if approval.get('status') == 'pending')
        print(f"当前待审批数量: {pending_count}")
        
        # 4. 模拟用户同意审批（只处理当前的审批）
        if pending_count > 0:
            # 找到最新的待审批操作
            for approval in reversed(mock_session.pending_approvals):
                if approval.get('status') == 'pending':
                    mock_approve_action(mock_session, approval['id'])
                    break
        
        # 5. 显示最终状态
        final_pending = sum(1 for approval in mock_session.pending_approvals if approval.get('status') == 'pending')
        final_approved = sum(1 for approval in mock_session.pending_approvals if approval['status'] == 'approved')
        print(f"处理后状态 - 待审批: {final_pending}, 已同意: {final_approved}")
        
        time.sleep(0.1)  # 短暂延迟模拟时间流逝
    
    print(f"\n{'='*60}")
    print("最终总结")
    print(f"{'='*60}")
    total_approvals = len(mock_session.pending_approvals)
    total_approved = sum(1 for approval in mock_session.pending_approvals if approval['status'] == 'approved')
    total_pending = sum(1 for approval in mock_session.pending_approvals if approval.get('status') == 'pending')
    
    print(f"总审批请求数: {total_approvals}")
    print(f"已同意数量: {total_approved}")
    print(f"待审批数量: {total_pending}")
    
    print(f"\n所有审批详情:")
    for approval in mock_session.pending_approvals:
        print(f"  ID {approval['id']}: {approval['description']} - 状态: {approval['status']}")

if __name__ == "__main__":
    test_multiple_approvals() 