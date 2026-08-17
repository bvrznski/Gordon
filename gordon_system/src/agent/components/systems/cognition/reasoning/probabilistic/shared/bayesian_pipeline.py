# Bayesian Inference Pipeline - Phase 7.7
# =========================================

"""
Canonical Bayesian Inference Pipeline Contract.

Canonical inference flow:
    Prior → Evidence → Likelihood → Posterior → Calibration → Publication

Inference remains reconstructable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class PriorDistribution:
    """
    Prior probability distribution for a variable.
    
    Priors represent existing knowledge or beliefs before observing new evidence.
    """
    
    # Identity
    prior_id: str                         # Unique identifier
    
    # Variable information
    represented_variable: str             # What variable does this describe?
    variable_domain: Tuple[str, ...]      # Possible values (e.g., ("true", "false"))
    
    # Distribution parameters
    distribution_type: str = "categorical"  # e.g., "gaussian", "uniform", "categorical"
    distribution_params: Dict[str, float] = field(default_factory=dict)  # Distribution-specific params
    
    # Confidence in the prior
    confidence: float = 0.5               # How strongly do we trust this prior?
    
    # Provenance
    source: str = "domain_knowledge"      # Where did the prior come from?
    created_at_utc: float = field(default_factory=time.time)
    
    def get_probability(self, value: str) -> float:
        """Get probability of a specific value under this distribution."""
        if self.distribution_type == "uniform":
            return 1.0 / len(self.variable_domain) if value in self.variable_domain else 0.0
        
        # For categorical with explicit params
        if value in self.distribution_params:
            total = sum(self.distribution_params.values())
            return self.distribution_params[value] / total if total > 0 else 0.0
        
        return 0.0
    
    def normalize(self) -> PriorDistribution:
        """Return a normalized version of this distribution."""
        params = dict(self.distribution_params)
        total = sum(params.values()) if params else len(self.variable_domain)
        
        if total > 0:
            for k in params:
                params[k] /= total
        
        return dataclass_replace(
            self,
            distribution_params=params,
        )


@dataclass(frozen=True)
class LikelihoodModel:
    """
    Likelihood function P(Evidence | Hypothesis).
    
    Defines how likely observed evidence is under different hypothesis states.
    """
    
    # Identity
    likelihood_id: str                    # Unique identifier
    
    # Variables involved
    evidence_variable: str                # The observed evidence variable
    hypothesis_variable: str              # The hypothesis variable being evaluated
    
    # Likelihood values
    # Format: {(hypothesis_value, evidence_value): probability}
    likelihood_values: Dict[Tuple[str, str], float] = field(default_factory=dict)
    
    # Normalization
    is_normalized: bool = False           # Whether likelihood sums to 1 per hypothesis
    
    def get_likelihood(self, hypothesis_value: str, evidence_value: str) -> float:
        """Get P(evidence | hypothesis)."""
        key = (hypothesis_value, evidence_value)
        return self.likelihood_values.get(key, 0.0)
    
    @classmethod
    def create_from_data(
        cls,
        evidence_variable: str,
        hypothesis_variable: str,
        data_counts: Dict[Tuple[str, str], int],
    ) -> LikelihoodModel:
        """Create likelihood model from observation counts."""
        total_per_hypothesis: Dict[str, int] = {}
        
        for (h, e), count in data_counts.items():
            if h not in total_per_hypothesis:
                total_per_hypothesis[h] = 0
            total_per_hypothesis[h] += count
        
        likelihood_values = {}
        for (h, e), count in data_counts.items():
            total = total_per_hypothesis.get(h, 1)
            likelihood_values[(h, e)] = count / total if total > 0 else 0.0
        
        return cls(
            likelihood_id=f"likelihood:{uuid.uuid4().hex[:16]}",
            evidence_variable=evidence_variable,
            hypothesis_variable=hypothesis_variable,
            likelihood_values=likelihood_values,
            is_normalized=True,
        )


@dataclass(frozen=True)
class PosteriorDistribution:
    """
    Posterior probability distribution P(Hypothesis | Evidence).
    
    Result of applying Bayes' theorem: P(H|E) ∝ P(E|H) * P(H)
    """
    
    # Identity
    posterior_id: str                     # Unique identifier
    
    # Variable information
    represented_variable: str             # What variable is described?
    evidence_used: Tuple[str, ...] = ()   # Evidence variables used in update
    
    # Distribution parameters
    distribution_type: str = "categorical"
    distribution_params: Dict[str, float] = field(default_factory=dict)
    
    # Uncertainty estimates
    entropy: float = 0.0                  # Shannon entropy of the distribution
    max_probability_value: float = 0.0    # Highest probability value
    
    # Provenance
    prior_id: Optional[str] = None        # Which prior was updated?
    likelihood_id: Optional[str] = None   # Which likelihood was used?
    created_at_utc: float = field(default_factory=time.time)
    
    def get_probability(self, value: str) -> float:
        """Get probability of a specific value."""
        return self.distribution_params.get(value, 0.0)
    
    @property
    def most_likely_value(self) -> Optional[str]:
        """Return the value with highest probability."""
        if not self.distribution_params:
            return None
        return max(self.distribution_params.keys(), key=lambda k: self.distribution_params[k])


@dataclass(frozen=True)
class BayesianInferencePipeline:
    """
    Canonical Bayesian inference pipeline.
    
    Flow: Prior → Evidence → Likelihood → Posterior → Calibration → Publication
    
    Each step remains independently observable and reconstructable.
    """
    
    # Identity
    pipeline_id: str                      # Unique identifier for this pipeline instance
    
    # Pipeline components
    prior_distribution: Optional[PriorDistribution] = None
    likelihood_model: Optional[LikelihoodModel] = None
    posterior_distribution: Optional[PosteriorDistribution] = None
    
    # Evidence used
    evidence_values: Dict[str, str] = field(default_factory=dict)  # variable → observed_value
    
    # Pipeline metadata
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Configuration
    use_marginalization: bool = False     # Marginalize over unobserved variables?
    
    @property
    def is_complete(self) -> bool:
        """Check if pipeline has produced a posterior."""
        return self.posterior_distribution is not None
    
    @classmethod
    def create_from_parts(
        cls,
        prior: PriorDistribution,
        likelihood: LikelihoodModel,
        evidence_values: Dict[str, str],
    ) -> BayesianInferencePipeline:
        """Create and run inference from components."""
        pipeline = cls(
            pipeline_id=f"bayesian_pipeline:{uuid.uuid4().hex[:16]}",
            prior_distribution=prior,
            likelihood_model=likelihood,
            evidence_values=evidence_values,
            created_at_utc=time.time(),
        )
        
        # Run inference (simple Bayesian update)
        posterior = pipeline._run_bayesian_update(prior, likelihood, evidence_values)
        
        return dataclass_replace(
            pipeline,
            posterior_distribution=posterior,
            completed_at_utc=time.time(),
        )
    
    def _run_bayesian_update(
        self,
        prior: PriorDistribution,
        likelihood: LikelihoodModel,
        evidence_values: Dict[str, str],
    ) -> PosteriorDistribution:
        """Perform Bayesian update: P(H|E) ∝ P(E|H) * P(H)."""
        # Get hypothesis variable (the one we're updating)
        hypothesis_var = likelihood.hypothesis_variable
        
        # Calculate unnormalized posteriors
        unnorm_posteriors = {}
        
        for hypothesis_value in prior.variable_domain:
            prior_prob = prior.get_probability(hypothesis_value)
            
            # Get likelihood for all observed evidence values
            likelihood_product = 1.0
            for evidence_var, evidence_val in evidence_values.items():
                if evidence_var == likelihood.evidence_variable:
                    likelihood_product *= likelihood.get_likelihood(
                        hypothesis_value, evidence_val
                    )
            
            unnorm_posteriors[hypothesis_value] = prior_prob * likelihood_product
        
        # Normalize
        total = sum(unnorm_posteriors.values()) or 1.0
        normalized = {k: v / total for k, v in unnorm_posteriors.items()}
        
        # Calculate entropy
        import math
        entropy = -sum(
            p * math.log2(p) for p in normalized.values() if p > 0
        )
        
        return PosteriorDistribution(
            posterior_id=f"posterior:{uuid.uuid4().hex[:16]}",
            represented_variable=hypothesis_var,
            evidence_used=tuple(evidence_values.keys()),
            distribution_type="categorical",
            distribution_params=normalized,
            entropy=entropy,
            max_probability_value=max(normalized.values()) if normalized else 0.0,
            prior_id=prior.prior_id,
            likelihood_id=likelihood.likelihood_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "BayesianInferencePipeline",
    "PriorDistribution",
    "LikelihoodModel", 
    "PosteriorDistribution",
]