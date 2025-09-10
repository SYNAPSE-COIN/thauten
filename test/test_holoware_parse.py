import sys
# from pathlib import Path
# s = str(Path(__file__).parent / "errloom")
# s = str(Path(".venv/lib/python3.12/site-packages/"))
# sys.path.append(s)

import pytest

from errloom.synapseware import (
    ClassSpan,
    ContextResetSpan,
    EgoSpan,
    SynapseWare,
    ObjSpan,
    SampleSpan,
    TextSpan,
)
from errloom.synapse_parse import (
    _build_class_span,
    _build_context_reset_span,
    _build_ego_or_sampler_span,
    _build_obj_span,
    filter_comments,
    SynapseParser,
    parse_span_tag,
)

# --- Tests for filter_comments ---

def test_filter_comments_empty():
    assert filter_comments("") == ""

def test_filter_comments_no_comments():
    content = "line 1\nline 2"
    assert filter_comments(content) == content

def test_filter_comments_only_comments():
    content = "# comment 1\n# comment 2"
    assert filter_comments(content) == "\n"

def test_filter_comments_mixed():
    content = "line 1\n# comment\nline 2"
    assert filter_comments(content) == "line 1\n\nline 2"

def test_filter_comments_with_whitespace():
    content = "  # comment with leading whitespace"
    assert filter_comments(content) == ""

def test_filter_comments_inline_content_not_filtered():
    content = "line_with_hash = '#value'"
    assert filter_comments(content) == content

# --- Tests for parse_span_tag ---

def test_parse_span_tag_simple():
    base, kargs, kwargs = parse_span_tag("MyClass")
    assert base == "MyClass"
    assert kargs == []
    assert kwargs == {}

def test_parse_span_tag_with_kargs():
    base, kargs, kwargs = parse_span_tag("MyClass arg1 arg2")
    assert base == "MyClass"
    assert kargs == ["arg1", "arg2"]
    assert kwargs == {}

def test_parse_span_tag_with_kwargs():
    base, kargs, kwargs = parse_span_tag("MyClass key1=val1 key2=val2")
    assert base == "MyClass"
    assert kargs == []
    assert kwargs == {"key1": "val1", "key2": "val2"}

def test_parse_span_tag_mixed_args():
    base, kargs, kwargs = parse_span_tag("MyClass arg1 key1=val1 arg2")
    assert base == "MyClass"
    assert kargs == ["arg1", "arg2"]
    assert kwargs == {"key1": "val1"}

def test_parse_span_tag_with_special_attr():
    base, kargs, kwargs = parse_span_tag("MyClass <>something")
    assert base == "MyClass"
    assert kargs == []
    assert kwargs == {"<>": "something"}

def test_parse_span_tag_with_empty_special_attr_raises_error():
    with pytest.raises(ValueError, match="Empty <> attribute"):
        parse_span_tag("MyClass <>")

# --- Tests for Span Builders ---

def test_build_class_span():
    out = []
    _build_class_span(out, "MyClass", ["arg"], {"kw": "val"})
    assert len(out) == 1
    span = out[0]
    assert isinstance(span, ClassSpan)
    assert span.class_name == "MyClass"
    assert span.kargs == ["arg"]
    assert span.kwargs == {"kw": "val"}

def test_build_ego_or_sampler_span_ego_only():
    out = []
    _build_ego_or_sampler_span(out, "o_o", [], {})
    assert len(out) == 1
    span = out[0]
    assert isinstance(span, EgoSpan)
    assert span.ego == "user"

def test_build_ego_or_sampler_span_with_uuid():
    out = []
    _build_ego_or_sampler_span(out, "@_@:123", [], {})
    assert len(out) == 1
    span = out[0]
    assert isinstance(span, EgoSpan)
    assert span.ego == "assistant"
    assert span.uuid == "123"

def test_build_ego_or_sampler_span_as_sampler():
    out = []
    _build_ego_or_sampler_span(out, "o_o:id", ["karg"], {"goal": "test"})
    assert len(out) == 2
    ego_span, sampler_span = out
    assert isinstance(ego_span, EgoSpan)
    assert ego_span.ego == "user"
    assert isinstance(sampler_span, SampleSpan)
    assert sampler_span.uuid == "id"
    assert sampler_span.kargs == ["karg"]
    assert sampler_span.goal == "test"
    assert sampler_span.kwargs == {}

def test_build_context_reset_span():
    out = []
    handler = _build_context_reset_span(train=True)
    handler(out, "+++", [], {})
    assert len(out) == 1
    span = out[0]
    assert isinstance(span, ContextResetSpan)
    assert span.train is True

def test_build_obj_span():
    out = []
    _build_obj_span(out, "var1|var2", ["karg"], {})
    assert len(out) == 1
    span = out[0]
    assert isinstance(span, ObjSpan)
    assert span.var_ids == ["var1", "var2"]
    assert span.kargs == ["karg"]

# --- Tests for SynapseParser ---

@pytest.mark.parametrize(
    "code, expected_details",
    [
        ("", []),
        ("   \n\t ", []),
        (
            "just text",
            [
                {"type": EgoSpan, "attrs": {"ego": "system"}},
                {"type": TextSpan, "attrs": {"text": "just text"}},
            ],
        ),
        ("<|o_o|>", [{"type": EgoSpan, "attrs": {"ego": "user"}}]),
        ("<|@_@|>", [{"type": EgoSpan, "attrs": {"ego": "assistant"}}]),
        (
            "<|o_o|>Hello",
            [
                {"type": EgoSpan, "attrs": {"ego": "user"}},
                {"type": TextSpan, "attrs": {"text": "Hello"}},
            ],
        ),
        (
            "Hello<|o_o|>",
            [
                {"type": EgoSpan, "attrs": {"ego": "system"}},
                {"type": TextSpan, "attrs": {"text": "Hello"}},
                {"type": EgoSpan, "attrs": {"ego": "user"}},
            ],
        ),
        (
            "<|o_o|>Hello<|@_@|>World",
            [
                {"type": EgoSpan, "attrs": {"ego": "user"}},
                {"type": TextSpan, "attrs": {"text": "Hello"}},
                {"type": EgoSpan, "attrs": {"ego": "assistant"}},
                {"type": TextSpan, "attrs": {"text": "World"}},
            ],
        ),
        (
