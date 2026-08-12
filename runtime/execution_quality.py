from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionQuality:
    fills: int
    rejects: int
    partials: int
    avg_slippage: float
    avg_spread: float
    avg_latency_ms: float

def summarize(records) -> ExecutionQuality:
    fills = [r for r in records if getattr(r,'status',None) == 'FILLED']
    partials = [r for r in records if getattr(r,'status',None) == 'PARTIAL']
    rejects = [r for r in records if getattr(r,'status',None) == 'REJECTED']
    n = len(fills) + len(partials)
    return ExecutionQuality(n,len(rejects),len(partials),
        sum((r.slippage or 0) for r in fills)/len(fills) if fills else 0,
        sum(r.spread for r in fills)/len(fills) if fills else 0,
        sum(r.latency_ms for r in fills)/len(fills) if fills else 0)
