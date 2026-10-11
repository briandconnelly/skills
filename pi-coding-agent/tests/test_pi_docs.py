from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from _scripts import load_script

pi_docs = load_script("pi_docs")

FENCE_MARK = "`" * 3  # built, not typed, so this file never contains a literal code fence


def test_symlinked_bin_resolves_to_package_root(pi_install, tmp_path):
    bin_dir, root = pi_install
    installs = pi_docs.find_installs(str(bin_dir), tmp_path)
    assert [(i.root, i.version, i.on_path) for i in installs] == [(root.resolve(), "0.99.1", True)]


def test_nameless_package_json_below_root_is_skipped(pi_install, tmp_path):
    bin_dir, root = pi_install
    assert (root / "dist" / "bundle" / "package.json").is_file()
    assert pi_docs.find_installs(str(bin_dir), tmp_path)[0].root == root.resolve()


def test_project_local_install_is_listed_after_path_install(pi_install, tmp_path):
    bin_dir, _ = pi_install
    nested = tmp_path / "project" / "src" / "deep"
    nested.mkdir(parents=True)
    local = tmp_path / "project" / "node_modules" / "@earendil-works" / "pi-coding-agent"
    local.mkdir(parents=True)
    manifest = {"name": pi_docs.PACKAGE_NAME, "version": "0.98.0"}
    (local / "package.json").write_text(json.dumps(manifest))
    installs = pi_docs.find_installs(str(bin_dir), nested)
    assert [(i.version, i.on_path) for i in installs] == [("0.99.1", True), ("0.98.0", False)]


def test_local_install_that_pi_runs_is_listed_once(pi_install, tmp_path):
    bin_dir, _ = pi_install
    installs = pi_docs.find_installs(str(bin_dir), tmp_path / "lib")
    assert len(installs) == 1
    assert installs[0].on_path


def test_no_install_names_what_was_searched(tmp_path):
    empty_bin = tmp_path / "bin"
    empty_bin.mkdir()
    with pytest.raises(pi_docs.NoInstallError, match=r"`pi` on PATH \(not found\).*node_modules"):
        pi_docs.find_installs(str(empty_bin), tmp_path)


def test_pi_on_path_outside_the_package_is_named(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    shim = bin_dir / "pi"
    shim.write_text("#!/bin/sh\n")
    shim.chmod(0o755)
    with pytest.raises(pi_docs.NoInstallError, match="not inside"):
        pi_docs.find_installs(str(bin_dir), tmp_path)


def test_headings_skip_fenced_code():
    text = f"# Title\n{FENCE_MARK}bash\n## not a heading\n{FENCE_MARK}\n## Real\n"
    assert [(h.level, h.text) for h in pi_docs.headings(text)] == [(1, "Title"), (2, "Real")]


def test_anchors_cover_slugs_duplicates_and_explicit_ids():
    text = (
        "## Choose how to customize Pi\n"
        "## Use your terminal's colors\n"
        "## Setup\n"
        "## Setup\n"
        '<a id="project-trust"></a>\n'
        f"{FENCE_MARK}\n"
        '<a id="in-code"></a>\n'
        f"{FENCE_MARK}\n"
    )
    got = pi_docs.anchors(text)
    expected = {
        "choose-how-to-customize-pi",
        "use-your-terminals-colors",
        "setup",
        "setup-1",
        "project-trust",
    }
    assert expected <= got
    assert "in-code" not in got


def test_heading_with_inline_code_slugs_like_github():
    assert pi_docs.slugify("Project `.pi` directory") == "project-pi-directory"


def test_real_pages_expose_heading_and_explicit_anchors(pi_install, tmp_path):
    bin_dir, _ = pi_install
    install = pi_docs.find_installs(str(bin_dir), tmp_path)[0]
    extensions = pi_docs.anchors((install.docs / "extensions.md").read_text(encoding="utf-8"))
    assert {"error-handling", "choose-an-integration-point"} <= extensions
    configuration = pi_docs.anchors((install.docs / "configuration.md").read_text(encoding="utf-8"))
    assert "project-pi-directory" in configuration


def _install(pi_install, tmp_path):
    bin_dir, _ = pi_install
    return pi_docs.find_installs(str(bin_dir), tmp_path)[0]


def _run(argv, pi_install, tmp_path, capsys, skill_dir=None):
    bin_dir, _ = pi_install
    code = pi_docs.main(
        argv, path_env=str(bin_dir), cwd=tmp_path, skill_dir=skill_dir or tmp_path / "no-skill"
    )
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_index_follows_navigation_with_level_2_and_3_headings(pi_install, tmp_path):
    entries = pi_docs.build_index(_install(pi_install, tmp_path))
    quickstart = next(e for e in entries if e.get("path") == "quickstart.md")
    assert quickstart["depth"] == 1
    assert not quickstart["missing"]
    guides = next(e for e in entries if e.get("title") == "Guides")
    assert {"level": 3, "text": "Choose how to customize Pi"} in quickstart["headings"]
    run_pi = next(e for e in entries if e.get("title") == "Run Pi")
    assert run_pi["group"]
    assert run_pi["depth"] == guides["depth"] + 1
    virtual_models = next(e for e in entries if e.get("path") == "virtual-models.md")
    assert virtual_models["depth"] == run_pi["depth"] + 1


def test_index_flags_navigation_pages_missing_from_disk(pi_install, tmp_path):
    entries = pi_docs.build_index(_install(pi_install, tmp_path))
    assert next(e for e in entries if e.get("path") == "gone.md")["missing"]


def test_index_lists_pages_absent_from_navigation(pi_install, tmp_path):
    entries = pi_docs.build_index(_install(pi_install, tmp_path))
    assert {"cli.md", "extensions.md"} <= {e["path"] for e in entries if e.get("unlisted")}


def test_grep_finds_every_home_of_a_multi_home_answer(pi_install, tmp_path):
    files = {h.file for h in pi_docs.grep(_install(pi_install, tmp_path), ["system prompt"])}
    assert {"docs/cli.md", "docs/configuration.md", "docs/extensions.md"} <= files


def test_grep_reports_the_enclosing_section(pi_install, tmp_path):
    hits = pi_docs.grep(_install(pi_install, tmp_path), ["APPEND_SYSTEM.md"])
    assert any(h.file == "docs/configuration.md" and h.section == "Agent directory" for h in hits)


def test_grep_terms_are_literal(pi_install, tmp_path):
    hits = pi_docs.grep(_install(pi_install, tmp_path), ["pi.registerTool("])
    assert any(h.file == "docs/extensions.md" for h in hits)


def test_grep_searches_example_headers_not_bodies(pi_install, tmp_path):
    install = _install(pi_install, tmp_path)
    header = pi_docs.grep(install, ["Minimal custom tool example"])
    assert [(h.file, h.section) for h in header] == [
        ("examples/extensions/hello.ts", "(header comment)")
    ]
    assert pi_docs.grep(install, ["greeted"]) == []


def test_grep_skips_node_modules_under_examples(pi_install, tmp_path):
    _, root = pi_install
    dep = root / "examples" / "extensions" / "x" / "node_modules" / "dep"
    dep.mkdir(parents=True)
    (dep / "index.ts").write_text("/** zebra-marker */\n")
    assert pi_docs.grep(_install(pi_install, tmp_path), ["zebra-marker"]) == []


def test_changelog_groups_matches_by_version(pi_install, tmp_path):
    entries = pi_docs.changelog(_install(pi_install, tmp_path), "virtual model")
    assert [version for version, _ in entries] == ["[0.99.0] - 2026-09-29"]
    assert any("registerVirtualModel" in line for line in entries[0][1])


def test_cli_changelog_without_changelog_file_names_the_path(pi_install, tmp_path, capsys):
    _, root = pi_install
    (root / "CHANGELOG.md").unlink()
    code, out, err = _run(["changelog", "virtual"], pi_install, tmp_path, capsys)
    assert code == pi_docs.EXIT_NOT_FOUND
    assert out == ""
    assert "CHANGELOG.md" in err


def test_cli_where_json(pi_install, tmp_path, capsys):
    code, out, _ = _run(["where", "--json"], pi_install, tmp_path, capsys)
    data = json.loads(out)
    assert code == pi_docs.EXIT_OK
    assert data["installs"][0]["version"] == "0.99.1"
    assert data["installs"][0]["on_path"] is True
    assert data["verified_against"] is None


@pytest.mark.parametrize(
    ("recorded", "expected"),
    [
        ("0.97.0\n", "verified against 0.97.0; installed Pi is 0.99.1"),
        ("v0.99.1\n", "verified against 0.99.1 (matches installed)"),
        ("0.99.1", "verified against 0.99.1 (matches installed)"),
        ("\n", "verified against: unrecorded"),
    ],
)
def test_cli_where_reports_skill_verification(pi_install, tmp_path, capsys, recorded, expected):
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "verified-against").write_text(recorded)
    code, out, _ = _run(["where"], pi_install, tmp_path, capsys, skill_dir=skill)
    assert code == pi_docs.EXIT_OK
    assert expected in out


def test_cli_index_text_shows_nesting_and_missing(pi_install, tmp_path, capsys):
    code, out, _ = _run(["index"], pi_install, tmp_path, capsys)
    assert code == pi_docs.EXIT_OK
    assert "  Run Pi/" in out
    assert "Removed Page — gone.md (missing)" in out
    assert "Not in docs.json navigation:" in out


def test_cli_grep_no_match_exits_1_and_says_where_it_looked(pi_install, tmp_path, capsys):
    code, out, err = _run(["grep", "no-such-term-xyzzy"], pi_install, tmp_path, capsys)
    assert code == pi_docs.EXIT_NOT_FOUND
    assert out == ""
    assert "no matches" in err
    assert "0.99.1" in err


def test_cli_no_install_exits_2(tmp_path, capsys):
    empty = tmp_path / "bin"
    empty.mkdir()
    code = pi_docs.main(["index"], path_env=str(empty), cwd=tmp_path, skill_dir=tmp_path)
    assert code == pi_docs.EXIT_NO_INSTALL
    assert "No Pi install found" in capsys.readouterr().err


def _live_install():
    """The Pi install `pi` on PATH runs, or None when there is none to check against."""
    if shutil.which("pi") is None:
        pytest.skip("no `pi` on PATH; live check not run")
    if pi_docs.unattributed_pi(os.environ.get("PATH")):
        pytest.skip(
            "`pi` on PATH is not a Pi install (another command or wrapper); live check not run"
        )
    installs = pi_docs.find_installs(os.environ.get("PATH"), Path.cwd())
    return installs


def test_live_install_matches_pi_version():
    installs = _live_install()
    reported = subprocess.run(
        ["pi", "--version"], capture_output=True, text=True, check=True, timeout=30
    ).stdout.strip()
    assert installs[0].on_path
    assert installs[0].version == reported
    assert "quickstart.md" in {e.get("path") for e in pi_docs.build_index(installs[0])}
    assert any(h.file.startswith("examples/") for h in pi_docs.grep(installs[0], ["hello"]))


# Review 2 (Codex, job 6f48c8b1) findings, each pinned before its fix.


def test_where_warns_when_pi_on_path_is_not_an_install(tmp_path, capsys):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    wrapper = bin_dir / "pi"
    wrapper.write_text('#!/bin/sh\nexec somewhere-else "$@"\n')
    wrapper.chmod(0o755)
    local = tmp_path / "node_modules" / "@earendil-works" / "pi-coding-agent"
    local.mkdir(parents=True)
    manifest = {"name": pi_docs.PACKAGE_NAME, "version": "0.98.0"}
    (local / "package.json").write_text(json.dumps(manifest))
    code = pi_docs.main(["where"], path_env=str(bin_dir), cwd=tmp_path, skill_dir=tmp_path)
    captured = capsys.readouterr()
    assert code == pi_docs.EXIT_OK
    assert f"`pi` on PATH ({wrapper}) does not belong to any install found" in captured.err
    code = pi_docs.main(
        ["where", "--json"], path_env=str(bin_dir), cwd=tmp_path, skill_dir=tmp_path
    )
    assert json.loads(capsys.readouterr().out)["unattributed_pi_on_path"] == str(wrapper)


def test_headings_respect_fence_length_and_character():
    longer = "`" * 4
    text = (
        f"{longer}md\n{FENCE_MARK}\n## phantom\n{longer}\n## real\n"
        f"~~~\n{FENCE_MARK}\n## inside tilde\n~~~\n## after tilde\n"
    )
    assert [h.text for h in pi_docs.headings(text)] == ["real", "after tilde"]


def test_grep_section_ignores_headings_inside_long_fences(tmp_path):
    longer = "`" * 4
    page = tmp_path / "page.md"
    page.write_text(f"## Outer\n{longer}\n{FENCE_MARK}\n## fake\n{longer}\nzebra\n")
    pattern = pi_docs.re.compile("zebra")
    assert [h.section for h in pi_docs._grep_markdown(page, "page.md", pattern)] == ["Outer"]


@pytest.mark.parametrize(
    ("heading", "slug"),
    [
        ("Read [configuration](configuration.md)", "read-configuration"),
        ("This is _italic_ and **bold**", "this-is-italic-and-bold"),
        ("session_before_compact", "session_before_compact"),
        ("`before_agent_start` hook", "before_agent_start-hook"),
    ],
)
def test_slug_uses_rendered_heading_text(heading, slug):
    assert pi_docs.slugify(heading) == slug


def test_cli_json_miss_prints_empty_json(pi_install, tmp_path, capsys):
    code, out, err = _run(["grep", "--json", "no-such-term-xyzzy"], pi_install, tmp_path, capsys)
    assert code == pi_docs.EXIT_NOT_FOUND
    assert json.loads(out) == []
    assert "no matches" in err
    code, out, _ = _run(["changelog", "--json", "no-such-term-xyzzy"], pi_install, tmp_path, capsys)
    assert code == pi_docs.EXIT_NOT_FOUND
    assert json.loads(out) == []


def test_example_header_stops_at_first_code_line(pi_install, tmp_path):
    _, root = pi_install
    (root / "examples" / "extensions" / "codey.ts").write_text(
        "/**\n * Codey header\n */\n\n"
        "const DESTRUCTIVE = [\n  'zebra-code',\n];\nexport default 1;\n"
    )
    install = _install(pi_install, tmp_path)
    assert pi_docs.grep(install, ["zebra-code"]) == []
    assert [h.file for h in pi_docs.grep(install, ["Codey header"])] == [
        "examples/extensions/codey.ts"
    ]


# Copilot review (PR #187) findings, each pinned before its fix.


def test_duplicate_slug_skips_an_existing_suffixed_slug():
    text = "## Foo\n## Foo-1\n## Foo\n"
    assert {"foo", "foo-1", "foo-2"} <= pi_docs.anchors(text)


@pytest.mark.parametrize(
    ("shim_dir", "install_dir"),
    [
        # Windows npm: <prefix>\pi.cmd beside <prefix>\node_modules
        (".", "node_modules/@earendil-works/pi-coding-agent"),
        # Unix npm without a symlink: <prefix>/bin/pi, <prefix>/lib/node_modules
        ("bin", "lib/node_modules/@earendil-works/pi-coding-agent"),
    ],
)
def test_npm_shim_layouts_resolve_to_the_global_install(tmp_path, shim_dir, install_dir):
    prefix = tmp_path / "prefix"
    shim_parent = prefix / shim_dir
    shim_parent.mkdir(parents=True, exist_ok=True)
    shim = shim_parent / "pi"
    shim.write_text("#!/bin/sh\n")
    shim.chmod(0o755)
    root = prefix / install_dir
    root.mkdir(parents=True)
    manifest = {"name": pi_docs.PACKAGE_NAME, "version": "0.99.1"}
    (root / "package.json").write_text(json.dumps(manifest))
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    installs = pi_docs.find_installs(str(shim_parent), elsewhere)
    assert [(i.root, i.on_path) for i in installs] == [(root.resolve(), True)]
    assert pi_docs.unattributed_pi(str(shim_parent)) is None


def _managed_layout(tmp_path, version="1.1.0", current=None):
    """pi's managed install: <agent>/bin/pi, <agent>/install/current-version, releases/<v>."""
    agent = tmp_path / "agent"
    (agent / "bin").mkdir(parents=True)
    launcher = agent / "bin" / "pi"
    launcher.write_text("#!/bin/sh\nexit 99\n")  # must never be executed
    launcher.chmod(0o755)
    root = agent / "install" / "releases" / version / pi_docs.LOCAL_INSTALL
    root.mkdir(parents=True)
    (root / "package.json").write_text(
        json.dumps({"name": pi_docs.PACKAGE_NAME, "version": version})
    )
    (agent / "install" / "current-version").write_text(f"{current or version}\n")
    entry = tmp_path / "local-bin"
    entry.mkdir()
    (entry / "pi").symlink_to(launcher)
    return entry, root


def test_managed_install_launcher_resolves_to_current_release(tmp_path):
    entry, root = _managed_layout(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    installs = pi_docs.find_installs(str(entry), elsewhere)
    assert [(i.root, i.version, i.on_path) for i in installs] == [(root.resolve(), "1.1.0", True)]


def _plant_package(root):
    root.mkdir(parents=True)
    (root / "package.json").write_text(
        json.dumps({"name": pi_docs.PACKAGE_NAME, "version": "9.9.9"})
    )


@pytest.mark.parametrize(
    ("bad", "where"),
    [
        (".", "releases"),  # releases/./node_modules/... resolves to releases/node_modules/...
        ("..", ""),  # releases/../node_modules/... resolves to install/node_modules/...
        ("1.1.0/../1.1.0", None),  # resolves to the real release; only the regex stops it
        ("1.1.0 x", "releases/1.1.0 x"),  # a real directory; only the regex stops it
    ],
)
def test_managed_install_rejects_unsafe_current_version(tmp_path, bad, where):
    """Each case would find an install if its guard were removed."""
    entry, _ = _managed_layout(tmp_path, current=bad)
    if where is not None:
        _plant_package(tmp_path / "agent" / "install" / where / pi_docs.LOCAL_INSTALL)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    with pytest.raises(pi_docs.NoInstallError):
        pi_docs.find_installs(str(entry), elsewhere)


def test_managed_install_rejects_empty_current_version(tmp_path):
    entry, _ = _managed_layout(tmp_path)
    (tmp_path / "agent" / "install" / "current-version").write_text("")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    with pytest.raises(pi_docs.NoInstallError):
        pi_docs.find_installs(str(entry), elsewhere)
