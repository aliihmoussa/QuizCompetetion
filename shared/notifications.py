"""
Notification system for real-time user feedback
"""
import streamlit as st
from typing import Literal, Optional
from datetime import datetime


NotificationType = Literal['info', 'success', 'warning', 'error']


def show_toast(message: str, icon: str = "ℹ️", duration: int = 3):
    """
    Show a toast notification (using Streamlit's native toast if available)
    
    Args:
        message: Notification message
        icon: Emoji icon
        duration: Duration in seconds (for display purposes)
    """
    # Streamlit 1.31+ has st.toast()
    try:
        st.toast(f"{icon} {message}", icon=icon)
    except AttributeError:
        # Fallback for older versions
        st.info(f"{icon} {message}")


def notify_success(message: str):
    """Show success notification"""
    show_toast(message, icon="✅")


def notify_error(message: str):
    """Show error notification"""
    show_toast(message, icon="❌")


def notify_warning(message: str):
    """Show warning notification"""
    show_toast(message, icon="⚠️")


def notify_info(message: str):
    """Show info notification"""
    show_toast(message, icon="ℹ️")


class NotificationQueue:
    """Queue system for managing multiple notifications"""
    
    def __init__(self):
        if 'notification_queue' not in st.session_state:
            st.session_state.notification_queue = []
    
    def add(self, message: str, type: NotificationType = 'info', icon: Optional[str] = None):
        """Add notification to queue"""
        # Initialize if not exists
        if 'notification_queue' not in st.session_state:
            st.session_state.notification_queue = []
        
        default_icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        notification = {
            'message': message,
            'type': type,
            'icon': icon or default_icons.get(type, 'ℹ️'),
            'timestamp': datetime.now(),
            'shown': False
        }
        
        st.session_state.notification_queue.append(notification)
    
    def show_all(self):
        """Display all queued notifications"""
        # Initialize if not exists
        if 'notification_queue' not in st.session_state:
            st.session_state.notification_queue = []
        
        if not st.session_state.notification_queue:
            return
        
        for notification in st.session_state.notification_queue:
            if not notification['shown']:
                show_toast(notification['message'], notification['icon'])
                notification['shown'] = True
        
        # Clear shown notifications
        st.session_state.notification_queue = [
            n for n in st.session_state.notification_queue if not n['shown']
        ]
    
    def clear(self):
        """Clear all notifications"""
        if 'notification_queue' not in st.session_state:
            st.session_state.notification_queue = []
        st.session_state.notification_queue = []
    
    def get_count(self) -> int:
        """Get count of unshown notifications"""
        if 'notification_queue' not in st.session_state:
            st.session_state.notification_queue = []
        return len([n for n in st.session_state.notification_queue if not n['shown']])


# Global notification queue instance
notification_queue = NotificationQueue()


def notify(message: str, type: NotificationType = 'info', icon: Optional[str] = None):
    """
    Add a notification to the queue
    
    Args:
        message: Notification message
        type: Notification type (info, success, warning, error)
        icon: Optional custom icon
    """
    notification_queue.add(message, type, icon)


def display_notifications():
    """Display all queued notifications - call this at the top of each page"""
    notification_queue.show_all()


class ActivityFeed:
    """Activity feed for showing recent events"""
    
    def __init__(self, max_items: int = 10):
        self.max_items = max_items
        if 'activity_feed' not in st.session_state:
            st.session_state.activity_feed = []
    
    def add_activity(
        self,
        title: str,
        description: str,
        icon: str = "📌",
        category: str = "general"
    ):
        """Add an activity to the feed"""
        # Initialize if not exists
        if 'activity_feed' not in st.session_state:
            st.session_state.activity_feed = []
        
        activity = {
            'title': title,
            'description': description,
            'icon': icon,
            'category': category,
            'timestamp': datetime.now()
        }
        
        # Add to beginning of list
        st.session_state.activity_feed.insert(0, activity)
        
        # Keep only max_items
        st.session_state.activity_feed = st.session_state.activity_feed[:self.max_items]
    
    def get_activities(self, limit: Optional[int] = None) -> list:
        """Get recent activities"""
        # Initialize if not exists
        if 'activity_feed' not in st.session_state:
            st.session_state.activity_feed = []
        
        activities = st.session_state.activity_feed
        if limit:
            return activities[:limit]
        return activities
    
    def clear(self):
        """Clear all activities"""
        if 'activity_feed' not in st.session_state:
            st.session_state.activity_feed = []
        st.session_state.activity_feed = []
    
    def display(self, title: str = "Recent Activity", limit: int = 10):
        """Display activity feed"""
        st.subheader(title)
        
        activities = self.get_activities(limit)
        
        if not activities:
            st.info("No recent activity")
            return
        
        for activity in activities:
            # Format relative time
            now = datetime.now()
            diff = now - activity['timestamp']
            
            if diff.seconds < 60:
                time_str = "Just now"
            elif diff.seconds < 3600:
                mins = diff.seconds // 60
                time_str = f"{mins}m ago"
            elif diff.seconds < 86400:
                hours = diff.seconds // 3600
                time_str = f"{hours}h ago"
            else:
                time_str = activity['timestamp'].strftime("%b %d")
            
            # Display activity
            with st.container():
                col1, col2 = st.columns([1, 20])
                with col1:
                    st.write(activity['icon'])
                with col2:
                    st.markdown(f"**{activity['title']}**")
                    st.caption(f"{activity['description']} • {time_str}")
                st.divider()


# Global activity feed instance
activity_feed = ActivityFeed()


def log_activity(title: str, description: str, icon: str = "📌", category: str = "general"):
    """
    Log an activity to the feed
    
    Args:
        title: Activity title
        description: Activity description
        icon: Emoji icon
        category: Activity category
    """
    activity_feed.add_activity(title, description, icon, category)

