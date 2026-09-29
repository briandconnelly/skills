from __future__ import annotations

import json

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
