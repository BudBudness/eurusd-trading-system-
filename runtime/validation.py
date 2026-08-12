from dataclasses import dataclass

@dataclass(frozen=True)
class ValidationReport:
    passed: bool
    in_sample_trades: int
    out_sample_trades: int
    notes: tuple[str, ...]

def walk_forward(pnls: list[float], split: float = 0.7) -> ValidationReport:
    if not 0.5 <= split < 1: raise ValueError("split must be between 0.5 and 1")
    cut = int(len(pnls)*split); ins = pnls[:cut]; out = pnls[cut:]
    passed = bool(ins and out and sum(ins) > 0 and sum(out) > 0)
    notes = ("out-of-sample positive",) if passed else ("validation failed",)
    return ValidationReport(passed,len(ins),len(out),notes)
