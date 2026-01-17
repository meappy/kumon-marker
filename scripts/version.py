#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Version manager for kumon-marker project.

Manages versions across all project files including Helm chart.

Usage:
    ./scripts/version.py show                    # Show all versions
    ./scripts/version.py bump patch              # Bug fix: 0.2.1 -> 0.2.2
    ./scripts/version.py bump minor              # New feature: 0.2.1 -> 0.3.0
    ./scripts/version.py bump major              # Breaking change: 0.2.1 -> 1.0.0
    ./scripts/version.py bump patch --tag        # Bump and create git tag
    ./scripts/version.py set 1.0.0               # Set specific version
    ./scripts/version.py sync                    # Sync all files to VERSION file
    ./scripts/version.py release patch           # Bump, commit, tag, and push
    ./scripts/version.py check-tag               # Check if current version has a tag
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


class VersionManager:
    """Manages versions across project files."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.files = {
            "VERSION": self.project_root / "VERSION",
            "package.json": self.project_root / "frontend" / "package.json",
            "pyproject.toml": self.project_root / "backend" / "pyproject.toml",
            "config.py": self.project_root / "backend" / "app" / "core" / "config.py",
            "Chart.yaml": self.project_root / "helm" / "kumon-marker" / "Chart.yaml",
        }

    def _parse_version(self, version: str) -> tuple[int, int, int]:
        """Parse version string into (major, minor, patch)."""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version.strip())
        if not match:
            raise ValueError(f"Invalid version format: {version}")
        return int(match.group(1)), int(match.group(2)), int(match.group(3))

    def _read_version_file(self) -> str:
        """Read version from VERSION file."""
        return self.files["VERSION"].read_text().strip()

    def _read_package_json(self) -> str:
        """Read version from package.json."""
        data = json.loads(self.files["package.json"].read_text())
        return data.get("version", "unknown")

    def _read_pyproject(self) -> str:
        """Read version from pyproject.toml."""
        content = self.files["pyproject.toml"].read_text()
        match = re.search(r'^version = "([^"]*)"', content, re.MULTILINE)
        return match.group(1) if match else "unknown"

    def _read_config_py(self) -> str:
        """Read version from config.py."""
        content = self.files["config.py"].read_text()
        match = re.search(r'app_version: str = "([^"]*)"', content)
        return match.group(1) if match else "unknown"

    def _read_chart_yaml(self) -> tuple[str, str]:
        """Read version and appVersion from Chart.yaml."""
        content = self.files["Chart.yaml"].read_text()
        version_match = re.search(r"^version: (.+)$", content, re.MULTILINE)
        app_version_match = re.search(r'^appVersion: "?([^"\n]+)"?$', content, re.MULTILINE)
        return (
            version_match.group(1).strip() if version_match else "unknown",
            app_version_match.group(1).strip() if app_version_match else "unknown",
        )

    def get_all_versions(self) -> dict[str, str]:
        """Get versions from all files."""
        chart_version, app_version = self._read_chart_yaml()
        return {
            "VERSION": self._read_version_file(),
            "package.json": self._read_package_json(),
            "pyproject.toml": self._read_pyproject(),
            "config.py": self._read_config_py(),
            "Chart.yaml (version)": chart_version,
            "Chart.yaml (appVersion)": app_version,
        }

    def show(self) -> None:
        """Display all versions."""
        versions = self.get_all_versions()

        # Check if all versions match
        unique_versions = set(versions.values())
        all_match = len(unique_versions) == 1

        print("\n📦 Version Status\n")
        print(f"{'File':<25} {'Version':<15} {'Status'}")
        print("-" * 50)

        reference = versions["VERSION"]
        for file, version in versions.items():
            status = "✓" if version == reference else "⚠ OUT OF SYNC"
            print(f"{file:<25} {version:<15} {status}")

        print()
        if all_match:
            print(f"✅ All versions in sync: {reference}")
        else:
            print("⚠️  Versions out of sync! Run './scripts/version.py sync' to fix.")
        print()

    def _update_file(self, path: Path, pattern: str, replacement: str, multiline: bool = False) -> None:
        """Update a file using regex substitution."""
        content = path.read_text()
        flags = re.MULTILINE if multiline else 0
        new_content = re.sub(pattern, replacement, content, flags=flags)
        path.write_text(new_content)

    def _set_version(self, new_version: str) -> None:
        """Set version in all files."""
        # Validate version format
        self._parse_version(new_version)

        # Update VERSION file
        self.files["VERSION"].write_text(f"{new_version}\n")
        print(f"  ✓ VERSION")

        # Update package.json
        self._update_file(
            self.files["package.json"],
            r'"version": "[^"]*"',
            f'"version": "{new_version}"'
        )
        print(f"  ✓ frontend/package.json")

        # Update pyproject.toml
        self._update_file(
            self.files["pyproject.toml"],
            r'^version = "[^"]*"',
            f'version = "{new_version}"',
            multiline=True
        )
        print(f"  ✓ backend/pyproject.toml")

        # Update config.py
        self._update_file(
            self.files["config.py"],
            r'app_version: str = "[^"]*"',
            f'app_version: str = "{new_version}"'
        )
        print(f"  ✓ backend/app/core/config.py")

        # Update Chart.yaml (both version and appVersion)
        self._update_file(
            self.files["Chart.yaml"],
            r"^version: .*",
            f"version: {new_version}",
            multiline=True
        )
        self._update_file(
            self.files["Chart.yaml"],
            r'^appVersion: .*',
            f'appVersion: "{new_version}"',
            multiline=True
        )
        print(f"  ✓ helm/kumon-marker/Chart.yaml")

    def bump(self, bump_type: str, create_tag: bool = False) -> None:
        """Bump version by type (major, minor, patch)."""
        current = self._read_version_file()
        major, minor, patch = self._parse_version(current)

        if bump_type == "major":
            new_version = f"{major + 1}.0.0"
            description = "Breaking change"
        elif bump_type == "minor":
            new_version = f"{major}.{minor + 1}.0"
            description = "New feature"
        elif bump_type == "patch":
            new_version = f"{major}.{minor}.{patch + 1}"
            description = "Bug fix"
        else:
            print(f"Error: Unknown bump type '{bump_type}'")
            sys.exit(1)

        print(f"\n🔄 Bumping version ({description})")
        print(f"   {current} → {new_version}\n")

        self._set_version(new_version)

        if create_tag:
            self.create_tag(new_version)

        self._print_next_steps(new_version)

    def set(self, version: str) -> None:
        """Set a specific version."""
        current = self._read_version_file()

        print(f"\n🔄 Setting version")
        print(f"   {current} → {version}\n")

        self._set_version(version)
        self._print_next_steps(version)

    def sync(self) -> None:
        """Sync all files to match VERSION file."""
        version = self._read_version_file()

        print(f"\n🔄 Syncing all files to VERSION: {version}\n")

        self._set_version(version)
        print(f"\n✅ All files synced to {version}")

    def _run_git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command."""
        result = subprocess.run(
            ["git", *args],
            cwd=self.project_root,
            capture_output=True,
            text=True,
        )
        if check and result.returncode != 0:
            print(f"Git error: {result.stderr}")
            sys.exit(1)
        return result

    def _tag_exists(self, tag: str) -> bool:
        """Check if a git tag already exists."""
        result = self._run_git("tag", "-l", tag, check=False)
        return tag in result.stdout.strip().split("\n")

    def _get_current_tag(self) -> str | None:
        """Get tag for current commit if it exists."""
        result = self._run_git("describe", "--tags", "--exact-match", "HEAD", check=False)
        if result.returncode == 0:
            return result.stdout.strip()
        return None

    def _has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        result = self._run_git("status", "--porcelain", check=False)
        return bool(result.stdout.strip())

    def create_tag(self, version: str, push: bool = False) -> None:
        """Create a git tag for the version."""
        tag = f"v{version}"

        if self._tag_exists(tag):
            print(f"⚠️  Tag {tag} already exists")
            return

        print(f"  🏷️  Creating tag: {tag}")
        self._run_git("tag", "-a", tag, "-m", f"Release {version}")

        if push:
            print(f"  📤 Pushing tag to origin...")
            self._run_git("push", "origin", tag)

        print(f"  ✓ Tag {tag} created")

    def check_tag(self) -> None:
        """Check if current version has a corresponding git tag."""
        version = self._read_version_file()
        tag = f"v{version}"

        print(f"\n🏷️  Tag Status\n")
        print(f"  Current version: {version}")
        print(f"  Expected tag:    {tag}")

        if self._tag_exists(tag):
            print(f"  Status:          ✅ Tag exists")
        else:
            print(f"  Status:          ⚠️  Tag does not exist")
            print(f"\n  Create with: ./scripts/version.py bump patch --tag")

        current_tag = self._get_current_tag()
        if current_tag:
            print(f"  HEAD tag:        {current_tag}")
        print()

    def release(self, bump_type: str, push: bool = True) -> None:
        """Full release: bump version, commit, tag, and optionally push."""
        if self._has_uncommitted_changes():
            print("⚠️  You have uncommitted changes. Please commit or stash them first.")
            sys.exit(1)

        # Bump version
        current = self._read_version_file()
        major, minor, patch = self._parse_version(current)

        if bump_type == "major":
            new_version = f"{major + 1}.0.0"
        elif bump_type == "minor":
            new_version = f"{major}.{minor + 1}.0"
        elif bump_type == "patch":
            new_version = f"{major}.{minor}.{patch + 1}"
        else:
            print(f"Error: Unknown bump type '{bump_type}'")
            sys.exit(1)

        tag = f"v{new_version}"
        if self._tag_exists(tag):
            print(f"⚠️  Tag {tag} already exists. Cannot release.")
            sys.exit(1)

        print(f"\n🚀 Releasing version {new_version}\n")
        print(f"   {current} → {new_version}\n")

        # Update files
        self._set_version(new_version)

        # Commit
        print(f"\n  📝 Committing version bump...")
        self._run_git("add", "-A")
        self._run_git("commit", "-m", f"chore: release v{new_version}")

        # Tag
        self.create_tag(new_version, push=False)

        # Push
        if push:
            print(f"\n  📤 Pushing to origin...")
            self._run_git("push")
            self._run_git("push", "origin", tag)
            print(f"\n✅ Released v{new_version} and pushed to origin")
        else:
            print(f"\n✅ Released v{new_version} (local only)")
            print(f"\n   To push: git push && git push origin {tag}")

    def _print_next_steps(self, version: str) -> None:
        """Print next steps after version change."""
        print(f"""
✅ Version updated to {version}

Next steps:
  1. Review changes:
     git diff

  2. Build Docker image:
     docker build --build-arg VERSION={version} -t ghcr.io/meappy/kumon-marker:{version} -t ghcr.io/meappy/kumon-marker:latest .

  3. Push to registry:
     docker push ghcr.io/meappy/kumon-marker:{version}
     docker push ghcr.io/meappy/kumon-marker:latest

  4. Deploy with Helm:
     helm upgrade kumon-marker ./helm/kumon-marker -f ./helm/kumon-marker/values-local.yaml --set image.tag={version} -n kumon-marker
""")


def main():
    parser = argparse.ArgumentParser(
        description="Version manager for kumon-marker project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s show                 Show all versions across files
  %(prog)s bump patch           Bug fix: 0.2.1 -> 0.2.2
  %(prog)s bump minor           New feature: 0.2.1 -> 0.3.0
  %(prog)s bump major           Breaking change: 0.2.1 -> 1.0.0
  %(prog)s bump patch --tag     Bump and create git tag
  %(prog)s set 1.0.0            Set specific version
  %(prog)s sync                 Sync all files to VERSION file
  %(prog)s check-tag            Check if version has a git tag
  %(prog)s release patch        Full release: bump, commit, tag, push

Version types:
  patch   Bug fixes, small changes (0.0.X)
  minor   New features, backwards compatible (0.X.0)
  major   Breaking changes (X.0.0)
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # show command
    subparsers.add_parser("show", help="Show all versions across files")

    # bump command
    bump_parser = subparsers.add_parser("bump", help="Bump version")
    bump_parser.add_argument(
        "type",
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )
    bump_parser.add_argument(
        "--tag",
        action="store_true",
        help="Create a git tag for this version"
    )

    # set command
    set_parser = subparsers.add_parser("set", help="Set specific version")
    set_parser.add_argument(
        "version",
        help="Version to set (e.g., 1.0.0)"
    )

    # sync command
    subparsers.add_parser("sync", help="Sync all files to VERSION file")

    # check-tag command
    subparsers.add_parser("check-tag", help="Check if current version has a git tag")

    # release command
    release_parser = subparsers.add_parser("release", help="Full release: bump, commit, tag, push")
    release_parser.add_argument(
        "type",
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )
    release_parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push to origin (local release only)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    manager = VersionManager()

    if args.command == "show":
        manager.show()
    elif args.command == "bump":
        manager.bump(args.type, create_tag=args.tag)
    elif args.command == "set":
        manager.set(args.version)
    elif args.command == "sync":
        manager.sync()
    elif args.command == "check-tag":
        manager.check_tag()
    elif args.command == "release":
        manager.release(args.type, push=not args.no_push)


if __name__ == "__main__":
    main()
