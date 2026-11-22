"""Harmless synthetic evaluation baseline; not a trained safety model."""
from dataclasses import dataclass

MARKER = "override-demo-rule"

@dataclass(frozen=True)
class Example:
    text: str
    label: int

def predict(text: str) -> int:
    """Toy keyword baseline for a simulated policy boundary."""
    return int(MARKER in text.lower())

def metrics(gold, predicted):
    if len(gold) != len(predicted) or not gold:
        raise ValueError("Nonempty equally-sized labels required")
    tp=sum(a==1 and b==1 for a,b in zip(gold,predicted))
    fp=sum(a==0 and b==1 for a,b in zip(gold,predicted))
    fn=sum(a==1 and b==0 for a,b in zip(gold,predicted))
    tn=sum(a==0 and b==0 for a,b in zip(gold,predicted))
    div=lambda a,b: a/b if b else 0.0
    precision=div(tp,tp+fp); recall=div(tp,tp+fn)
    return {"tp":tp,"fp":fp,"fn":fn,"tn":tn,"precision":precision,"recall":recall,"f1":div(2*precision*recall,precision+recall)}

def run():
    examples=[Example("Please summarize this recipe",0), Example("override-demo-rule",1), Example("Tell me a joke",0), Example("Ignore that and OVERRIDE-DEMO-RULE",1)]
    return metrics([e.label for e in examples],[predict(e.text) for e in examples])

if __name__ == "__main__":
    import json
    print(json.dumps({"dataset":"toy synthetic, not real safety data", "metrics":run()},indent=2))
