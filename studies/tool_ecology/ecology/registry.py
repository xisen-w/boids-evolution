import ast
import hashlib
import json
import random
import re
import shutil
import stat
from pathlib import Path


def safe_files(root: Path):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("symlink or invalid root forbidden")
    resolved = root.resolve()
    result = []
    for p in sorted(root.rglob("*")):
        if p.is_symlink() or not p.resolve().is_relative_to(resolved):
            raise ValueError("symlink or escaping path forbidden")
        mode = p.lstat().st_mode
        if stat.S_ISREG(mode):
            result.append(p)
        elif not stat.S_ISDIR(mode):
            raise ValueError("special file forbidden")
    return result


def file_hashes(root: Path, *, exclude_freeze=False) -> dict:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in safe_files(root)
        if not (exclude_freeze and p.relative_to(root) == Path("freeze.json"))
    }


class Registry:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.artifacts = {p.stem: json.loads(p.read_text()) for p in root.glob("*.json")}

    def publish(
        self, author: str, round_: int, candidate: Path, *, allowed: set, allowed_checks: set | None = None
    ) -> str:
        if not re.fullmatch(r"a\d{2}", author) or round_ < 1:
            raise ValueError("invalid identity")
        identity = f"{author}_r{round_:02d}"
        if identity in self.artifacts or (self.root / identity).exists():
            raise ValueError("publication already exists")
        files = [
            p
            for p in safe_files(candidate)
            if not any(
                part.startswith(".") or part == "__pycache__" for part in p.relative_to(candidate).parts
            )
        ]
        if len(files) > 64 or sum(p.stat().st_size for p in files) > 300_000:
            raise ValueError("publication exceeds file/byte limit")
        if not (candidate / "__init__.py").is_file() or not (candidate / "README.md").is_file():
            raise ValueError("publication needs __init__.py and README.md")
        meta = json.loads((candidate / "publish.json").read_text())
        if not isinstance(meta, dict):
            raise ValueError("publication manifest must be a JSON object")
        if not isinstance(meta.get("description"), str) or not meta["description"].strip():
            raise ValueError("description required")
        if not isinstance(meta.get("capabilities", []), list) or any(
            not isinstance(c, str) for c in meta.get("capabilities", [])
        ):
            raise ValueError("capabilities must be a list of strings")
        checks = meta.get("checks", {})
        if not isinstance(checks, dict) or any(
            not isinstance(k, str)
            or not re.fullmatch(r"[a-z][a-z_]*", k)
            or not isinstance(v, str)
            or not re.fullmatch(r"[A-Za-z_]\w*", v)
            for k, v in checks.items()
        ):
            raise ValueError("checks must map family names to top-level callable names")
        if allowed_checks is not None and set(checks) - allowed_checks:
            raise ValueError("checks must name known service families")
        deps = meta.get("dependencies", [])
        if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
            raise ValueError("dependencies must be IDs")
        if not set(deps) <= allowed:
            raise ValueError("unreceived dependency")
        if any(d not in self.artifacts or self.artifacts[d]["round"] >= round_ for d in deps):
            raise ValueError("dependency must precede round")
        complexity = 0
        for p in files:
            if p.suffix == ".py":
                tree = ast.parse(p.read_text())
                complexity += sum(1 for _ in ast.walk(tree))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.level:
                        # One component for the publication plus its nested directories.
                        # Both __init__.py and ordinary modules use that containing package.
                        relative = p.relative_to(candidate)
                        package_depth = len(relative.parts)
                        if node.level > package_depth:
                            raise ValueError("relative import escapes publication; use declared published.ID")
                    names = (
                        [node.module or ""]
                        if isinstance(node, ast.ImportFrom)
                        else [x.name for x in node.names]
                        if isinstance(node, ast.Import)
                        else []
                    )
                    for name in names:
                        if name == "published" and isinstance(node, ast.ImportFrom):
                            for alias in node.names:
                                if alias.name not in deps and alias.name != identity:
                                    raise ValueError("undeclared published import")
                        if name.startswith("published."):
                            dep = name.split(".")[1]
                            if dep != identity and dep not in deps:
                                raise ValueError("undeclared published import")
        dest = self.root / identity
        dest.mkdir()
        for p in files:
            target = dest / p.relative_to(candidate)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, target)
        artifact = dict(
            id=identity,
            author=author,
            round=round_,
            description=meta["description"],
            capabilities=meta.get("capabilities", []),
            dependencies=sorted(set(deps)),
            checks=checks,
            ast_nodes=complexity,
            status="syntax_checked_only",
            hashes=file_hashes(dest),
        )
        (self.root / f"{identity}.json").write_text(json.dumps(artifact, indent=2))
        self.artifacts[identity] = artifact
        return identity

    def closure(self, roots: set) -> set:
        result = set()

        def visit(identity):
            if identity not in result:
                result.add(identity)
                for dep in self.artifacts[identity]["dependencies"]:
                    visit(dep)

        for root in sorted(roots):
            visit(root)
        return result

    def materialize(self, roots: set, dest: Path) -> Path:
        if dest.exists():
            raise ValueError("view destination exists")
        package = dest / "published"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
        cards = []
        for identity in sorted(self.closure(roots)):
            meta = self.artifacts[identity]
            if file_hashes(self.root / identity) != meta["hashes"]:
                raise ValueError("registry hash mismatch")
            shutil.copytree(self.root / identity, package / identity)
            cards.append(meta)
        (dest / "catalogue.json").write_text(json.dumps(cards, indent=2))
        return dest

    def freeze(self, dest: Path) -> Path:
        self.materialize(set(self.artifacts), dest)
        (dest / "freeze.json").write_text(json.dumps(dict(hashes=file_hashes(dest)), indent=2))
        return dest

    @staticmethod
    def verify_freeze(dest: Path):
        if file_hashes(dest, exclude_freeze=True) != json.loads((dest / "freeze.json").read_text())["hashes"]:
            raise ValueError("frozen library hash mismatch")


class LocalSociety:
    def __init__(self, registry: Registry, n: int, condition: str, seed: int):
        if n < 3 or condition not in ("local-neutral", "local-boids", "independent"):
            raise ValueError("invalid society configuration")
        self.registry, self.condition = registry, condition
        self.agents = [f"a{i:02d}" for i in range(n)]
        self.ring = self.agents.copy()
        random.Random(seed).shuffle(self.ring)
        self.receipts = []

    def neighbors(self, author):
        i = self.ring.index(author)
        return [self.ring[(i - 1) % len(self.ring)], self.ring[(i + 1) % len(self.ring)]]

    def view(self, author, round_):
        own = {i for i, a in self.registry.artifacts.items() if a["author"] == author and a["round"] < round_}
        received = {
            r["member"] for r in self.receipts if r["recipient"] == author and r["available_round"] <= round_
        }
        return own | received

    def deliver(self, round_, publications):
        if self.condition == "independent":
            return
        for identity in publications:
            meta = self.registry.artifacts[identity]
            if meta["round"] != round_:
                raise ValueError("wrong publication round")
            for recipient in self.neighbors(meta["author"]):
                for member in sorted(self.registry.closure({identity})):
                    self.receipts.append(
                        dict(
                            recipient=recipient,
                            sender=meta["author"],
                            root=identity,
                            member=member,
                            available_round=round_ + 1,
                        )
                    )
