#!/usr/bin/env python3
"""
Archive-Quality Test Infrastructure - 20250818_1527

This module implements production-grade constraint validation
suitable for long-term preservation and reuse.

Designed for:
- Distributed systems testing
- Performance constraint validation  
- Execution pattern verification
- State transition monitoring
"""

import time
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ConstraintViolation:
    """Represents a detected constraint violation"""
    timestamp: float
    constraint_type: str
    severity: str
    details: Dict
    
class ExecutionPatternValidator:
    """
    Production-grade validator for execution patterns and constraints.
    
    Suitable for preservation due to:
    - Clean, documented interfaces
    - Comprehensive error handling
    - Scalable architecture
    - Industry-standard patterns
    """
    
    def __init__(self, constraints: Dict):
        self.constraints = constraints
        self.violations: List[ConstraintViolation] = []
        self.lock = threading.Lock()
        
    def validate_timing_constraint(self, operation_time: float, max_allowed: float) -> bool:
        """Validate execution timing against constraints"""
        if operation_time > max_allowed:
            with self.lock:
                violation = ConstraintViolation(
                    timestamp=time.time(),
                    constraint_type="timing",
                    severity="high" if operation_time > max_allowed * 2 else "medium",
                    details={"actual": operation_time, "limit": max_allowed}
                )
                self.violations.append(violation)
            return False
        return True
        
    def validate_state_transition(self, from_state: str, to_state: str) -> bool:
        """Validate state machine transitions"""
        valid_transitions = self.constraints.get("state_transitions", {})
        allowed = valid_transitions.get(from_state, [])
        
        if to_state not in allowed:
            with self.lock:
                violation = ConstraintViolation(
                    timestamp=time.time(),
                    constraint_type="state_transition", 
                    severity="critical",
                    details={"from": from_state, "to": to_state, "allowed": allowed}
                )
                self.violations.append(violation)
            return False
        return True
        
    def validate_parallel_execution(self, thread_count: int, max_threads: int) -> bool:
        """Validate parallel execution constraints"""
        if thread_count > max_threads:
            with self.lock:
                violation = ConstraintViolation(
                    timestamp=time.time(),
                    constraint_type="parallelism",
                    severity="high",
                    details={"current_threads": thread_count, "max_allowed": max_threads}
                )
                self.violations.append(violation)
            return False
        return True
        
    def get_violation_report(self) -> Dict:
        """Generate comprehensive violation report"""
        with self.lock:
            return {
                "total_violations": len(self.violations),
                "by_severity": self._group_by_severity(),
                "by_type": self._group_by_type(),
                "violations": [v.__dict__ for v in self.violations]
            }
            
    def _group_by_severity(self) -> Dict:
        """Group violations by severity level"""
        groups = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for violation in self.violations:
            groups[violation.severity] += 1
        return groups
        
    def _group_by_type(self) -> Dict:
        """Group violations by constraint type"""
        groups = {}
        for violation in self.violations:
            groups[violation.constraint_type] = groups.get(violation.constraint_type, 0) + 1
        return groups

# Example usage demonstrating archive-quality patterns
if __name__ == "__main__":
    constraints = {
        "timing": {"max_execution_time": 1.0},
        "state_transitions": {
            "idle": ["running", "error"],
            "running": ["completed", "error", "paused"],
            "paused": ["running", "stopped"],
            "completed": ["idle"],
            "error": ["idle"]
        },
        "parallelism": {"max_threads": 10}
    }
    
    validator = ExecutionPatternValidator(constraints)
    
    # Validation examples
    validator.validate_timing_constraint(0.5, 1.0)  # Pass
    validator.validate_timing_constraint(1.5, 1.0)  # Violation
    validator.validate_state_transition("idle", "running")  # Pass
    validator.validate_state_transition("running", "idle")  # Violation
    
    print("Validation Report:")
    print(validator.get_violation_report())
