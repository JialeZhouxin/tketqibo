"""Strategy Recommendation System for Quantum Circuit Optimization.

This module provides intelligent optimization strategy recommendations
based on circuit characteristics, performance data, and usage patterns.

Key Features:
- Circuit characteristic analysis
- Performance-based method recommendation
- Usage scenario optimization
- Adaptive learning from historical data
- Confidence scoring for recommendations
- Multi-objective optimization guidance

Dependencies:
- Optional: scikit-learn (for advanced recommendation algorithms)
- Optional: numpy (for efficient numerical computations)

Authors: Sim-Fusion Team
Version: 1.0.0
"""

from __future__ import annotations

import math
import statistics
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path
import warnings

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    RandomForestClassifier = None
    StandardScaler = None


class OptimizationMethod(Enum):
    """Available optimization methods."""
    SIM_FUSION = "sim_fusion"
    QIBO_FUSION = "qibo_fusion"
    TKET_ONLY = "tket_only"
    HYBRID_CUSTOM = "hybrid_custom"


class UsageScenario(Enum):
    """Common usage scenarios."""
    SIMULATION = "simulation"
    HARDWARE_EXECUTION = "hardware_execution"
    REPEATED_OPTIMIZATION = "repeated_optimization"
    LARGE_SCALE_PROBLEMS = "large_scale_problems"
    REAL_TIME_APPLICATIONS = "real_time_applications"
    RESEARCH_EXPLORATION = "research_exploration"


class RecommendationConfidence(Enum):
    """Confidence levels for recommendations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass
class CircuitCharacteristics:
    """Characteristics of a quantum circuit for recommendation."""

    n_qubits: int
    n_gates: int
    depth: int
    two_qubit_gate_ratio: float
    rotation_gate_ratio: float
    clifford_gate_ratio: float
    redundancy_level: float  # 0-1 scale
    circuit_density: float   # gates per qubit
    entanglement_density: float

    @classmethod
    def from_analysis(cls, analysis_data: Dict[str, Any]) -> 'CircuitCharacteristics':
        """Create characteristics from circuit analysis data."""
        gate_distribution = analysis_data.get('gate_distribution', {})
        total_gates = analysis_data.get('gates', 1)

        # Count gate types
        two_qubit_gates = sum(count for gate, count in gate_distribution.items()
                             if gate in ['CNOT', 'CZ', 'SWAP', 'CU1', 'CU2'])
        rotation_gates = sum(count for gate, count in gate_distribution.items()
                           if gate.startswith('R'))  # RX, RY, RZ, etc.
        clifford_gates = sum(count for gate, count in gate_distribution.items()
                           if gate in ['H', 'X', 'Y', 'Z', 'S', 'SDG', 'CNOT', 'CZ'])

        return cls(
            n_qubits=analysis_data.get('qubits', 1),
            n_gates=total_gates,
            depth=analysis_data.get('depth', 1),
            two_qubit_gate_ratio=two_qubit_gates / max(total_gates, 1),
            rotation_gate_ratio=rotation_gates / max(total_gates, 1),
            clifford_gate_ratio=clifford_gates / max(total_gates, 1),
            redundancy_level=analysis_data.get('redundancy_level', 0.0),
            circuit_density=total_gates / max(analysis_data.get('qubits', 1), 1),
            entanglement_density=analysis_data.get('entanglement_density', 0.0)
        )


@dataclass
class PerformanceProfile:
    """Performance profile for an optimization method."""

    method: OptimizationMethod
    avg_gate_reduction: float
    avg_depth_reduction: float
    avg_optimization_time: float
    time_consistency: float  # lower is better
    success_rate: float
    scalability_factor: float  # how well it scales with circuit size
    memory_efficiency: float


@dataclass
class Recommendation:
    """Optimization method recommendation."""

    method: OptimizationMethod
    confidence: RecommendationConfidence
    reasoning: str
    expected_benefits: List[str]
    potential_drawbacks: List[str]
    performance_prediction: Dict[str, float]
    scenario_fit_score: float  # 0-1 scale

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'method': self.method.value,
            'confidence': self.confidence.value,
            'reasoning': self.reasoning,
            'expected_benefits': self.expected_benefits,
            'potential_drawbacks': self.potential_drawbacks,
            'performance_prediction': self.performance_prediction,
            'scenario_fit_score': self.scenario_fit_score
        }


class StrategyRecommender:
    """Main strategy recommendation system."""

    def __init__(self,
                 historical_data_path: Optional[str] = None,
                 learning_enabled: bool = True):
        """Initialize the strategy recommender.

        Args:
            historical_data_path: Path to historical performance data
            learning_enabled: Whether to use machine learning for recommendations
        """
        self.learning_enabled = learning_enabled
        self.historical_data_path = historical_data_path

        # Load historical data if available
        self.historical_performance = self._load_historical_data()

        # ML models (if available)
        self.method_classifier = None
        self.performance_scaler = None

        if learning_enabled and SKLEARN_AVAILABLE and self.historical_performance:
            self._train_models()

    def recommend_optimization_method(self,
                                    circuit_characteristics: CircuitCharacteristics,
                                    usage_scenario: UsageScenario = UsageScenario.SIMULATION,
                                    priorities: Optional[Dict[str, float]] = None) -> Recommendation:
        """Generate optimization method recommendation.

        Args:
            circuit_characteristics: Characteristics of the target circuit
            usage_scenario: Intended usage scenario
            priorities: Performance priorities (e.g., {'speed': 0.7, 'quality': 0.3})

        Returns:
            Recommendation for best optimization method
        """
        if priorities is None:
            priorities = self._get_default_priorities(usage_scenario)

        # Generate candidate recommendations
        candidates = self._generate_candidates(circuit_characteristics, usage_scenario)

        # Score and rank candidates
        scored_candidates = []
        for candidate in candidates:
            score = self._calculate_recommendation_score(
                candidate, circuit_characteristics, usage_scenario, priorities
            )
            scored_candidates.append((score, candidate))

        # Select best recommendation
        if not scored_candidates:
            # Fallback: create a default Sim-Fusion recommendation
            from dataclasses import replace
            fallback_candidate = Recommendation(
                method=OptimizationMethod.SIM_FUSION,
                confidence=RecommendationConfidence.LOW,
                reasoning="Default recommendation based on general optimization capabilities",
                expected_benefits=["Comprehensive optimization approach"],
                potential_drawbacks=["May not be optimal for specific circuit characteristics"],
                performance_prediction={
                    'gate_reduction': 0.15,
                    'depth_reduction': 0.08,
                    'optimization_time': 0.1
                },
                scenario_fit_score=0.5
            )
            scored_candidates = [(0.5, fallback_candidate)]

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        best_candidate = scored_candidates[0][1]
        best_score = scored_candidates[0][0]

        # Determine confidence level
        confidence = self._determine_confidence(best_score, len(scored_candidates))

        # Enhance recommendation with detailed reasoning
        recommendation = self._enhance_recommendation(
            best_candidate, circuit_characteristics, usage_scenario, confidence
        )

        return recommendation

    def analyze_circuit_characteristics(self, circuit_analysis: Dict[str, Any]) -> CircuitCharacteristics:
        """Analyze circuit and extract characteristics for recommendation.

        Args:
            circuit_analysis: Circuit analysis data

        Returns:
            Circuit characteristics object
        """
        return CircuitCharacteristics.from_analysis(circuit_analysis)

    def update_historical_data(self,
                              circuit_characteristics: CircuitCharacteristics,
                              method: OptimizationMethod,
                              performance_results: Dict[str, float]):
        """Update historical performance data.

        Args:
            circuit_characteristics: Circuit characteristics
            method: Method used
            performance_results: Performance metrics achieved
        """
        if not self.historical_performance:
            self.historical_performance = []

        # Create performance record
        record = {
            'characteristics': asdict(circuit_characteristics),
            'method': method.value,
            'performance': performance_results,
            'timestamp': str(Path().resolve())  # Simple timestamp
        }

        self.historical_performance.append(record)

        # Retrain models if learning is enabled
        if self.learning_enabled and SKLEARN_AVAILABLE:
            self._train_models()

        # Save data
        if self.historical_data_path:
            self._save_historical_data()

    def _generate_candidates(self,
                           characteristics: CircuitCharacteristics,
                           scenario: UsageScenario) -> List[Recommendation]:
        """Generate candidate recommendations."""
        candidates = []

        # Rule-based candidate generation
        candidates.extend(self._rule_based_candidates(characteristics, scenario))

        # ML-based candidates (if available)
        if self.learning_enabled and self.method_classifier:
            ml_candidates = self._ml_based_candidates(characteristics, scenario)
            candidates.extend(ml_candidates)

        return candidates

    def _rule_based_candidates(self,
                             characteristics: CircuitCharacteristics,
                             scenario: UsageScenario) -> List[Recommendation]:
        """Generate candidates using rule-based approach."""
        candidates = []

        # Sim-Fusion candidates
        sim_fusion_reasons = []
        sim_fusion_benefits = []
        sim_fusion_drawbacks = []

        if characteristics.redundancy_level > 0.3:
            sim_fusion_reasons.append("High redundancy level suitable for TKET preprocessing")
            sim_fusion_benefits.append("Effective redundancy removal")

        if characteristics.two_qubit_gate_ratio > 0.3:
            sim_fusion_reasons.append("High two-qubit gate density")
            sim_fusion_benefits.append("Optimized two-qubit gate handling")

        if characteristics.n_qubits > 10:
            sim_fusion_reasons.append("Large circuit scale")
            sim_fusion_benefits.append("Better scalability for large circuits")
            sim_fusion_drawbacks.append("Longer optimization time")

        if sim_fusion_reasons:
            candidates.append(Recommendation(
                method=OptimizationMethod.SIM_FUSION,
                confidence=RecommendationConfidence.MEDIUM,
                reasoning="; ".join(sim_fusion_reasons),
                expected_benefits=sim_fusion_benefits,
                potential_drawbacks=sim_fusion_drawbacks,
                performance_prediction={
                    'gate_reduction': min(0.4, characteristics.redundancy_level * 0.8),
                    'depth_reduction': min(0.3, characteristics.redundancy_level * 0.6),
                    'optimization_time': 0.1 + characteristics.n_qubits * 0.01
                },
                scenario_fit_score=self._calculate_scenario_fit(
                    OptimizationMethod.SIM_FUSION, characteristics, scenario
                )
            ))

        # Qibo Fusion candidates
        qibo_fusion_reasons = []
        qibo_fusion_benefits = []
        qibo_fusion_drawbacks = []

        if characteristics.rotation_gate_ratio > 0.5:
            qibo_fusion_reasons.append("High rotation gate density")
            qibo_fusion_benefits.append("Excellent rotation gate fusion")

        if scenario == UsageScenario.REAL_TIME_APPLICATIONS:
            qibo_fusion_reasons.append("Fast optimization required")
            qibo_fusion_benefits.append("Very fast optimization")
            qibo_fusion_drawbacks.append("Limited optimization depth")

        if characteristics.circuit_density < 2.0:
            qibo_fusion_reasons.append("Low circuit density")
            qibo_fusion_benefits.append("Efficient for sparse circuits")

        if qibo_fusion_reasons:
            candidates.append(Recommendation(
                method=OptimizationMethod.QIBO_FUSION,
                confidence=RecommendationConfidence.MEDIUM,
                reasoning="; ".join(qibo_fusion_reasons),
                expected_benefits=qibo_fusion_benefits,
                potential_drawbacks=qibo_fusion_drawbacks,
                performance_prediction={
                    'gate_reduction': min(0.2, characteristics.rotation_gate_ratio * 0.3),
                    'depth_reduction': min(0.15, characteristics.rotation_gate_ratio * 0.25),
                    'optimization_time': 0.05 + characteristics.n_gates * 0.001
                },
                scenario_fit_score=self._calculate_scenario_fit(
                    OptimizationMethod.QIBO_FUSION, characteristics, scenario
                )
            ))

        # TKET-only candidates
        tket_reasons = []
        tket_benefits = []
        tket_drawbacks = []

        if characteristics.clifford_gate_ratio > 0.7:
            tket_reasons.append("Highly Clifford circuit")
            tket_benefits.append("Excellent Clifford optimization")

        if scenario == UsageScenario.HARDWARE_EXECUTION:
            tket_reasons.append("Hardware optimization required")
            tket_benefits.append("Hardware-aware optimizations")

        if tket_reasons:
            candidates.append(Recommendation(
                method=OptimizationMethod.TKET_ONLY,
                confidence=RecommendationConfidence.LOW,
                reasoning="; ".join(tket_reasons),
                expected_benefits=tket_benefits,
                potential_drawbacks=tket_drawbacks or ["May miss fusion opportunities"],
                performance_prediction={
                    'gate_reduction': min(0.35, characteristics.clifford_gate_ratio * 0.4),
                    'depth_reduction': min(0.25, characteristics.clifford_gate_ratio * 0.3),
                    'optimization_time': 0.08 + characteristics.n_qubits * 0.008
                },
                scenario_fit_score=self._calculate_scenario_fit(
                    OptimizationMethod.TKET_ONLY, characteristics, scenario
                )
            ))

        return candidates

    def _ml_based_candidates(self,
                           characteristics: CircuitCharacteristics,
                           scenario: UsageScenario) -> List[Recommendation]:
        """Generate candidates using machine learning."""
        if not self.method_classifier or not self.historical_performance:
            return []

        try:
            # Prepare features
            features = np.array([[
                characteristics.n_qubits,
                characteristics.n_gates,
                characteristics.depth,
                characteristics.two_qubit_gate_ratio,
                characteristics.rotation_gate_ratio,
                characteristics.redundancy_level,
                characteristics.circuit_density
            ]])

            # Predict best method
            if self.performance_scaler:
                features = self.performance_scaler.transform(features)

            predicted_method_idx = self.method_classifier.predict(features)[0]
            confidence_scores = self.method_classifier.predict_proba(features)[0]

            method_names = list(self.method_classifier.classes_)
            predicted_method = OptimizationMethod(method_names[predicted_method_idx])
            confidence = confidence_scores[predicted_method_idx]

            # Create ML-based recommendation
            return [Recommendation(
                method=predicted_method,
                confidence=RecommendationConfidence.HIGH if confidence > 0.8 else RecommendationConfidence.MEDIUM,
                reasoning=f"ML prediction based on {len(self.historical_performance)} historical cases",
                expected_benefits=["Data-driven selection", "Historically validated performance"],
                potential_drawbacks=["Limited by training data diversity"],
                performance_prediction={
                    'confidence_score': float(confidence),
                    'training_data_size': len(self.historical_performance)
                },
                scenario_fit_score=confidence
            )]

        except Exception as e:
            warnings.warn(f"ML prediction failed: {e}")
            return []

    def _calculate_recommendation_score(self,
                                      candidate: Recommendation,
                                      characteristics: CircuitCharacteristics,
                                      scenario: UsageScenario,
                                      priorities: Dict[str, float]) -> float:
        """Calculate overall score for a recommendation."""
        # Base score from confidence and scenario fit
        base_score = candidate.scenario_fit_score

        # Adjust based on confidence
        confidence_weights = {
            RecommendationConfidence.HIGH: 1.2,
            RecommendationConfidence.MEDIUM: 1.0,
            RecommendationConfidence.LOW: 0.8,
            RecommendationConfidence.VERY_LOW: 0.6
        }
        base_score *= confidence_weights.get(candidate.confidence, 1.0)

        # Priority-based adjustment
        if 'quality' in priorities and 'gate_reduction' in candidate.performance_prediction:
            quality_factor = candidate.performance_prediction['gate_reduction'] * priorities['quality']
            base_score += quality_factor * 0.3

        if 'speed' in priorities and 'optimization_time' in candidate.performance_prediction:
            # Lower time is better, so invert
            time_factor = (1.0 / max(candidate.performance_prediction['optimization_time'], 0.01)) * priorities['speed']
            base_score += min(time_factor * 0.1, 0.5)  # Cap the influence

        return min(base_score, 1.0)  # Ensure score doesn't exceed 1.0

    def _determine_confidence(self, score: float, num_candidates: int) -> RecommendationConfidence:
        """Determine confidence level based on score and competition."""
        if score > 0.8 and num_candidates > 1:
            return RecommendationConfidence.HIGH
        elif score > 0.6:
            return RecommendationConfidence.MEDIUM
        elif score > 0.4:
            return RecommendationConfidence.LOW
        else:
            return RecommendationConfidence.VERY_LOW

    def _enhance_recommendation(self,
                              candidate: Recommendation,
                              characteristics: CircuitCharacteristics,
                              scenario: UsageScenario,
                              confidence: RecommendationConfidence) -> Recommendation:
        """Enhance recommendation with additional reasoning."""
        # Add scenario-specific reasoning
        scenario_reasoning = self._get_scenario_reasoning(candidate.method, scenario)
        if scenario_reasoning:
            candidate.reasoning += f"; {scenario_reasoning}"

        # Add circuit-specific insights
        circuit_insights = self._get_circuit_insights(candidate.method, characteristics)
        candidate.expected_benefits.extend(circuit_insights)

        # Update confidence
        candidate.confidence = confidence

        return candidate

    def _get_scenario_reasoning(self, method: OptimizationMethod, scenario: UsageScenario) -> str:
        """Get scenario-specific reasoning for method."""
        reasoning_map = {
            (OptimizationMethod.SIM_FUSION, UsageScenario.LARGE_SCALE_PROBLEMS):
                "Best scalability for large quantum circuits",
            (OptimizationMethod.SIM_FUSION, UsageScenario.RESEARCH_EXPLORATION):
                "Comprehensive optimization for exploration",
            (OptimizationMethod.QIBO_FUSION, UsageScenario.REAL_TIME_APPLICATIONS):
                "Fastest optimization suitable for real-time use",
            (OptimizationMethod.QIBO_FUSION, UsageScenario.REPEATED_OPTIMIZATION):
                "Consistent fast performance for repeated tasks",
            (OptimizationMethod.TKET_ONLY, UsageScenario.HARDWARE_EXECUTION):
                "Hardware-aware optimizations for actual quantum devices",
        }
        return reasoning_map.get((method, scenario), "")

    def _get_circuit_insights(self, method: OptimizationMethod, characteristics: CircuitCharacteristics) -> List[str]:
        """Get circuit-specific insights for method."""
        insights = []

        if method == OptimizationMethod.SIM_FUSION:
            if characteristics.redundancy_level > 0.5:
                insights.append("Will effectively remove redundant operations")
            if characteristics.entanglement_density > 0.3:
                insights.append("Optimizes entangled gate sequences")

        elif method == OptimizationMethod.QIBO_FUSION:
            if characteristics.rotation_gate_ratio > 0.6:
                insights.append("Excellent rotation gate fusion capabilities")
            if characteristics.circuit_density < 1.5:
                insights.append("Efficient handling of sparse circuits")

        elif method == OptimizationMethod.TKET_ONLY:
            if characteristics.clifford_gate_ratio > 0.8:
                insights.append("Superior Clifford circuit optimization")

        return insights

    def _calculate_scenario_fit(self,
                               method: OptimizationMethod,
                               characteristics: CircuitCharacteristics,
                               scenario: UsageScenario) -> float:
        """Calculate how well a method fits a scenario."""
        fit_scores = {
            (OptimizationMethod.SIM_FUSION, UsageScenario.SIMULATION): 0.8,
            (OptimizationMethod.SIM_FUSION, UsageScenario.LARGE_SCALE_PROBLEMS): 0.9,
            (OptimizationMethod.SIM_FUSION, UsageScenario.RESEARCH_EXPLORATION): 0.8,
            (OptimizationMethod.QIBO_FUSION, UsageScenario.REAL_TIME_APPLICATIONS): 0.9,
            (OptimizationMethod.QIBO_FUSION, UsageScenario.REPEATED_OPTIMIZATION): 0.8,
            (OptimizationMethod.TKET_ONLY, UsageScenario.HARDWARE_EXECUTION): 0.9,
        }

        base_score = fit_scores.get((method, scenario), 0.5)

        # Adjust based on circuit characteristics
        if method == OptimizationMethod.SIM_FUSION:
            if characteristics.redundancy_level > 0.3:
                base_score += 0.1
            if characteristics.n_qubits > 15:
                base_score += 0.1

        elif method == OptimizationMethod.QIBO_FUSION:
            if characteristics.rotation_gate_ratio > 0.5:
                base_score += 0.1
            if characteristics.n_gates < 100:
                base_score += 0.1

        elif method == OptimizationMethod.TKET_ONLY:
            if characteristics.clifford_gate_ratio > 0.7:
                base_score += 0.1

        return min(base_score, 1.0)

    def _get_default_priorities(self, scenario: UsageScenario) -> Dict[str, float]:
        """Get default priorities for a usage scenario."""
        priority_map = {
            UsageScenario.REAL_TIME_APPLICATIONS: {'speed': 0.8, 'quality': 0.2},
            UsageScenario.HARDWARE_EXECUTION: {'quality': 0.7, 'speed': 0.3},
            UsageScenario.LARGE_SCALE_PROBLEMS: {'quality': 0.6, 'scalability': 0.4},
            UsageScenario.RESEARCH_EXPLORATION: {'quality': 0.5, 'speed': 0.3, 'flexibility': 0.2},
            UsageScenario.REPEATED_OPTIMIZATION: {'speed': 0.6, 'consistency': 0.4},
            UsageScenario.SIMULATION: {'quality': 0.6, 'speed': 0.4},
        }
        return priority_map.get(scenario, {'quality': 0.5, 'speed': 0.5})

    def _load_historical_data(self) -> Optional[List[Dict[str, Any]]]:
        """Load historical performance data."""
        if not self.historical_data_path:
            return None

        try:
            path = Path(self.historical_data_path)
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            warnings.warn(f"Failed to load historical data: {e}")

        return None

    def _save_historical_data(self):
        """Save historical performance data."""
        if not self.historical_data_path or not self.historical_performance:
            return

        try:
            path = Path(self.historical_data_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w') as f:
                json.dump(self.historical_performance, f, indent=2)
        except Exception as e:
            warnings.warn(f"Failed to save historical data: {e}")

    def _train_models(self):
        """Train machine learning models from historical data."""
        if not SKLEARN_AVAILABLE or not self.historical_performance:
            return

        try:
            # Prepare training data
            X = []
            y = []

            for record in self.historical_performance:
                char = record['characteristics']
                features = [
                    char['n_qubits'],
                    char['n_gates'],
                    char['depth'],
                    char['two_qubit_gate_ratio'],
                    char['rotation_gate_ratio'],
                    char['redundancy_level'],
                    char['circuit_density']
                ]
                X.append(features)
                y.append(record['method'])

            if len(set(y)) < 2:  # Need at least 2 different methods
                return

            X = np.array(X)

            # Scale features
            self.performance_scaler = StandardScaler()
            X_scaled = self.performance_scaler.fit_transform(X)

            # Train classifier
            self.method_classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            self.method_classifier.fit(X_scaled, y)

        except Exception as e:
            warnings.warn(f"Failed to train ML models: {e}")

    def get_recommendation_summary(self,
                                 characteristics: CircuitCharacteristics,
                                 scenario: UsageScenario = UsageScenario.SIMULATION) -> Dict[str, Any]:
        """Get comprehensive recommendation summary.

        Args:
            characteristics: Circuit characteristics
            scenario: Usage scenario

        Returns:
            Summary with recommendations and analysis
        """
        # Get primary recommendation
        primary = self.recommend_optimization_method(characteristics, scenario)

        # Get alternative recommendations
        candidates = self._generate_candidates(characteristics, scenario)
        alternatives = [c for c in candidates if c.method != primary.method][:2]

        return {
            'primary_recommendation': primary.to_dict(),
            'alternatives': [alt.to_dict() for alt in alternatives],
            'circuit_analysis': asdict(characteristics),
            'scenario': scenario.value,
            'recommendation_confidence': primary.confidence.value,
            'key_factors': self._identify_key_factors(primary, characteristics),
            'implementation_notes': self._get_implementation_notes(primary.method, characteristics)
        }

    def _identify_key_factors(self, recommendation: Recommendation, characteristics: CircuitCharacteristics) -> List[str]:
        """Identify key factors influencing the recommendation."""
        factors = []

        if characteristics.redundancy_level > 0.3:
            factors.append(f"High redundancy level ({characteristics.redundancy_level:.2f})")

        if characteristics.n_qubits > 10:
            factors.append(f"Large circuit size ({characteristics.n_qubits} qubits)")

        if characteristics.two_qubit_gate_ratio > 0.4:
            factors.append(f"High entanglement ({characteristics.two_qubit_gate_ratio:.2f} two-qubit gates)")

        if characteristics.rotation_gate_ratio > 0.5:
            factors.append(f"Rotation-gate heavy ({characteristics.rotation_gate_ratio:.2f})")

        return factors

    def _get_implementation_notes(self, method: OptimizationMethod, characteristics: CircuitCharacteristics) -> List[str]:
        """Get implementation notes for the recommended method."""
        notes = []

        if method == OptimizationMethod.SIM_FUSION:
            notes.append("Ensure pytket and pytket-qibo are installed")
            if characteristics.n_qubits > 20:
                notes.append("Consider memory usage for very large circuits")
            notes.append("Monitor TKET preprocessing time")

        elif method == OptimizationMethod.QIBO_FUSION:
            notes.append("Fast optimization suitable for repeated use")
            if characteristics.rotation_gate_ratio < 0.3:
                notes.append("Limited benefits for circuits with few rotation gates")

        elif method == OptimizationMethod.TKET_ONLY:
            notes.append("Best for Clifford-dominant circuits")
            notes.append("Consider hardware backend constraints")

        return notes


# Convenience functions for quick usage
def quick_recommend(circuit_analysis: Dict[str, Any],
                   scenario: str = "simulation") -> Dict[str, Any]:
    """Generate quick optimization recommendation.

    Args:
        circuit_analysis: Circuit analysis results
        scenario: Usage scenario name

    Returns:
        Recommendation summary
    """
    recommender = StrategyRecommender()
    characteristics = recommender.analyze_circuit_characteristics(circuit_analysis)

    try:
        usage_scenario = UsageScenario(scenario)
    except ValueError:
        usage_scenario = UsageScenario.SIMULATION

    return recommender.get_recommendation_summary(characteristics, usage_scenario)


def compare_methods_for_circuit(circuit_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Compare all methods for a specific circuit.

    Args:
        circuit_analysis: Circuit analysis results

    Returns:
        Method comparison summary
    """
    recommender = StrategyRecommender()
    characteristics = recommender.analyze_circuit_characteristics(circuit_analysis)

    comparison = {}
    for scenario in UsageScenario:
        recommendation = recommender.recommend_optimization_method(characteristics, scenario)
        comparison[scenario.value] = recommendation.to_dict()

    return {
        'circuit_characteristics': asdict(characteristics),
        'method_comparison': comparison,
        'overall_recommendation': max(
            comparison.items(),
            key=lambda x: x[1]['scenario_fit_score']
        )
    }