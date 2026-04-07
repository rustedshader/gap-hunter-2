"""
Tools for NIST gap analysis agents to access framework documents and config.
"""

from __future__ import annotations

import yaml
from pydantic import BaseModel, Field

from resource_paths import resource_path

_NIST_CONFIG_PATH = resource_path("nist/nist_config.yaml")
_FRAMEWORK_DOCS_DIR = resource_path("nist/framework-documents")


class ReadFrameworkDocumentTool(BaseModel):
    """Tool to read NIST framework policy/standard documents."""

    document_name: str = Field(
        description="Name of the framework document to read (e.g., 'Information Security Policy', 'Access Control Policy')"
    )


class GetNISTFunctionInfoTool(BaseModel):
    """Tool to get information about a specific NIST CSF function."""

    function_name: str = Field(
        description="NIST function name: Govern, Identify, Protect, Detect, Respond, or Recover"
    )


def read_framework_document(document_name: str) -> str:
    """
    Read a NIST framework document from the framework-documents directory.

    Args:
        document_name: Name of the document (with or without .md extension)

    Returns:
        Content of the document
    """
    # Add .md extension if not present
    if not document_name.endswith(".md"):
        document_name = f"{document_name}.md"

    doc_path = _FRAMEWORK_DOCS_DIR / document_name

    if not doc_path.exists():
        return f"Error: Document '{document_name}' not found in framework-documents directory."

    return doc_path.read_text()


def get_nist_function_info(function_name: str) -> dict:
    """
    Get information about a specific NIST CSF function from the config.

    Args:
        function_name: One of: Govern, Identify, Protect, Detect, Respond, Recover

    Returns:
        Dictionary with function description and subcategories
    """
    with open(_NIST_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    # Find the function in the framework
    for func in config["NIST_Cybersecurity_Framework"]:
        if func["NIST_Function"] == function_name:
            return {
                "function": func["NIST_Function"],
                "description": func["function_description"],
                "categories": func.get("Subheadings", []),
            }

    return {"error": f"Function '{function_name}' not found in NIST config"}


def list_framework_documents() -> list[str]:
    """List all available NIST framework documents."""
    return [f.stem for f in _FRAMEWORK_DOCS_DIR.glob("*.md")]


def build_function_context(function_name: str) -> str:
    """
    Build a detailed, formatted string of all NIST subcategories for a function.

    This is injected directly into the agent prompt so the LLM has full
    subcategory details without needing to make tool calls.

    Args:
        function_name: One of: Govern, Identify, Protect, Detect, Respond, Recover

    Returns:
        Formatted string listing every subcategory with description,
        implementation guidance, key questions, and required policy templates.
    """
    with open(_NIST_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    func_data = None
    for func in config["NIST_Cybersecurity_Framework"]:
        if func["NIST_Function"] == function_name:
            func_data = func
            break

    if func_data is None:
        return f"ERROR: Function '{function_name}' not found in NIST config."

    lines: list[str] = []
    lines.append(f"## NIST CSF Function: {function_name}")
    lines.append(f"{func_data.get('function_description', '').strip()}")
    lines.append("")

    for category in func_data.get("Subheadings", []):
        lines.append(f"### {category.get('Title', '')}")
        lines.append(category.get("category_description", "").strip())
        lines.append("")

        for sub in category.get("Subparts", []):
            sub_id = sub.get("ID", "")
            lines.append(f"#### {sub_id}")
            lines.append(f"**Requirement**: {sub.get('Description', '').strip()}")
            lines.append("")
            guidance = sub.get("Implementation_Guidance", "").strip()
            if guidance:
                lines.append(f"**Implementation Guidance**: {guidance}")
                lines.append("")
            questions = sub.get("Key_Questions", [])
            if questions:
                lines.append("**Key Questions**:")
                for q in questions:
                    lines.append(f"  - {q}")
                lines.append("")
            policies = sub.get("Policies", [])
            if policies:
                lines.append(f"**Required Policy Templates**: {', '.join(policies)}")
            lines.append("")

    return "\n".join(lines)


def get_function_subcategories(function_name: str) -> list[dict]:
    """
    Return structured subcategory data for a NIST function.

    Each dict contains the raw fields needed to build a per-subcategory prompt:
    id, category, description, guidance, questions, policies.

    Args:
        function_name: One of: Govern, Identify, Protect, Detect, Respond, Recover

    Returns:
        List of dicts, one per subcategory.
    """
    with open(_NIST_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    func_data = None
    for func in config["NIST_Cybersecurity_Framework"]:
        if func["NIST_Function"] == function_name:
            func_data = func
            break

    if func_data is None:
        return []

    subcategories: list[dict] = []
    for category in func_data.get("Subheadings", []):
        cat_title = category.get("Title", "")
        for sub in category.get("Subparts", []):
            subcategories.append(
                {
                    "id": sub.get("ID", ""),
                    "category": cat_title,
                    "description": (sub.get("Description") or "").strip(),
                    "guidance": (sub.get("Implementation_Guidance") or "").strip(),
                    "questions": sub.get("Key_Questions", []),
                    "policies": sub.get("Policies", []),
                }
            )

    return subcategories


def get_framework_excerpt(policy_names: list[str], max_chars: int = 600) -> str:
    """
    Load and return truncated excerpts from CIS MS-ISAC framework template docs.

    Multiple policy documents are concatenated until *max_chars* is reached.
    This provides the model with "gold-standard" reference content for comparison.

    Args:
        policy_names: List of document names (e.g. ["Information Security Policy"]).
        max_chars: Maximum combined character length.

    Returns:
        Concatenated excerpt string, or a note if no documents could be loaded.
    """
    docs_dir = _FRAMEWORK_DOCS_DIR
    parts: list[str] = []
    chars_remaining = max_chars

    for name in policy_names:
        if chars_remaining <= 0:
            break

        # Try exact match, then with .md
        candidates = [
            docs_dir / f"{name}.md",
            docs_dir / name,
            docs_dir / f"{name.replace(' ', '-')}.md",
        ]

        content: str | None = None
        for path in candidates:
            if path.exists():
                content = path.read_text()
                break

        if content is None:
            continue

        # Take up to chars_remaining from this document
        excerpt = content[:chars_remaining]
        if len(content) > chars_remaining:
            excerpt += "\n\n[... truncated ...]"
        parts.append(f"### {name}\n{excerpt}")
        chars_remaining -= len(excerpt)

    if not parts:
        return "(No matching CIS MS-ISAC policy template documents found.)"

    return "\n\n---\n\n".join(parts)
