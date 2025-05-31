#!/usr/bin/env python3
"""
审批功能测试演示
用于验证改进后的审批界面功能
"""

import streamlit as st

def main():
    st.title("🧪 审批功能测试演示")
    
    # 初始化session state
    if 'pending_approvals' not in st.session_state:
        st.session_state.pending_approvals = []
    
    st.markdown("### 测试审批功能")
    
    # 添加测试审批项目按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧮 添加计算审批"):
            approval_id = len(st.session_state.pending_approvals)
            st.session_state.pending_approvals.append({
                'id': approval_id,
                'description': 'Calculate: 15 * 23',
                'action': lambda: "计算结果: 345",
                'status': 'pending'
            })
            st.success("已添加计算审批项目")
            st.rerun()
    
    with col2:
        if st.button("📁 添加文件审批"):
            approval_id = len(st.session_state.pending_approvals)
            st.session_state.pending_approvals.append({
                'id': approval_id,
                'description': 'File operation: read test.txt',
                'action': lambda: "文件内容: Hello World!",
                'status': 'pending'
            })
            st.success("已添加文件审批项目")
            st.rerun()
    
    with col3:
        if st.button("🔍 添加搜索审批"):
            approval_id = len(st.session_state.pending_approvals)
            st.session_state.pending_approvals.append({
                'id': approval_id,
                'description': 'Web search: latest AI news',
                'action': lambda: "搜索结果: AI技术最新进展...",
                'status': 'pending'
            })
            st.success("已添加搜索审批项目")
            st.rerun()
    
    # 显示审批界面（复制主程序的审批逻辑）
    if st.session_state.pending_approvals:
        st.subheader("⏳ 待审批操作")
        st.markdown("以下操作需要您的确认才能执行：")
        
        # 添加快捷键说明
        with st.expander("⌨️ 快捷操作说明", expanded=False):
            st.markdown("""
            **快速审批操作：**
            - 🟢 **全部同意**: 一键同意所有待审批操作
            - 🔴 **全部拒绝**: 一键拒绝所有待审批操作  
            - 🧹 **清理已处理**: 清理已完成的审批记录
            
            **审批建议：**
            - ✅ 计算操作通常是安全的
            - ⚠️ 文件操作需要谨慎考虑
            - 🔍 网络搜索操作请确认查询内容
            """)
        
        # 添加统计信息
        pending_count = sum(1 for approval in st.session_state.pending_approvals if approval['status'] == 'pending')
        processed_count = len(st.session_state.pending_approvals) - pending_count
        
        # 状态统计
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("待审批", pending_count, delta=None)
        with col_stat2:
            approved_count = sum(1 for approval in st.session_state.pending_approvals if approval['status'] == 'approved')
            st.metric("已同意", approved_count, delta=None)
        with col_stat3:
            denied_count = sum(1 for approval in st.session_state.pending_approvals if approval['status'] == 'denied')
            st.metric("已拒绝", denied_count, delta=None)
        
        # 批量操作按钮
        if pending_count > 1:
            st.markdown("---")
            col_batch1, col_batch2, col_batch3 = st.columns([1, 1, 2])
            with col_batch1:
                if st.button("✅ 全部同意", type="primary", use_container_width=True):
                    for approval in st.session_state.pending_approvals:
                        if approval['status'] == 'pending':
                            try:
                                result = approval['action']()
                                approval['status'] = 'approved'
                                st.success(f"✅ 已执行：{result}")
                            except Exception as e:
                                st.error(f"❌ 执行操作时出错：{str(e)}")
                    st.success("✅ 已同意所有待审批操作")
                    st.rerun()
            
            with col_batch2:
                if st.button("❌ 全部拒绝", type="secondary", use_container_width=True):
                    for approval in st.session_state.pending_approvals:
                        if approval['status'] == 'pending':
                            approval['status'] = 'denied'
                    st.warning("⚠️ 已拒绝所有待审批操作")
                    st.rerun()
            
            with col_batch3:
                if st.button("🧹 清理已处理", help="清理已同意或拒绝的审批记录"):
                    st.session_state.pending_approvals = [
                        approval for approval in st.session_state.pending_approvals 
                        if approval['status'] == 'pending'
                    ]
                    st.info("🧹 已清理处理完成的审批记录")
                    st.rerun()
        
        st.markdown("---")
        
        # 分别显示待审批和已处理的操作
        # 待审批操作
        pending_approvals = [approval for approval in st.session_state.pending_approvals if approval['status'] == 'pending']
        if pending_approvals:
            st.markdown("### 🔄 待审批操作")
            for approval in pending_approvals:
                # Create a card-like container for each approval
                with st.container():
                    # 使用颜色编码的边框
                    st.markdown("""
                    <div style="
                        border: 2px solid #ffa726; 
                        border-radius: 10px; 
                        padding: 15px; 
                        margin: 10px 0;
                        background-color: rgba(255, 167, 38, 0.1);
                    ">
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**🔍 操作内容：** {approval['description']}")
                        st.caption(f"📋 审批 ID: #{approval['id']} | ⏰ 状态: 等待审批")
                        
                        # 添加风险等级判断
                        description = approval['description'].lower()
                        if 'calculate' in description or '计算' in description:
                            risk_level = "🟢 低风险"
                            risk_color = "#4caf50"
                            risk_desc = "计算操作，通常安全"
                        elif 'file' in description or '文件' in description:
                            risk_level = "🟡 中风险"  
                            risk_color = "#ff9800"
                            risk_desc = "文件操作，请确认路径和内容"
                        elif 'web' in description or 'search' in description or '搜索' in description:
                            risk_level = "🟡 中风险"
                            risk_color = "#ff9800" 
                            risk_desc = "网络搜索，请确认查询内容"
                        elif 'mcp' in description:
                            risk_level = "🟠 高风险"
                            risk_color = "#f44336"
                            risk_desc = "外部服务调用，请谨慎确认"
                        else:
                            risk_level = "⚪ 未知风险"
                            risk_color = "#9e9e9e"
                            risk_desc = "请仔细检查操作内容"
                        
                        st.markdown(f"""
                        <div style="
                            background-color: rgba(128, 128, 128, 0.1);
                            padding: 8px;
                            border-radius: 5px;
                            border-left: 4px solid {risk_color};
                            margin-top: 8px;
                        ">
                        <small><strong>{risk_level}</strong> - {risk_desc}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Create two columns for approve/deny buttons
                        btn_col1, btn_col2 = st.columns(2)
                        
                        with btn_col1:
                            if st.button(
                                "✅ 同意", 
                                key=f"approve_{approval['id']}", 
                                type="primary", 
                                use_container_width=True,
                                help="点击同意执行此操作"
                            ):
                                try:
                                    result = approval['action']()
                                    approval['status'] = 'approved'
                                    st.success(f"✅ 已同意并执行操作：{approval['description']}")
                                    st.info(f"执行结果：{result}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 执行批准操作时出错：{str(e)}")
                        
                        with btn_col2:
                            if st.button(
                                "❌ 拒绝", 
                                key=f"deny_{approval['id']}", 
                                type="secondary", 
                                use_container_width=True,
                                help="点击拒绝此操作"
                            ):
                                approval['status'] = 'denied'
                                st.warning(f"⚠️ 已拒绝操作：{approval['description']}")
                                st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        
        # 已处理操作 (可折叠显示)
        processed_approvals = [approval for approval in st.session_state.pending_approvals if approval['status'] != 'pending']
        if processed_approvals:
            with st.expander(f"📋 查看已处理操作 ({len(processed_approvals)} 个)", expanded=False):
                for approval in processed_approvals:
                    # 根据状态设置颜色
                    if approval['status'] == 'approved':
                        border_color = "#4caf50"  # 绿色
                        bg_color = "rgba(76, 175, 80, 0.1)"
                        status_icon = "✅"
                        status_text = "已同意"
                    else:  # denied
                        border_color = "#f44336"  # 红色
                        bg_color = "rgba(244, 67, 54, 0.1)"
                        status_icon = "❌"
                        status_text = "已拒绝"
                    
                    st.markdown(f"""
                    <div style="
                        border: 2px solid {border_color}; 
                        border-radius: 10px; 
                        padding: 10px; 
                        margin: 5px 0;
                        background-color: {bg_color};
                    ">
                    <strong>{status_icon} 操作内容：</strong> {approval['description']}<br>
                    <small>📋 审批 ID: #{approval['id']} | 📊 状态: {status_text}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        # Show summary
        if pending_count > 0:
            st.info(f"💡 共有 {pending_count} 个操作待审批，请及时处理")
        else:
            st.success("✅ 所有操作已处理完成")
    
    else:
        st.info("🔵 当前没有待审批的操作。点击上方按钮添加测试审批项目。")
    
    # 清空所有审批记录
    if st.button("🗑️ 清空所有记录", type="secondary"):
        st.session_state.pending_approvals = []
        st.success("已清空所有审批记录")
        st.rerun()

if __name__ == "__main__":
    main() 