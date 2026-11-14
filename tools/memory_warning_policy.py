"""Apply the pack's early client heap advisory policy to exact author bytes."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


CONFIG = "config/memorysettings.json"
MOD = "mods/memorysettings-1.20.1-5.9.jar"
MINIMUM = re.compile(rb'("minimumClient"\s*:\s*\{[^{}]*?"minimumClient"\s*:\s*)(-?\d+)(?=\s*[,}])')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def set_minimum(raw, value):
    parsed = json.loads(raw)
    old = parsed["minimumClient"]["minimumClient"]
    matches = list(MINIMUM.finditer(raw))
    if type(old) is not int or len(matches) != 1 or int(matches[0][2]) != old:
        raise ValueError("Unexpected Memory Settings client recommendation shape")
    start, end = matches[0].span(2)
    return raw[:start] + str(value).encode("ascii") + raw[end:]


@dataclass(frozen=True)
class Policy:
    path: Path
    author: dict
    effective: dict
    original_minimum: int

    @staticmethod
    def matches(raw, record):
        return len(raw) == record["sizeBytes"] and sha(raw) == record["sha256"]

    def is_effective(self, raw):
        if not self.matches(raw, self.effective):
            return False
        author = set_minimum(raw, self.original_minimum)
        return self.matches(author, self.author) and set_minimum(author, 0) == raw

    def accepts(self, raw):
        return self.matches(raw, self.author) or self.is_effective(raw)

    def verify(self):
        if not self.is_effective(self.path.read_bytes()):
            raise ValueError("The authored Memory Settings client advisory policy is missing")

    def normalize(self):
        raw = self.path.read_bytes()
        if self.matches(raw, self.author):
            return
        if not self.is_effective(raw):
            raise ValueError("Unknown Memory Settings configuration; review the author update")
        self.write(set_minimum(raw, self.original_minimum))

    def apply(self):
        raw = self.path.read_bytes()
        if self.is_effective(raw):
            return
        if not self.matches(raw, self.author):
            raise ValueError("Unknown Memory Settings configuration; review the author update")
        output = set_minimum(raw, 0)
        if not self.is_effective(output):
            raise ValueError("Memory Settings policy output differs from the reviewed config")
        self.write(output)

    def write(self, raw):
        file = tempfile.NamedTemporaryFile(dir=self.path.parent, delete=False)
        try:
            with file:
                file.write(raw)
            os.replace(file.name, self.path)
        finally:
            Path(file.name).unlink(missing_ok=True)


def load(pack, author_records, resource):
    config = resource(pack, "tools/client-policy/policy.json")
    if not config.is_file():
        return None
    pin = json.loads(config.read_bytes()).get("earlyClientWarning")
    if pin is None:
        return None
    if set(pin) != {"originalMinimum", "effectiveSizeBytes", "effectiveSha256", "nativeJarSha256"}:
        raise ValueError("Unknown Memory Settings early advisory policy")
    if (type(pin["originalMinimum"]) is not int or pin["originalMinimum"] <= 0
            or type(pin["effectiveSizeBytes"]) is not int or pin["effectiveSizeBytes"] <= 0
            or not re.fullmatch(r"[0-9a-f]{64}", pin["effectiveSha256"])):
        raise ValueError("Invalid Memory Settings early advisory policy pin")
    records = {row["path"]: row for row in author_records}
    if CONFIG not in records or MOD not in records or records[MOD]["sha256"] != pin["nativeJarSha256"]:
        raise ValueError("Author changed Memory Settings inputs; verify the native advisory again")
    effective = {**records[CONFIG], "sizeBytes": pin["effectiveSizeBytes"], "sha256": pin["effectiveSha256"]}
    return Policy(resource(pack, CONFIG), records[CONFIG], effective, pin["originalMinimum"])
