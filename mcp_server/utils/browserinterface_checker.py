"""
BrowserInterface Checker - Validates method existence in BrowserInterface class.

Single Responsibility: "Does BrowserInterface have this method?"

This module introspects the BrowserInterface class to:
- Check if a method exists
- Get method signature details
- List all available public methods

Used during runtime validation to verify POM methods call valid
BrowserInterface operations.
"""

import inspect
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable, Type
from pathlib import Path


@dataclass
class MethodParameter:
    """Information about a method parameter."""
    name: str
    annotation: Optional[str] = None
    has_default: bool = False
    default_value: Optional[Any] = None

    def __repr__(self) -> str:
        parts = [self.name]
        if self.annotation:
            parts.append(f": {self.annotation}")
        if self.has_default:
            parts.append(f" = {self.default_value}")
        return "".join(parts)


@dataclass
class MethodSignature:
    """Method signature with parameters and return type."""
    name: str
    parameters: List[MethodParameter] = field(default_factory=list)
    return_annotation: Optional[str] = None
    docstring: Optional[str] = None

    def __repr__(self) -> str:
        params = ", ".join(str(p) for p in self.parameters)
        ret = f" -> {self.return_annotation}" if self.return_annotation else ""
        return f"{self.name}({params}){ret}"


@dataclass
class MethodInfo:
    """Full information about a method."""
    name: str
    signature: MethodSignature
    is_public: bool = True
    category: Optional[str] = None  # Navigation, Interaction, Wait, etc.

    def __repr__(self) -> str:
        prefix = "" if self.is_public else "_"
        cat = f"[{self.category}] " if self.category else ""
        return f"{cat}{prefix}{self.signature}"


class BrowserInterfaceChecker:
    """
    Checks if BrowserInterface has requested methods.

    Uses Python introspection to analyze BrowserInterface class without
    needing a running instance.

    Usage:
        checker = BrowserInterfaceChecker()
        if checker.method_exists("click"):
            sig = checker.get_method_signature("click")
            print(f"click takes: {sig.parameters}")
    """

    # Method categories based on BrowserInterface sections
    METHOD_CATEGORIES = {
        # Navigation
        "navigate_to": "Navigation",
        "refresh_page": "Navigation",
        "go_back": "Navigation",
        "go_forward": "Navigation",
        "get_current_url": "Navigation",
        "get_page_title": "Navigation",

        # Element Finding
        "find_element": "Finding",
        "find_elements": "Finding",
        "is_element_present": "Finding",
        "element_exists": "Finding",  # Deprecated alias

        # Interaction
        "click": "Interaction",
        "click_js": "Interaction",
        "enter_text": "Interaction",
        "type_text": "Interaction",  # Deprecated alias
        "select_dropdown_by_visible_text": "Interaction",
        "select_dropdown_by_value": "Interaction",
        "get_text": "Interaction",
        "get_attribute": "Interaction",
        "is_element_displayed": "Interaction",
        "hover": "Interaction",
        "hover_over_element": "Interaction",  # Deprecated alias
        "is_element_clickable": "Interaction",

        # Wait
        "wait_for_element_visible": "Wait",
        "wait_for_element_invisible": "Wait",
        "wait_for_text_in_element": "Wait",
        "wait_for_url_contains": "Wait",

        # Screenshot
        "take_screenshot": "Screenshot",

        # JavaScript
        "execute_script": "JavaScript",
        "scroll_to_element": "JavaScript",
        "scroll_to_bottom": "JavaScript",
        "scroll_to_top": "JavaScript",

        # Window/Frame
        "switch_to_frame": "Window",
        "switch_to_default_content": "Window",
        "switch_to_window": "Window",
        "get_window_handles": "Window",
        "switch_to_new_window": "Window",
        "close_current_window": "Window",

        # Utility
        "get_page_source": "Utility",
        "quit": "Utility",
    }

    def __init__(self, browserinterface_class: Optional[Type] = None):
        """
        Initialize BrowserInterfaceChecker.

        Args:
            browserinterface_class: Optional BrowserInterface class to inspect.
                                If None, attempts to import from framework.
        """
        self._class = browserinterface_class
        self._methods_cache: Dict[str, MethodInfo] = {}
        self._loaded = False

        if browserinterface_class is not None:
            self._load_methods()

    def _load_methods(self) -> bool:
        """
        Load and cache all methods from BrowserInterface class.

        Returns:
            True if methods loaded successfully, False otherwise.
        """
        if self._loaded:
            return True

        if self._class is None:
            # Try to import BrowserInterface
            try:
                from framework.interfaces.browser_interface import BrowserInterface
                self._class = BrowserInterface
            except ImportError:
                return False

        # Introspect the class
        for name, method in inspect.getmembers(self._class, predicate=inspect.isfunction):
            # Skip __dunder__ methods
            if name.startswith("__") and name.endswith("__"):
                continue

            is_public = not name.startswith("_")
            signature = self._extract_signature(name, method)
            category = self.METHOD_CATEGORIES.get(name)

            self._methods_cache[name] = MethodInfo(
                name=name,
                signature=signature,
                is_public=is_public,
                category=category
            )

        self._loaded = True
        return True

    def _extract_signature(self, name: str, method: Callable) -> MethodSignature:
        """
        Extract method signature using inspect.

        Args:
            name: Method name
            method: Method function object

        Returns:
            MethodSignature with parameters and return type.
        """
        try:
            sig = inspect.signature(method)
        except (ValueError, TypeError):
            return MethodSignature(name=name)

        parameters = []
        for param_name, param in sig.parameters.items():
            # Skip 'self' parameter
            if param_name == "self":
                continue

            annotation = None
            if param.annotation != inspect.Parameter.empty:
                annotation = self._format_annotation(param.annotation)

            has_default = param.default != inspect.Parameter.empty
            default_value = param.default if has_default else None

            parameters.append(MethodParameter(
                name=param_name,
                annotation=annotation,
                has_default=has_default,
                default_value=default_value
            ))

        return_annotation = None
        if sig.return_annotation != inspect.Signature.empty:
            return_annotation = self._format_annotation(sig.return_annotation)

        # Get docstring
        docstring = inspect.getdoc(method)

        return MethodSignature(
            name=name,
            parameters=parameters,
            return_annotation=return_annotation,
            docstring=docstring
        )

    def _format_annotation(self, annotation: Any) -> str:
        """
        Format type annotation as string.

        Args:
            annotation: Type annotation object

        Returns:
            String representation of the annotation.
        """
        if annotation is None:
            return "None"

        # Handle typing module types
        if hasattr(annotation, "__origin__"):
            # Generic types like List[str], Optional[int]
            origin = getattr(annotation, "__origin__", None)
            args = getattr(annotation, "__args__", ())

            origin_name = getattr(origin, "__name__", str(origin))
            if args:
                args_str = ", ".join(self._format_annotation(a) for a in args)
                return f"{origin_name}[{args_str}]"
            return origin_name

        # Simple types
        if hasattr(annotation, "__name__"):
            return annotation.__name__

        return str(annotation)

    def method_exists(self, method_name: str) -> bool:
        """
        Check if a method exists in BrowserInterface.

        Args:
            method_name: Name of the method to check

        Returns:
            True if method exists, False otherwise.
        """
        if not self._load_methods():
            return False

        return method_name in self._methods_cache

    def get_method_signature(self, method_name: str) -> Optional[MethodSignature]:
        """
        Get signature for a method.

        Args:
            method_name: Name of the method

        Returns:
            MethodSignature if method exists, None otherwise.
        """
        if not self._load_methods():
            return None

        info = self._methods_cache.get(method_name)
        if info is None:
            return None

        return info.signature

    def get_method_info(self, method_name: str) -> Optional[MethodInfo]:
        """
        Get full method information.

        Args:
            method_name: Name of the method

        Returns:
            MethodInfo if method exists, None otherwise.
        """
        if not self._load_methods():
            return None

        return self._methods_cache.get(method_name)

    def get_available_methods(self, public_only: bool = True) -> List[MethodInfo]:
        """
        Get list of all available methods.

        Args:
            public_only: If True, only return public methods (default)

        Returns:
            List of MethodInfo for available methods.
        """
        if not self._load_methods():
            return []

        methods = list(self._methods_cache.values())

        if public_only:
            methods = [m for m in methods if m.is_public]

        # Sort by category, then name
        return sorted(methods, key=lambda m: (m.category or "zzz", m.name))

    def get_methods_by_category(self, category: str) -> List[MethodInfo]:
        """
        Get methods in a specific category.

        Args:
            category: Category name (Navigation, Interaction, Wait, etc.)

        Returns:
            List of MethodInfo in that category.
        """
        if not self._load_methods():
            return []

        return [
            m for m in self._methods_cache.values()
            if m.category == category
        ]

    def get_method_names(self, public_only: bool = True) -> List[str]:
        """
        Get list of method names.

        Args:
            public_only: If True, only return public methods (default)

        Returns:
            List of method names.
        """
        return [m.name for m in self.get_available_methods(public_only)]

    def validate_method_call(
        self,
        method_name: str,
        arg_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate if a method call would be valid.

        Args:
            method_name: Name of the method to call
            arg_count: Optional number of arguments being passed

        Returns:
            Dict with 'valid' bool and 'reason' if invalid.
        """
        if not self._load_methods():
            return {
                "valid": False,
                "reason": "BrowserInterface class not available"
            }

        if method_name not in self._methods_cache:
            similar = self._find_similar_methods(method_name)
            reason = f"Method '{method_name}' does not exist"
            if similar:
                reason += f". Did you mean: {', '.join(similar)}?"
            return {
                "valid": False,
                "reason": reason,
                "similar_methods": similar
            }

        info = self._methods_cache[method_name]

        if not info.is_public:
            return {
                "valid": False,
                "reason": f"Method '{method_name}' is private (starts with _)"
            }

        # Check argument count if provided
        if arg_count is not None:
            sig = info.signature
            required_params = sum(
                1 for p in sig.parameters if not p.has_default
            )
            total_params = len(sig.parameters)

            if arg_count < required_params:
                return {
                    "valid": False,
                    "reason": f"Method '{method_name}' requires at least {required_params} arguments, got {arg_count}"
                }

            if arg_count > total_params:
                return {
                    "valid": False,
                    "reason": f"Method '{method_name}' takes at most {total_params} arguments, got {arg_count}"
                }

        return {
            "valid": True,
            "method_info": info
        }

    def _find_similar_methods(self, method_name: str, max_results: int = 3) -> List[str]:
        """
        Find methods with similar names.

        Args:
            method_name: Method name to match
            max_results: Maximum number of suggestions

        Returns:
            List of similar method names.
        """
        if not self._methods_cache:
            return []

        method_lower = method_name.lower()

        # Find methods that start with same prefix or contain the name
        similar = []
        for name in self._methods_cache:
            name_lower = name.lower()
            if (
                name_lower.startswith(method_lower[:3]) or
                method_lower in name_lower or
                name_lower in method_lower
            ):
                similar.append(name)

        return sorted(similar)[:max_results]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_checker(browserinterface_class: Optional[Type] = None) -> BrowserInterfaceChecker:
    """
    Create a BrowserInterfaceChecker instance.

    Args:
        browserinterface_class: Optional BrowserInterface class to inspect.

    Returns:
        Configured BrowserInterfaceChecker.
    """
    return BrowserInterfaceChecker(browserinterface_class)


def method_exists_in_browserinterface(method_name: str) -> bool:
    """
    Quick check if method exists in BrowserInterface.

    Args:
        method_name: Method name to check

    Returns:
        True if method exists, False otherwise.
    """
    checker = BrowserInterfaceChecker()
    return checker.method_exists(method_name)


def get_browserinterface_methods() -> List[str]:
    """
    Get list of all public BrowserInterface method names.

    Returns:
        List of method names.
    """
    checker = BrowserInterfaceChecker()
    return checker.get_method_names()


