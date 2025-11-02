"""
High-performance decorators for caching, error handling, and monitoring
Following Streamlit best practices for optimal performance
"""
import streamlit as st
import functools
import time
from typing import Callable, Any, Optional
from datetime import datetime


def cache_with_ttl(ttl_seconds: int = 300, key_prefix: str = ""):
    """
    Smart caching decorator with TTL (Time To Live)
    
    Args:
        ttl_seconds: Cache lifetime in seconds (default: 5 minutes)
        key_prefix: Optional prefix for cache key
    
    Usage:
        @cache_with_ttl(ttl_seconds=60)
        def expensive_query(user_id):
            return database.query(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use Streamlit's built-in caching with TTL
            cached_func = st.cache_data(ttl=ttl_seconds, show_spinner=False)(func)
            return cached_func(*args, **kwargs)
        return wrapper
    return decorator


def handle_errors(
    fallback_message: str = "An error occurred",
    show_traceback: bool = False,
    log_error: bool = True,
    fallback_value: Any = None
):
    """
    Graceful error handling decorator with user-friendly messages
    
    Args:
        fallback_message: Message to show users on error
        show_traceback: Whether to show full traceback (dev mode)
        log_error: Whether to log error to console
        fallback_value: Value to return on error
    
    Usage:
        @handle_errors(fallback_message="Failed to load data")
        def load_user_data(user_id):
            return database.get_user(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    print(f"[ERROR] {func.__name__}: {str(e)}")
                
                if show_traceback:
                    st.error(f"{fallback_message}\n\n```\n{str(e)}\n```")
                else:
                    st.error(f"❌ {fallback_message}")
                
                return fallback_value
        return wrapper
    return decorator


def performance_monitor(threshold_ms: float = 1000.0, show_warning: bool = False):
    """
    Monitor function performance and log slow operations
    
    Args:
        threshold_ms: Warning threshold in milliseconds
        show_warning: Whether to show warning to user for slow operations
    
    Usage:
        @performance_monitor(threshold_ms=500)
        def complex_calculation(data):
            # Automatically monitored
            return process(data)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_ms = (time.time() - start_time) * 1000
            
            if elapsed_ms > threshold_ms:
                message = f"⚠️ Slow operation: {func.__name__} took {elapsed_ms:.2f}ms"
                print(message)
                
                if show_warning:
                    st.warning(message, icon="⏱️")
            
            # Store performance metrics in session state
            if 'performance_metrics' not in st.session_state:
                st.session_state.performance_metrics = []
            
            st.session_state.performance_metrics.append({
                'function': func.__name__,
                'elapsed_ms': elapsed_ms,
                'timestamp': datetime.now(),
                'slow': elapsed_ms > threshold_ms
            })
            
            # Keep only last 100 metrics
            if len(st.session_state.performance_metrics) > 100:
                st.session_state.performance_metrics = st.session_state.performance_metrics[-100:]
            
            return result
        return wrapper
    return decorator


def require_auth(role: Optional[str] = None, redirect_to: str = "login"):
    """
    Authentication decorator to protect routes
    
    Args:
        role: Required user role (optional)
        redirect_to: Where to redirect unauthorized users
    
    Usage:
        @require_auth(role="instructor")
        def instructor_only_view():
            render_dashboard()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if user is logged in
            if 'user_id' not in st.session_state:
                st.warning("⚠️ Please log in to access this page")
                st.stop()
                return None
            
            # Check role if specified
            if role and st.session_state.get('role') != role:
                st.error(f"❌ This page requires {role} access")
                st.stop()
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def memoize_in_session(key_prefix: str = "memoize"):
    """
    Memoize function results in session state (per-session cache)
    
    Args:
        key_prefix: Prefix for session state key
    
    Usage:
        @memoize_in_session(key_prefix="user_data")
        def get_user_data(user_id):
            return expensive_query(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and args
            cache_key = f"{key_prefix}_{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Check if result is in session state
            if cache_key in st.session_state:
                return st.session_state[cache_key]
            
            # Compute and cache result
            result = func(*args, **kwargs)
            st.session_state[cache_key] = result
            return result
        return wrapper
    return decorator


def debounce(wait_seconds: float = 0.5):
    """
    Debounce decorator to prevent rapid repeated calls
    
    Args:
        wait_seconds: Minimum time between calls
    
    Usage:
        @debounce(wait_seconds=1.0)
        def search_handler(query):
            return database.search(query)
    """
    def decorator(func: Callable) -> Callable:
        last_called = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_key = f"debounce_{func.__name__}"
            current_time = time.time()
            
            if func_key in last_called:
                elapsed = current_time - last_called[func_key]
                if elapsed < wait_seconds:
                    return None  # Skip this call
            
            last_called[func_key] = current_time
            return func(*args, **kwargs)
        return wrapper
    return decorator


def retry_on_error(max_attempts: int = 3, delay_seconds: float = 1.0):
    """
    Retry decorator for handling transient failures
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Delay between retries
    
    Usage:
        @retry_on_error(max_attempts=3)
        def unreliable_api_call():
            return api.fetch_data()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"Attempt {attempt + 1} failed, retrying in {delay_seconds}s...")
                        time.sleep(delay_seconds)
                    else:
                        print(f"All {max_attempts} attempts failed")
            
            # All attempts failed, raise the last exception
            if last_exception:
                raise last_exception
        return wrapper
    return decorator


def log_execution(log_args: bool = False, log_result: bool = False):
    """
    Log function execution for debugging
    
    Args:
        log_args: Whether to log function arguments
        log_result: Whether to log return value
    
    Usage:
        @log_execution(log_args=True)
        def process_data(data):
            return transform(data)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_msg = f"[EXEC] {func.__name__}"
            
            if log_args:
                log_msg += f" args={args} kwargs={kwargs}"
            
            print(log_msg)
            
            result = func(*args, **kwargs)
            
            if log_result:
                print(f"[RESULT] {func.__name__} returned: {result}")
            
            return result
        return wrapper
    return decorator


# Convenience decorators combining multiple decorators
def cached_and_monitored(ttl_seconds: int = 300, threshold_ms: float = 1000.0):
    """
    Combine caching and performance monitoring
    
    Usage:
        @cached_and_monitored(ttl_seconds=60)
        def expensive_operation(data):
            return process(data)
    """
    def decorator(func: Callable) -> Callable:
        return cache_with_ttl(ttl_seconds)(
            performance_monitor(threshold_ms)(func)
        )
    return decorator


def safe_cached(ttl_seconds: int = 300, fallback_value: Any = None):
    """
    Combine error handling and caching
    
    Usage:
        @safe_cached(ttl_seconds=60, fallback_value=[])
        def fetch_data():
            return database.query()
    """
    def decorator(func: Callable) -> Callable:
        return handle_errors(fallback_value=fallback_value)(
            cache_with_ttl(ttl_seconds)(func)
        )
    return decorator

