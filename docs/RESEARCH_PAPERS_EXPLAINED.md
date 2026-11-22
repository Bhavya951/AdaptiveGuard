# Research papers explained

## XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models

Paul Röttger, Hannah Rose Kirk, Bertie Vidgen, Giuseppe Attanasio, Federico Bianchi and Dirk Hovy. NAACL 2024. [ACL Anthology primary record and paper](https://aclanthology.org/2024.naacl-long.301/)

A model may refuse a harmless question because its wording resembles an unsafe request. XSTest uses 250 safe prompts across ten categories and 200 unsafe contrasts. The authors evaluate standalone responses and distinguish full compliance, partial refusal and full refusal. Observed refusal patterns depend on the model and prompt category. The crafted prompts and evaluated models bound how broadly the frequencies apply, and each test starts with a single prompt. The suite definition and tables establish the counts used here.

AdaptiveGuard borrows the idea of contrasting benign cases and tracking false alarms. Its label describes whether executing a fictional request would break a rule. We use deterministic classifiers, explicit policies and fixed authored conversations. The project has its own examples and outcome measure.

1. **What is exaggerated safety behavior?** Refusing a benign request when its words or topic resemble a risky request.
2. **Why include unsafe contrasts?** Checking benign compliance alone could reward a system that complies with everything.
3. **What does manual response coding capture?** The degree of compliance or refusal, including responses between the two extremes.
4. **How does this relate to AdaptiveGuard FPR?** Both quantify over-triggering on benign inputs. XSTest observes language-model refusals, while this project counts binary flags on permitted fictional cases.
5. **What would change for conversations?** A scenario must define what earlier turns can affect and preserve the unit of comparison when changing available context.

## Beyond Over-Refusal: Scenario-Based Diagnostics and Post-Hoc Mitigation for Exaggerated Refusals in LLMs

Shuzhou Yuan, Ercong Nie, Yinuo Sun, Chenxuan Zhao, William LaCroix and Michael Färber. 2025 arXiv preprint, version 3. [Primary full text](https://arxiv.org/html/2510.08158v3)

XSB studies single-turn refusal and annotates words suspected of triggering it. MS-XSB extends the analysis to 30 authored scenarios with 20 prompts each, compares context conditions with up to four prior model responses, and uses manual evaluation. The effect of context varies by model. The paper also evaluates post-hoc mitigation of false refusals on four instruction-tuned Llama models. Results depend on the selected models and scenarios. Earlier generated replies can change subsequent inputs.

AdaptiveGuard takes the scenario grouping and context comparison as design precedents. It uses matched fixed histories and family-based resampling, holds the policy and interpreter constant in its matched comparison, and measures decisions under authored fictional rules.

1. **What is a scenario group?** A collection of related prompts in a shared setting, whose outcomes may be statistically dependent.
2. **What does the context comparison vary?** Whether the model sees earlier dialogue responses when answering the current prompt.
3. **Why can generated responses complicate interpretation?** Different earlier replies can supply different evidence to later turns.
4. **What is post-hoc mitigation?** A change applied at inference time after examining where the model tends to go wrong, without retraining.
5. **What does AdaptiveGuard isolate?** The change caused by supplying earlier authored turns to the same interpreter on paired inputs, within the evaluation grammar.
