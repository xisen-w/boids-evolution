"""The society's shared tool library.

Visibility: a tool is importable AND listed starting the next synchronous
round, whatever its test outcome. There is no promotion step.

Naming rule (audit item 6): tool ids are assigned by the runner as
a<agent>_r<round>, so no build can overwrite another.  The model's proposed
name is kept only as a label.
"""
import ast
import json
import os
import re


class Library:
    def __init__(self, root):
        # This constructor creates a NEW library; it is deliberately not a
        # resume API. Check before touching any existing metadata or source.
        if os.path.exists(root) and os.listdir(root):
            raise FileExistsError("refusing to initialize a nonempty library")
        self.root = root
        self.pkg = os.path.join(root, "tools")
        os.makedirs(self.pkg, exist_ok=True)
        open(os.path.join(self.pkg, "__init__.py"), "w").close()
        self.entries = {}   # tool_id -> metadata
        self.acl = {}       # tool_id -> importable tool ids
        self.index_path = os.path.join(root, "index.json")
        self.save()  # an all-unparseable society is still a valid empty library
        with open(os.path.join(root, "acl.json"), "w") as f:
            json.dump({}, f)

    @staticmethod
    def make_id(agent, rnd):
        return f"a{agent:02d}_r{rnd:02d}"

    def add(self, tool_id, author, rnd, label, description, target, source, implements=(), acl=()):
        if not re.fullmatch(r"a\d{2}_r\d{2}", tool_id):
            raise ValueError("tool id must be assigned by the runner")
        if tool_id in self.entries:
            raise RuntimeError(f"duplicate tool id {tool_id}")
        path = os.path.join(self.pkg, f"{tool_id}.py")
        with open(path, "x") as f:
            f.write(source)
        entry = {
            "id": tool_id, "author": author, "round": rnd, "label": label,
            "description": description, "target": target, "implements": list(implements),
            "static_imports": self.static_imports(source),
            "harness": None, "signature_signal": None,
        }
        self.entries[tool_id] = entry
        # Import ACL: the catalogue the author saw when building this tool.
        # Enforced at run time by the sandbox's audit hook.
        self.acl[tool_id] = sorted(acl)
        with open(os.path.join(self.root, "acl.json"), "w") as f:
            json.dump(self.acl, f, sort_keys=True)
        self.save()
        return entry

    def static_imports(self, source):
        """Tool ids imported via `from tools import X` / `import tools.X`
        (definition (a); (b)/(c) are computed by the analysis code)."""
        found = set()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "tools":
                found.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("tools."):
                found.add(node.module.split(".", 1)[1])
            elif isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.startswith("tools."):
                        found.add(a.name.split(".", 1)[1])
        return sorted(found)

    def listed_for(self, agent, scope):
        """Catalogue an agent sees before building."""
        if scope == "self":
            return [e for e in self.entries.values() if e["author"] == agent]
        return list(self.entries.values())

    def by_author(self, agent):
        return sorted((e for e in self.entries.values() if e["author"] == agent),
                      key=lambda e: e["round"])

    def save(self):
        with open(self.index_path, "w") as f:
            json.dump(self.entries, f, indent=1, sort_keys=True)
