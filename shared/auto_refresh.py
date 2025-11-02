"""
Auto-refresh utilities for real-time updates without manual page refreshes
"""
import streamlit as st
import time
from typing import Optional


def auto_refresh_component(
    interval_seconds: int = 5,
    key: str = "auto_refresh",
    label: str = "Auto-refreshing",
    show_indicator: bool = True
):
    """
    Add auto-refresh functionality to the current page
    
    Args:
        interval_seconds: Refresh interval in seconds
        key: Unique key for this refresh component
        label: Label to show in indicator
        show_indicator: Whether to show refresh indicator
    """
    # Initialize refresh state
    if f'{key}_enabled' not in st.session_state:
        st.session_state[f'{key}_enabled'] = True
    
    if f'{key}_last_refresh' not in st.session_state:
        st.session_state[f'{key}_last_refresh'] = time.time()
    
    # Show refresh indicator and controls
    if show_indicator:
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col2:
            if st.session_state[f'{key}_enabled']:
                st.markdown(
                    """
                    <div style="text-align: center; color: #10B981;">
                        <div class="spinner" style="display: inline-block;">🔄</div>
                        <div style="font-size: 0.75rem; margin-top: 0.25rem;">Live</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="text-align: center; color: #6B7280;">
                        <div>⏸️</div>
                        <div style="font-size: 0.75rem; margin-top: 0.25rem;">Paused</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with col3:
            toggle_label = "⏸️" if st.session_state[f'{key}_enabled'] else "▶️"
            if st.button(toggle_label, key=f"{key}_toggle"):
                st.session_state[f'{key}_enabled'] = not st.session_state[f'{key}_enabled']
                st.rerun()
    
    # Trigger refresh if enabled
    if st.session_state[f'{key}_enabled']:
        current_time = time.time()
        elapsed = current_time - st.session_state[f'{key}_last_refresh']
        
        if elapsed >= interval_seconds:
            st.session_state[f'{key}_last_refresh'] = current_time
            time.sleep(0.1)  # Small delay to prevent too rapid refreshes
            st.rerun()


def enable_auto_refresh(key: str = "auto_refresh"):
    """Enable auto-refresh for a page"""
    if f'{key}_enabled' not in st.session_state:
        st.session_state[f'{key}_enabled'] = True
    else:
        st.session_state[f'{key}_enabled'] = True


def disable_auto_refresh(key: str = "auto_refresh"):
    """Disable auto-refresh for a page"""
    st.session_state[f'{key}_enabled'] = False


def is_auto_refresh_enabled(key: str = "auto_refresh") -> bool:
    """Check if auto-refresh is enabled"""
    return st.session_state.get(f'{key}_enabled', False)


def refresh_countdown(interval_seconds: int, key: str = "refresh_countdown"):
    """
    Display a countdown timer until next refresh
    
    Args:
        interval_seconds: Refresh interval in seconds
        key: Unique key for countdown
    """
    if f'{key}_last' not in st.session_state:
        st.session_state[f'{key}_last'] = time.time()
    
    elapsed = time.time() - st.session_state[f'{key}_last']
    remaining = max(0, interval_seconds - int(elapsed))
    
    st.caption(f"Next refresh in {remaining}s")
    
    if elapsed >= interval_seconds:
        st.session_state[f'{key}_last'] = time.time()
        st.rerun()


class RefreshManager:
    """Manager for handling multiple refresh contexts"""
    
    def __init__(self, default_interval: int = 5):
        self.default_interval = default_interval
        self.contexts = {}
    
    def register_context(self, name: str, interval: Optional[int] = None):
        """Register a new refresh context"""
        self.contexts[name] = interval or self.default_interval
    
    def should_refresh(self, context: str) -> bool:
        """Check if context should refresh"""
        key = f"refresh_manager_{context}"
        
        if key not in st.session_state:
            st.session_state[key] = {
                'last_refresh': time.time(),
                'enabled': True
            }
        
        if not st.session_state[key]['enabled']:
            return False
        
        interval = self.contexts.get(context, self.default_interval)
        elapsed = time.time() - st.session_state[key]['last_refresh']
        
        if elapsed >= interval:
            st.session_state[key]['last_refresh'] = time.time()
            return True
        
        return False
    
    def enable_context(self, context: str):
        """Enable refresh for a context"""
        key = f"refresh_manager_{context}"
        if key in st.session_state:
            st.session_state[key]['enabled'] = True
    
    def disable_context(self, context: str):
        """Disable refresh for a context"""
        key = f"refresh_manager_{context}"
        if key in st.session_state:
            st.session_state[key]['enabled'] = False

