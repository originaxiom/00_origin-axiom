"""
Floor derivation from fundamental constraints.

Derives existence floor ε from:
- Holographic bounds
- Information-theoretic limits
- Topological constraints
"""

from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
from phase0_fc import PreGeometricManifold, FrustrationField


class FloorDerivation:
    """
    Derive existence floor from fundamental constraints.

    Implements three derivation methods:
    1. Holographic: ε ~ 1/sqrt(N) from surface/volume ratio
    2. Information: ε from Shannon entropy bounds
    3. Topological: ε from graph Laplacian spectrum

    Parameters
    ----------
    manifold : PreGeometricManifold
        Manifold providing topology
    """

    def __init__(self, manifold: PreGeometricManifold):
        self.manifold = manifold

    def holographic_floor(self) -> Tuple[float, Dict]:
        """
        Derive floor from holographic bound.

        Holographic principle analog for discrete graph:
        - Information in volume N bounded by "surface area"
        - Surface area ~ N^(d-1)/d for d-dimensional lattice
        - For cubic 3D: A ~ N^(2/3)

        Derivation:
            Total information: I ~ N·log(1/ε)
            Holographic bound: I ≲ A ~ N^(2/3)
            Therefore: N·log(1/ε) ≲ N^(2/3)
            Solving: ε_holo ~ exp(-N^(-1/3))

        For small N, approximate: ε_holo ~ C/sqrt(N)

        Returns
        -------
        epsilon_holo : float
            Holographic floor estimate
        diagnostics : dict
            Contains N, effective_surface, volume, derivation_method
        """
        N = self.manifold.N

        # Estimate effective "surface" as sqrt(N) for d=3 cube
        # (actual surface ~ N^(2/3), but use simpler scaling)
        effective_surface = np.sqrt(N)
        volume = N

        # Holographic ratio
        holo_ratio = effective_surface / volume  # ~ N^(-1/2)

        # Floor estimate: ε ~ holographic_ratio
        # With coefficient C ~ 1 for order of magnitude
        epsilon_holo = holo_ratio

        diagnostics = {
            'N': N,
            'effective_surface': effective_surface,
            'volume': volume,
            'holo_ratio': holo_ratio,
            'derivation': 'holographic',
            'scaling': 'N^(-1/2)',
            'note': 'Order-of-magnitude estimate from surface/volume ratio'
        }

        return epsilon_holo, diagnostics

    def information_floor(
        self,
        field: Optional[FrustrationField] = None,
        target_entropy_ratio: float = 0.5
    ) -> Tuple[float, Dict]:
        """
        Derive floor from information entropy bounds.

        Shannon entropy of amplitude distribution:
            S = -Σ p_i log(p_i)
            where p_i = |ψ_i|² / Σ|ψ_j|²

        Require: S > S_min to maintain "alive" state.

        If field provided: compute actual entropy.
        If not: use entropic lower bound from system size.

        Parameters
        ----------
        field : FrustrationField, optional
            Field to compute entropy from (if None, use theoretical bound)
        target_entropy_ratio : float
            Target S/S_max ratio (default 0.5)

        Returns
        -------
        epsilon_info : float
            Information-theoretic floor estimate
        diagnostics : dict
            Contains entropy calculations
        """
        N = self.manifold.N

        if field is not None:
            # Compute actual entropy from field state
            amplitudes = np.abs(field.psi)
            amp_sq = amplitudes ** 2
            total_amp_sq = np.sum(amp_sq)

            if total_amp_sq < 1e-12:
                # Degenerate case: no amplitude
                epsilon_info = 1.0 / np.sqrt(N)  # Default to holographic scaling
                diagnostics = {
                    'N': N,
                    'entropy': 0.0,
                    'max_entropy': np.log(N),
                    'derivation': 'information (degenerate)',
                    'note': 'Field has zero amplitude, using default scaling'
                }
                return epsilon_info, diagnostics

            # Probability distribution
            p = amp_sq / total_amp_sq

            # Shannon entropy (avoid log(0))
            p_safe = p[p > 1e-12]
            entropy = -np.sum(p_safe * np.log(p_safe))

            # Maximum entropy (uniform distribution)
            max_entropy = np.log(N)

            # Derive floor from entropy requirement
            # Lower entropy → need larger minimum amplitude
            # Heuristic: ε ~ (1/sqrt(N)) * (2 - S/S_max)
            # When S ≈ S_max (high entropy): ε ≈ 1/sqrt(N) (holographic scaling)
            # When S ≈ 0 (low entropy): ε ≈ 2/sqrt(N) (larger floor needed)
            entropy_ratio = entropy / max_entropy
            epsilon_info = (1.0 / np.sqrt(N)) * (2.0 - entropy_ratio)

            diagnostics = {
                'N': N,
                'entropy': entropy,
                'max_entropy': max_entropy,
                'entropy_ratio': entropy / max_entropy,
                'mean_amplitude': np.mean(amplitudes),
                'derivation': 'information (from field)',
                'note': 'Derived from actual field entropy'
            }

        else:
            # Theoretical bound without field
            # Require S > S_min ~ target_entropy_ratio · log(N)
            S_min = target_entropy_ratio * np.log(N)

            # Heuristic: if all amplitudes at floor ε, entropy ~ log(N)
            # So ε ~ (S_min / N)^(1/2) for order of magnitude
            epsilon_info = np.sqrt(S_min / N)

            diagnostics = {
                'N': N,
                'S_min': S_min,
                'target_ratio': target_entropy_ratio,
                'derivation': 'information (theoretical)',
                'scaling': '(log(N)/N)^(1/2)',
                'note': 'Theoretical bound without field state'
            }

        return epsilon_info, diagnostics

    def topological_floor(self) -> Tuple[float, Dict]:
        """
        Derive floor from graph topology.

        Uses graph Laplacian spectrum to estimate minimum flow.

        Graph Laplacian: L = D - A
        where D is degree matrix, A is adjacency matrix.

        For connected graph: λ_0 = 0, λ_1 > 0 (algebraic connectivity).

        Heuristic: minimum amplitude to sustain flow:
            ε_topo ~ sqrt(λ_1 / N)

        Returns
        -------
        epsilon_topo : float
            Topological floor estimate
        diagnostics : dict
            Contains Laplacian eigenvalues and connectivity info
        """
        N = self.manifold.N
        adjacency = self.manifold.adjacency

        # Build Laplacian matrix L = D - A
        # Degree matrix
        degrees = np.array([len(adjacency[i]) for i in range(N)])
        D = np.diag(degrees)

        # Adjacency matrix (sparse)
        row_ind = []
        col_ind = []
        for i in range(N):
            for j in adjacency[i]:
                row_ind.append(i)
                col_ind.append(j)

        A_sparse = csr_matrix(
            (np.ones(len(row_ind)), (row_ind, col_ind)),
            shape=(N, N)
        )

        # Laplacian L = D - A
        L_sparse = csr_matrix(D) - A_sparse

        # Compute smallest non-zero eigenvalue (algebraic connectivity)
        # Use sparse eigensolver for efficiency
        try:
            # Get 2 smallest eigenvalues (λ_0=0, λ_1>0)
            eigenvalues, eigenvectors = eigsh(L_sparse, k=min(2, N-1), which='SM')
            eigenvalues = np.sort(eigenvalues)

            lambda_0 = eigenvalues[0]  # Should be ~0
            lambda_1 = eigenvalues[1] if len(eigenvalues) > 1 else eigenvalues[0]

        except Exception as e:
            # Fallback to dense eigendecomposition for small systems
            L_dense = L_sparse.toarray()
            eigenvalues_all = np.linalg.eigvalsh(L_dense)
            eigenvalues_all = np.sort(eigenvalues_all)

            lambda_0 = eigenvalues_all[0]
            lambda_1 = eigenvalues_all[1] if len(eigenvalues_all) > 1 else eigenvalues_all[0]

        # Floor estimate: ε ~ sqrt(λ_1 / N)
        epsilon_topo = np.sqrt(lambda_1 / N)

        diagnostics = {
            'N': N,
            'lambda_0': lambda_0,
            'lambda_1': lambda_1,
            'algebraic_connectivity': lambda_1,
            'mean_degree': np.mean(degrees),
            'derivation': 'topological',
            'scaling': '(λ_1/N)^(1/2)',
            'note': 'Derived from graph Laplacian spectrum'
        }

        return epsilon_topo, diagnostics

    def compare_floors(
        self,
        epsilon_imposed: float,
        field: Optional[FrustrationField] = None
    ) -> pd.DataFrame:
        """
        Compare derived floors with imposed value.

        Parameters
        ----------
        epsilon_imposed : float
            Floor value imposed in dynamics (e.g., 0.01)
        field : FrustrationField, optional
            Field for information entropy calculation

        Returns
        -------
        comparison : DataFrame
            Table with all floor values, ratios, and diagnostics
        """
        # Derive all floors
        eps_holo, diag_holo = self.holographic_floor()
        eps_info, diag_info = self.information_floor(field=field)
        eps_topo, diag_topo = self.topological_floor()

        # Build comparison table
        data = []

        data.append({
            'Method': 'Holographic',
            'Floor (ε)': eps_holo,
            'Ratio to Imposed': eps_holo / epsilon_imposed,
            'Scaling': diag_holo['scaling'],
            'Note': diag_holo['note']
        })

        data.append({
            'Method': 'Information',
            'Floor (ε)': eps_info,
            'Ratio to Imposed': eps_info / epsilon_imposed,
            'Scaling': diag_info.get('scaling', 'field-dependent'),
            'Note': diag_info['note']
        })

        data.append({
            'Method': 'Topological',
            'Floor (ε)': eps_topo,
            'Ratio to Imposed': eps_topo / epsilon_imposed,
            'Scaling': diag_topo['scaling'],
            'Note': diag_topo['note']
        })

        data.append({
            'Method': 'Imposed (Phase 1)',
            'Floor (ε)': epsilon_imposed,
            'Ratio to Imposed': 1.0,
            'Scaling': 'N/A',
            'Note': 'Hard floor used in frustrated dynamics'
        })

        comparison = pd.DataFrame(data)

        return comparison

    def scaling_analysis(
        self,
        N_values: list,
        topology: str = 'cubic_3d'
    ) -> pd.DataFrame:
        """
        Analyze how derived floors scale with system size.

        Parameters
        ----------
        N_values : list
            List of system sizes to test
        topology : str
            Manifold topology

        Returns
        -------
        scaling_data : DataFrame
            Floor values for each N
        """
        results = []

        for N in N_values:
            # Create temporary manifold
            manifold_temp = PreGeometricManifold(N_nodes=N, topology=topology)
            deriv_temp = FloorDerivation(manifold_temp)

            # Derive floors
            eps_holo, _ = deriv_temp.holographic_floor()
            eps_info, _ = deriv_temp.information_floor()  # Theoretical, no field
            eps_topo, _ = deriv_temp.topological_floor()

            results.append({
                'N': N,
                'ε_holographic': eps_holo,
                'ε_information': eps_info,
                'ε_topological': eps_topo
            })

        scaling_data = pd.DataFrame(results)

        return scaling_data
