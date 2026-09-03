# 5\. Auto-DV on RISC-V Cores

**Team:** Forrest Zhang, Daniel Cummings  
**Target:** VCS / Verdi

# Challenge

Automate test-plan creation and functional/code coverage closure while minimizing the amount of generated test infrastructure humans need to inspect manually.

### **Transformation Bet**

With strong contracts and measurable verification outcomes, AI can own most of the DV creation-and-closure loop while humans validate outcomes rather than review every line of generated code.

### **Ambitious 2-Week Outcome**

Take a bounded RISC-V verification target from requirements through an AI-generated test plan, test infrastructure, execution, and meaningful FCOV/CCOV closure.

### **Success Evidence**

Coverage achieved; bugs found; completeness of test plan; number of iterations; amount of generated infrastructure requiring human review or repair.

### **Baseline**

How the same verification target would normally be planned, implemented, and closed by a DV engineer.

### **Constraints**

The experiment should explicitly test **how we can trust generated DV**, not simply whether AI can generate test code.

# How You Work

There is no prescribed AI methodology.

Explore:

* What contracts or checks allow you to review less generated code?  
* What should AI optimize against?  
* Should one agent own the loop or should responsibilities be separated?  
* What approaches did you reject, and why?  
* How did you determine that a verification result itself could be trusted?

### **At the End**

1. **Challenge & Goal**  
2. **Approach & Key Decisions** — Especially your trust model and agent/workflow design.  
3. **Result & Evidence**  
4. **How AI Actually Worked**  
5. **Learnings & Next Time** — What would need to be true for engineers to routinely trust AI-generated DV?

