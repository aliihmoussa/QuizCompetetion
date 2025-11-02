"""
Centralized state management for Streamlit applications
Provides clean API for session state operations with type safety and persistence
"""
import streamlit as st
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import json


class StateManager:
    """
    Centralized manager for Streamlit session state
    Provides clean API and helper methods for state operations
    """
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get value from session state
        
        Args:
            key: State key
            default: Default value if key doesn't exist
        
        Returns:
            Value from session state or default
        """
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """
        Set value in session state
        
        Args:
            key: State key
            value: Value to store
        """
        st.session_state[key] = value
    
    @staticmethod
    def update(updates: Dict[str, Any]) -> None:
        """
        Update multiple values in session state
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        st.session_state.update(updates)
    
    @staticmethod
    def delete(key: str) -> bool:
        """
        Delete key from session state
        
        Args:
            key: State key to delete
        
        Returns:
            True if key was deleted, False if key didn't exist
        """
        if key in st.session_state:
            del st.session_state[key]
            return True
        return False
    
    @staticmethod
    def clear(keys: Optional[List[str]] = None) -> None:
        """
        Clear session state
        
        Args:
            keys: Optional list of specific keys to clear.
                  If None, clears entire session state.
        """
        if keys is None:
            # Clear all
            for key in list(st.session_state.keys()):
                del st.session_state[key]
        else:
            # Clear specific keys
            for key in keys:
                StateManager.delete(key)
    
    @staticmethod
    def exists(key: str) -> bool:
        """
        Check if key exists in session state
        
        Args:
            key: State key to check
        
        Returns:
            True if key exists, False otherwise
        """
        return key in st.session_state
    
    @staticmethod
    def get_or_set(key: str, factory: Callable[[], Any]) -> Any:
        """
        Get value from state, or compute and store it if it doesn't exist
        
        Args:
            key: State key
            factory: Function to compute value if key doesn't exist
        
        Returns:
            Value from state or newly computed value
        
        Example:
            data = StateManager.get_or_set(
                'expensive_data',
                lambda: expensive_computation()
            )
        """
        if not StateManager.exists(key):
            value = factory()
            StateManager.set(key, value)
            return value
        return StateManager.get(key)
    
    @staticmethod
    def increment(key: str, amount: int = 1, initial: int = 0) -> int:
        """
        Increment numeric value in state
        
        Args:
            key: State key
            amount: Amount to increment by (default: 1)
            initial: Initial value if key doesn't exist (default: 0)
        
        Returns:
            New value after increment
        """
        current = StateManager.get(key, initial)
        new_value = current + amount
        StateManager.set(key, new_value)
        return new_value
    
    @staticmethod
    def toggle(key: str, initial: bool = False) -> bool:
        """
        Toggle boolean value in state
        
        Args:
            key: State key
            initial: Initial value if key doesn't exist (default: False)
        
        Returns:
            New value after toggle
        """
        current = StateManager.get(key, initial)
        new_value = not current
        StateManager.set(key, new_value)
        return new_value
    
    @staticmethod
    def append(key: str, value: Any, max_length: Optional[int] = None) -> List:
        """
        Append value to list in state
        
        Args:
            key: State key
            value: Value to append
            max_length: Optional maximum list length (FIFO if exceeded)
        
        Returns:
            Updated list
        """
        current_list = StateManager.get(key, [])
        if not isinstance(current_list, list):
            current_list = []
        
        current_list.append(value)
        
        # Trim if max_length specified
        if max_length and len(current_list) > max_length:
            current_list = current_list[-max_length:]
        
        StateManager.set(key, current_list)
        return current_list
    
    @staticmethod
    def get_all() -> Dict[str, Any]:
        """
        Get all session state as dictionary
        
        Returns:
            Dictionary of all session state
        """
        return dict(st.session_state)
    
    @staticmethod
    def keys() -> List[str]:
        """
        Get all keys in session state
        
        Returns:
            List of all keys
        """
        return list(st.session_state.keys())
    
    @staticmethod
    def size() -> int:
        """
        Get number of keys in session state
        
        Returns:
            Number of keys
        """
        return len(st.session_state)


class NamespacedState:
    """
    Namespaced state manager for organizing related state
    
    Example:
        user_state = NamespacedState('user')
        user_state.set('name', 'John')
        user_state.get('name')  # 'John'
    """
    
    def __init__(self, namespace: str):
        """
        Initialize namespaced state manager
        
        Args:
            namespace: Namespace prefix for all keys
        """
        self.namespace = namespace
    
    def _key(self, key: str) -> str:
        """Generate namespaced key"""
        return f"{self.namespace}.{key}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from namespaced state"""
        return StateManager.get(self._key(key), default)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in namespaced state"""
        StateManager.set(self._key(key), value)
    
    def delete(self, key: str) -> bool:
        """Delete key from namespaced state"""
        return StateManager.delete(self._key(key))
    
    def exists(self, key: str) -> bool:
        """Check if key exists in namespaced state"""
        return StateManager.exists(self._key(key))
    
    def clear(self) -> None:
        """Clear all keys in this namespace"""
        prefix = f"{self.namespace}."
        keys_to_delete = [k for k in StateManager.keys() if k.startswith(prefix)]
        StateManager.clear(keys_to_delete)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all values in this namespace"""
        prefix = f"{self.namespace}."
        return {
            k.replace(prefix, ''): v
            for k, v in StateManager.get_all().items()
            if k.startswith(prefix)
        }


class PersistentState:
    """
    State manager with persistence to browser localStorage (via query params hack)
    
    Note: Limited to serializable data types
    """
    
    @staticmethod
    def save_to_query_params(key: str, value: Any) -> None:
        """
        Save state to query parameters (persists across reloads)
        
        Args:
            key: State key
            value: Value to save (must be JSON serializable)
        """
        try:
            serialized = json.dumps(value)
            st.query_params[key] = serialized
        except (TypeError, ValueError) as e:
            print(f"Cannot serialize {key}: {e}")
    
    @staticmethod
    def load_from_query_params(key: str, default: Any = None) -> Any:
        """
        Load state from query parameters
        
        Args:
            key: State key
            default: Default value if key doesn't exist
        
        Returns:
            Deserialized value or default
        """
        try:
            if key in st.query_params:
                serialized = st.query_params[key]
                return json.loads(serialized)
        except (json.JSONDecodeError, KeyError):
            pass
        return default


class StateHistory:
    """
    Track state history for undo/redo functionality
    
    Example:
        history = StateHistory('form_data')
        history.save({'name': 'John'})
        history.save({'name': 'Jane'})
        history.undo()  # Back to {'name': 'John'}
    """
    
    def __init__(self, key: str, max_history: int = 10):
        """
        Initialize state history tracker
        
        Args:
            key: State key to track
            max_history: Maximum number of history items to keep
        """
        self.key = key
        self.max_history = max_history
        self.history_key = f"_history_{key}"
        self.position_key = f"_history_pos_{key}"
        
        # Initialize history
        if not StateManager.exists(self.history_key):
            StateManager.set(self.history_key, [])
            StateManager.set(self.position_key, -1)
    
    def save(self, value: Any) -> None:
        """Save current state to history"""
        history = StateManager.get(self.history_key, [])
        position = StateManager.get(self.position_key, -1)
        
        # Remove any "future" states if we're not at the end
        if position < len(history) - 1:
            history = history[:position + 1]
        
        # Add new state
        history.append(value)
        
        # Trim if exceeds max
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        
        # Update state
        StateManager.set(self.history_key, history)
        StateManager.set(self.position_key, len(history) - 1)
        StateManager.set(self.key, value)
    
    def undo(self) -> Optional[Any]:
        """Undo to previous state"""
        history = StateManager.get(self.history_key, [])
        position = StateManager.get(self.position_key, -1)
        
        if position > 0:
            position -= 1
            value = history[position]
            StateManager.set(self.position_key, position)
            StateManager.set(self.key, value)
            return value
        return None
    
    def redo(self) -> Optional[Any]:
        """Redo to next state"""
        history = StateManager.get(self.history_key, [])
        position = StateManager.get(self.position_key, -1)
        
        if position < len(history) - 1:
            position += 1
            value = history[position]
            StateManager.set(self.position_key, position)
            StateManager.set(self.key, value)
            return value
        return None
    
    def can_undo(self) -> bool:
        """Check if undo is possible"""
        position = StateManager.get(self.position_key, -1)
        return position > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible"""
        history = StateManager.get(self.history_key, [])
        position = StateManager.get(self.position_key, -1)
        return position < len(history) - 1
    
    def clear_history(self) -> None:
        """Clear all history"""
        StateManager.delete(self.history_key)
        StateManager.delete(self.position_key)


# Convenience functions
def use_state(key: str, initial_value: Any = None) -> tuple[Any, Callable]:
    """
    React-like useState hook for Streamlit
    
    Args:
        key: State key
        initial_value: Initial value if key doesn't exist
    
    Returns:
        Tuple of (current_value, setter_function)
    
    Example:
        count, set_count = use_state('count', 0)
        if st.button('Increment'):
            set_count(count + 1)
    """
    if not StateManager.exists(key):
        StateManager.set(key, initial_value)
    
    current_value = StateManager.get(key)
    
    def setter(value: Any):
        StateManager.set(key, value)
    
    return current_value, setter

