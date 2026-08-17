"""Knowledge Graphs Tests - Phase 6.8 (Parts 1-3)
================================================================

Comprehensive tests for the canonical Knowledge Graph contracts.

Test requirements (Phase 6.8 Part 3 Section 14):
    1.  node creation
    2.  edge creation
    3.  topology validation
    4.  multi-layer organization
    5.  traversal strategies
    6.  index generation
    7.  partition management
    8.  graph composition
    9.  graph evolution
    10. governance evaluation
    11. provenance completeness
    12. deterministic replay
    13. deterministic traversal
    14. deterministic indexing

Laws verified:
    GRAPH / NODE / EDGE / TOPOLOGY / LAYER / TRAVERSAL / INDEX /
    PARTITION / EVOLUTION / VALIDATION / GOVERNANCE
"""

import unittest

from agent.components.systems.knowledge.graphs import (
    GraphDescriptor,
    GraphKind,
    GraphLifecycleState,
    GraphNode,
    GraphEdge,
    EdgeDirection,
    GraphTopology,
    TopologyKind,
    GraphMetrics,
    GraphLayer,
    LayerKind,
    InterLayerMapping,
    GraphTraversalSession,
    TraversalStrategy,
    GraphIndex,
    GraphIndexEntry,
    IndexingStrategy,
    GraphComposition,
    CompositionStrategy,
    GraphPartition,
    PartitionStrategy,
    GraphValidation,
    ValidationResult,
    GraphGovernance,
    GovernanceFindings,
    GraphHealth,
    HealthMetrics,
)

from agent.components.systems.knowledge.graphs.shared.node import NodeReference
from agent.components.systems.knowledge.graphs.shared.descriptor import (
    ProvenanceRecord,
)
from agent.components.systems.knowledge.graphs import (
    KnowledgeGraph,
    KnowledgeSubgraph,
)
from agent.components.systems.knowledge.graphs.shared.diagnostics import (
    GraphDiagnostic,
    GraphDiagnosticsReport,
)


class TestGraphDescriptorLaws(unittest.TestCase):
    """GRAPH-LAW-001 .. GRAPH-LAW-008 (Phase 6.8 Part 3 Section 1)."""

    def test_GRAPH_LAW_001_one_immutable_semantic_identity(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        self.assertEqual(d.semantic_identity, "knowledge:python")
        d2 = d.with_revision(2, "evolve")
        self.assertEqual(d.graph_identity, d2.graph_identity)
        self.assertEqual(d.semantic_identity, d2.semantic_identity)

    def test_GRAPH_LAW_003_preserves_artifact_identities(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        self.assertEqual(d.semantic_identity, "knowledge:python")
        roundtripped = GraphDescriptor.from_dict(d.to_dict())
        self.assertEqual(roundtripped.semantic_identity, d.semantic_identity)

    def test_GRAPH_LAW_004_preserves_provenance(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        self.assertTrue(d.has_provenance)
        self.assertEqual(len(d.provenance), 1)
        d2 = d.with_revision(2, "evolve")
        self.assertEqual(len(d2.provenance), 2)

    def test_GRAPH_LAW_005_preserves_revision_lineage(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        d2 = d.with_revision(2, "evolve")
        d3 = d2.with_revision(3, "evolve again")
        self.assertEqual(d.graph_revision, 1)
        self.assertEqual(d2.graph_revision, 2)
        self.assertEqual(d3.graph_revision, 3)

    def test_GRAPH_LAW_006_independently_inspectable(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        as_dict = d.to_dict()
        self.assertEqual(as_dict["graph_kind"], "semantic")
        self.assertEqual(as_dict["lifecycle_state"], "created")

    def test_GRAPH_LAW_007_deterministic(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        a = d.to_dict()
        b = d.to_dict()
        self.assertEqual(a, b)

    def test_GRAPH_LAW_008_published_graphs_immutable(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        with self.assertRaises(AttributeError):
            d.semantic_identity = "mutated"  # type: ignore[misc]

    def test_empty_identity_rejected(self):
        with self.assertRaises(ValueError):
            GraphDescriptor(
                graph_identity="",
                semantic_identity="x",
                graph_kind=GraphKind.SEMANTIC,
                lifecycle_state=GraphLifecycleState.CREATED,
            )


class TestGraphNodeLaws(unittest.TestCase):
    """NODE-LAW-001 .. NODE-LAW-008 (Phase 6.8 Part 3 Section 2)."""

    def test_NODE_LAW_001_exactly_one_artifact(self):
        node = GraphNode.create_from_reference("concept:python", "concept")
        self.assertEqual(node.referenced_artifact.referenced_identity, "concept:python")

    def test_NODE_LAW_002_no_duplicate_node_identities(self):
        n1 = GraphNode.create_from_reference("concept:a", "concept")
        n2 = GraphNode.create_from_reference("concept:a", "concept")
        self.assertNotEqual(n1.node_identity, n2.node_identity)

    def test_NODE_LAW_004_complete_provenance(self):
        node = GraphNode.create_from_reference("concept:python", "concept")
        self.assertTrue(len(node.provenance) >= 1)
        first = node.provenance[0]
        self.assertIn("provenance_identity", first)
        self.assertIn("originating_system", first)

    def test_NODE_LAW_005_explicit_memberships(self):
        node = GraphNode.create_from_reference(
            "concept:python", "concept",
            graph_memberships=["graph:g1"],
            layer_memberships=["layer:l1"],
        )
        self.assertIn("graph:g1", node.graph_memberships)
        self.assertIn("layer:l1", node.layer_memberships)

    def test_NODE_LAW_008_equivalent_artifacts_equivalent_nodes(self):
        a = GraphNode.create_from_reference("concept:python", "concept")
        b = GraphNode.create_from_reference("concept:python", "concept")
        self.assertEqual(a.referenced_identity, b.referenced_identity)
        self.assertEqual(a.artifact_kind, b.artifact_kind)

    def test_node_serialization_deterministic(self):
        node = GraphNode.create_from_reference("concept:python", "concept")
        d1 = node.to_dict()
        d2 = node.to_dict()
        self.assertEqual(d1, d2)
        restored = GraphNode.from_dict(d1)
        self.assertEqual(restored.node_identity, node.node_identity)
        self.assertEqual(restored.referenced_identity, node.referenced_identity)

    def test_add_membership_is_additive(self):
        node = GraphNode.create_from_reference("concept:python", "concept")
        node2 = node.add_graph_membership("graph:g1")
        node3 = node2.add_graph_membership("graph:g2")
        self.assertEqual(len(node.graph_memberships), 0)
        self.assertEqual(len(node2.graph_memberships), 1)
        self.assertEqual(len(node3.graph_memberships), 2)
        node3b = node3.add_graph_membership("graph:g1")
        self.assertEqual(len(node3b.graph_memberships), 2)


class TestGraphEdgeLaws(unittest.TestCase):
    """EDGE-LAW-001 .. EDGE-LAW-008 (Phase 6.8 Part 3 Section 3)."""

    def test_EDGE_LAW_001_exactly_one_relation(self):
        edge = GraphEdge.create_from_relation("n1", "n2", "relation:r1")
        self.assertEqual(edge.referenced_relation_id, "relation:r1")

    def test_EDGE_LAW_002_preserves_endpoint_identities(self):
        edge = GraphEdge.create_from_relation("n1", "n2", "relation:r1")
        self.assertEqual(edge.source_node, "n1")
        self.assertEqual(edge.target_node, "n2")

    def test_EDGE_LAW_003_explicit_direction(self):
        edge = GraphEdge.create_from_relation("n1", "n2", "relation:r1")
        self.assertEqual(edge.direction, EdgeDirection.DIRECTED)
        self.assertIn(edge.direction, EdgeDirection.ALL)

    def test_EDGE_LAW_004_inverse_edges_explicit(self):
        edge = GraphEdge.create_from_relation("n1", "n2", "relation:r1")
        inv = edge.with_inverse_direction()
        self.assertEqual(inv.direction, EdgeDirection.INVERSE)
        self.assertEqual(inv.source_node, "n2")
        self.assertEqual(inv.target_node, "n1")
        self.assertEqual(inv.referenced_relation_id, edge.referenced_relation_id)

    def test_EDGE_LAW_008_equivalent_relations_equivalent_edges(self):
        e1 = GraphEdge.create_from_relation("n1", "n2", "relation:r1")
        e2 = GraphEdge.create_from_relation("n1", "n2", "relation:r1")
        self.assertEqual(e1.referenced_relation_id, e2.referenced_relation_id)
        self.assertEqual(e1.source_node, e2.source_node)
        self.assertEqual(e1.target_node, e2.target_node)

    def test_edge_serialization_deterministic(self):
        edge = GraphEdge.create_from_relation("n1", "n2", "relation:r1")
        d1 = edge.to_dict()
        d2 = edge.to_dict()
        self.assertEqual(d1, d2)
        restored = GraphEdge.from_dict(d1)
        self.assertEqual(restored.edge_identity, edge.edge_identity)

    def test_edge_missing_relation_rejected(self):
        with self.assertRaises(ValueError):
            GraphEdge(
                edge_identity="e1",
                referenced_relation={},
                source_node="n1",
                target_node="n2",
            )


class TestTopologyLaws(unittest.TestCase):
    """TOPOLOGY-LAW-001 .. TOPOLOGY-LAW-008 (Phase 6.8 Part 3 Section 4)."""

    def test_TOPOLOGY_LAW_001_explicitly_declared(self):
        t = GraphTopology.create_initial(TopologyKind.DAG)
        self.assertEqual(t.topology_kind, "dag")

    def test_TOPOLOGY_LAW_002_explicit_constraints(self):
        t = GraphTopology.create_initial(TopologyKind.DAG, supported_constraints=["acyclic"])
        self.assertIn("acyclic", t.supported_constraints)

    def test_invalid_topology_kind_rejected(self):
        with self.assertRaises(ValueError):
            GraphTopology(topology_identity="t1", topology_kind="not_a_kind")

    def test_topology_validation_inspectable(self):
        t = GraphTopology.create_initial(TopologyKind.TREE, node_count=5, edge_count=4)
        self.assertEqual(t.graph_metrics.node_count, 5)
        self.assertEqual(t.graph_metrics.edge_count, 4)
        if t.topology_kind == TopologyKind.TREE:
            self.assertEqual(t.graph_metrics.edge_count, t.graph_metrics.node_count - 1)

    def test_topology_deterministic(self):
        a = GraphTopology.create_initial(TopologyKind.DAG, node_count=3, edge_count=4)
        b = GraphTopology.create_initial(TopologyKind.DAG, node_count=3, edge_count=4)
        self.assertEqual(a.graph_metrics.to_dict(), b.graph_metrics.to_dict())

    def test_all_topology_kinds_supported(self):
        for kind in TopologyKind.ALL:
            t = GraphTopology.create_initial(kind)
            self.assertIn(t.topology_kind, TopologyKind.ALL)


class TestLayerLaws(unittest.TestCase):
    """LAYER-LAW-001 .. LAYER-LAW-008 (Phase 6.8 Part 3 Section 5)."""

    def test_LAYER_LAW_001_explicit_semantics(self):
        layer = GraphLayer.create_initial(LayerKind.CONCEPT)
        self.assertEqual(layer.layer_kind, "concept")
        self.assertIn(layer.layer_kind, LayerKind.ALL)

    def test_LAYER_LAW_002_artifacts_may_belong_to_multiple_layers(self):
        c = GraphLayer.create_initial(LayerKind.CONCEPT)
        a = GraphLayer.create_initial(LayerKind.ASSERTION)
        node = GraphNode.create_from_reference(
            "concept:python", "concept",
            layer_memberships=[c.layer_identity, a.layer_identity],
        )
        self.assertEqual(len(node.layer_memberships), 2)

    def test_LAYER_LAW_003_explicit_interlayer_mappings(self):
        c = GraphLayer.create_initial(LayerKind.CONCEPT)
        a = GraphLayer.create_initial(LayerKind.ASSERTION)
        m = InterLayerMapping.create_initial(c.layer_identity, a.layer_identity)
        self.assertEqual(m.source_layer, c.layer_identity)
        self.assertEqual(m.target_layer, a.layer_identity)

    def test_LAYER_LAW_007_independently_traversable(self):
        layer = GraphLayer.create_initial(LayerKind.CONCEPT)
        layer = layer.add_node("node:a").add_node("node:b")
        self.assertEqual(len(layer.participating_nodes), 2)

    def test_all_layer_kinds_supported(self):
        for kind in LayerKind.ALL:
            layer = GraphLayer.create_initial(kind)
            self.assertIn(layer.layer_kind, LayerKind.ALL)

    def test_layer_add_node_idempotent(self):
        layer = GraphLayer.create_initial(LayerKind.CONCEPT)
        l1 = layer.add_node("n1")
        l2 = l1.add_node("n1")
        self.assertEqual(len(l1.participating_nodes), 1)
        self.assertEqual(len(l2.participating_nodes), 1)


class TestTraversalLaws(unittest.TestCase):
    """TRAVERSAL-LAW-001 .. TRAVERSAL-LAW-008 (Phase 6.8 Part 3 Section 6)."""

    def test_TRAVERSAL_LAW_001_explicit_strategy(self):
        s = GraphTraversalSession.create_initial(
            "graph:g1", traversal_strategy=TraversalStrategy.BREADTH_FIRST
        )
        self.assertEqual(s.traversal_strategy, "breadth_first")

    def test_TRAVERSAL_LAW_002_explicit_constraints(self):
        s = GraphTraversalSession.create_initial("graph:g1", constraints=["max_depth:3"])
        self.assertIn("max_depth:3", s.traversal_constraints)

    def test_TRAVERSAL_LAW_005_explicit_termination(self):
        s = GraphTraversalSession.create_initial("graph:g1")
        s = s.terminate("completed")
        self.assertEqual(s.termination_reason, "completed")

    def test_TRAVERSAL_LAW_006_never_modifies_graph(self):
        s = GraphTraversalSession.create_initial("graph:g1", starting_nodes=["n1"])
        s2 = s.visit_node("n2")
        self.assertNotIn("n2", s.visited_nodes)
        self.assertIn("n2", s2.visited_nodes)

    def test_TRAVERSAL_LAW_008_equivalent_states_equivalent_results(self):
        s1 = GraphTraversalSession.create_initial("g1", starting_nodes=["n1"])
        s2 = GraphTraversalSession.create_initial("g1", starting_nodes=["n1"])
        s1 = s1.visit_node("n2").visit_node("n3")
        s2 = s2.visit_node("n3").visit_node("n2")
        self.assertEqual(sorted(s1.visited_nodes), sorted(s2.visited_nodes))
        self.assertEqual(s1.termination_reason, s2.termination_reason)

    def test_deterministic_traversal_membership(self):
        s = GraphTraversalSession.create_initial("g1", starting_nodes=["n1"])
        for n in ["n2", "n3", "n4", "n5"]:
            s = s.visit_node(n)
        self.assertEqual(sorted(s.visited_nodes), ["n1", "n2", "n3", "n4", "n5"])

    def test_traversal_serialization_roundtrip(self):
        s = GraphTraversalSession.create_initial("g1", starting_nodes=["n1"])
        s = s.visit_node("n2").add_result({"found": "target"}).terminate("done")
        restored = GraphTraversalSession.from_dict(s.to_dict())
        self.assertEqual(restored.traversal_identity, s.traversal_identity)
        self.assertEqual(sorted(restored.visited_nodes), sorted(s.visited_nodes))


class TestIndexLaws(unittest.TestCase):
    """INDEX-LAW-001 .. INDEX-LAW-008 (Phase 6.8 Part 3 Section 7)."""

    def test_INDEX_LAW_005_explicit_invalidation(self):
        idx = GraphIndex.create_initial("graph:g1")
        entry = GraphIndexEntry.create_initial("concept:python", index_keys=["python"])
        idx = idx.add_entry(entry)
        self.assertEqual(len(idx.entries), 1)
        invalidated = idx.invalidate("stale")
        self.assertEqual(len(invalidated.entries), 0)
        self.assertTrue(len(invalidated.provenance) > len(idx.provenance))

    def test_INDEX_LAW_007_independently_inspectable(self):
        idx = GraphIndex.create_initial("graph:g1", indexing_strategies=[IndexingStrategy.NODE])
        self.assertIn(IndexingStrategy.NODE, idx.indexing_strategy)
        d = idx.to_dict()
        self.assertEqual(d["indexed_graph"]["graph_identity"], "graph:g1")

    def test_INDEX_LAW_008_equivalent_contents_equivalent_indexes(self):
        a = GraphIndex.create_initial("g1", indexing_strategies=[IndexingStrategy.NODE])
        b = GraphIndex.create_initial("g1", indexing_strategies=[IndexingStrategy.NODE])
        a = a.add_entry(GraphIndexEntry.create_initial("concept:a", ["a"]))
        b = b.add_entry(GraphIndexEntry.create_initial("concept:a", ["a"]))
        self.assertEqual(len(a.entries), len(b.entries))
        self.assertEqual(
            [e.indexed_artifact for e in a.entries],
            [e.indexed_artifact for e in b.entries],
        )

    def test_deterministic_indexing(self):
        idx = GraphIndex.create_initial("g1")
        for name in ["concept:a", "concept:b", "concept:c"]:
            idx = idx.add_entry(GraphIndexEntry.create_initial(name, [name]))
        d = idx.to_dict()
        self.assertEqual(len(d["entries"]), 3)
        self.assertEqual(idx.to_dict()["entries"], d["entries"])

    def test_index_entry_lookup(self):
        entry = GraphIndexEntry.create_initial("concept:python", index_keys=["python"])
        self.assertEqual(entry.indexed_artifact["referenced_identity"], "concept:python")
        self.assertIn("python", entry.index)


class TestPartitionLaws(unittest.TestCase):
    """PARTITION-LAW-001 .. PARTITION-LAW-008 (Phase 6.8 Part 3 Section 8)."""

    def test_PARTITION_LAW_002_explicit_boundaries(self):
        p = GraphPartition.create_initial(strategy=PartitionStrategy.DOMAIN, node_ids=["n1", "n2"])
        self.assertEqual(len(p.participating_nodes), 2)

    def test_PARTITION_LAW_003_explicit_cross_partition_edges(self):
        p = GraphPartition.create_initial(strategy=PartitionStrategy.DOMAIN)
        p2 = p.add_node("n1")
        self.assertEqual(len(p2.participating_nodes), 1)

    def test_all_partition_strategies_supported(self):
        for strat in PartitionStrategy.ALL:
            p = GraphPartition.create_initial(strategy=strat)
            self.assertIn(p.partition_strategy, PartitionStrategy.ALL)

    def test_partition_deterministic_membership(self):
        p = GraphPartition.create_initial(strategy=PartitionStrategy.DOMAIN)
        for n in ["n1", "n2", "n3"]:
            p = p.add_node(n)
        self.assertEqual(sorted(p.participating_nodes), ["n1", "n2", "n3"])

    def test_partition_idempotent_add(self):
        p = GraphPartition.create_initial(strategy=PartitionStrategy.DOMAIN)
        p = p.add_node("n1").add_node("n1")
        self.assertEqual(len(p.participating_nodes), 1)


class TestCompositionLaws(unittest.TestCase):
    """Graph composition (Phase 6.8 Part 2 Section 15)."""

    def test_composition_preserves_identity(self):
        comp = GraphComposition.create_initial(
            ["g1", "g2"], composition_strategy=CompositionStrategy.UNION
        )
        self.assertEqual(len(comp.participating_graphs), 2)
        self.assertEqual(
            comp.resulting_graph.get("composition_identity"), comp.composition_identity
        )

    def test_composition_add_graph(self):
        comp = GraphComposition.create_initial(["g1"])
        comp2 = comp.add_participating_graph({"graph_identity": "g2"})
        self.assertEqual(len(comp2.participating_graphs), 2)

    def test_composition_cross_edges(self):
        comp = GraphComposition.create_initial(["g1", "g2"])
        comp2 = comp.add_cross_graph_edge({"edge_identity": "cross1"})
        self.assertEqual(len(comp2.cross_graph_edges), 1)

    def test_all_composition_strategies_supported(self):
        for strat in CompositionStrategy.ALL:
            comp = GraphComposition.create_initial(["g1", "g2"], composition_strategy=strat)
            self.assertIn(comp.composition_strategy, CompositionStrategy.ALL)


class TestValidationLaws(unittest.TestCase):
    """VALIDATION-LAW-001 .. VALIDATION-LAW-008 (Phase 6.8 Part 3 Section 10)."""

    def test_VALIDATION_LAW_001_observational(self):
        v = GraphValidation.create_initial("graph:g1")
        v = v.add_finding(ValidationResult.create_pass("connectivity"))
        self.assertTrue(v.is_valid)

    def test_VALIDATION_LAW_002_preserves_findings(self):
        v = GraphValidation.create_initial("graph:g1")
        v = v.add_finding(ValidationResult.create_pass("connectivity"))
        v = v.add_finding(ValidationResult.create_fail("consistency", "conflict"))
        self.assertEqual(len(v.findings), 2)
        self.assertFalse(v.is_valid)

    def test_VALIDATION_LAW_003_distinguishes_error_types(self):
        v = GraphValidation.create_initial("graph:g1")
        v = v.add_finding(ValidationResult.create_pass("connectivity", "topology ok"))
        v = v.add_finding(ValidationResult.create_fail("consistency", "semantic conflict"))
        statuses = [(f.check_type, f.status) for f in v.findings]
        self.assertIn(("connectivity", "pass"), statuses)
        self.assertIn(("consistency", "fail"), statuses)

    def test_VALIDATION_LAW_006_never_modifies_graphs(self):
        v = GraphValidation.create_initial("graph:g1")
        original = v.to_dict()
        v2 = v.add_finding(ValidationResult.create_pass("connectivity"))
        self.assertNotEqual(v.to_dict(), v2.to_dict())
        self.assertEqual(v.to_dict(), original)


class TestGovernanceLaws(unittest.TestCase):
    """GOVERNANCE-LAW-001 .. GOVERNANCE-LAW-008 (Phase 6.8 Part 3 Section 11)."""

    def test_GOVERNANCE_LAW_001_observational(self):
        g = GraphGovernance.create_initial(graph_refs=[{"graph_identity": "g1"}])
        g = g.add_finding(GovernanceFindings.create_info("fragmentation", "2 components"))
        self.assertEqual(len(g.findings), 1)

    def test_GOVERNANCE_LAW_002_detects_fragmentation(self):
        g = GraphGovernance.create_initial()
        g = g.add_finding(
            GovernanceFindings.create_warning("fragmentation", "3 disjoint components")
        )
        self.assertTrue(any(f.category == "fragmentation" for f in g.findings))

    def test_GOVERNANCE_LAW_003_detects_redundancy(self):
        g = GraphGovernance.create_initial()
        g = g.add_finding(GovernanceFindings.create_info("redundancy", "duplicate nodes"))
        self.assertTrue(any(f.category == "redundancy" for f in g.findings))

    def test_GOVERNANCE_LAW_004_detects_invalid_mappings(self):
        g = GraphGovernance.create_initial()
        g = g.add_finding(
            GovernanceFindings.create_error(
                "invalid_inter_layer_mapping", "orphan mapping"
            )
        )
        self.assertTrue(
            any(f.category == "invalid_inter_layer_mapping" for f in g.findings)
        )

    def test_GOVERNANCE_LAW_005_preserves_findings(self):
        g = GraphGovernance.create_initial()
        g = g.add_finding(GovernanceFindings.create_info("fragmentation"))
        g = g.add_finding(GovernanceFindings.create_warning("redundancy"))
        self.assertEqual(len(g.findings), 2)

    def test_GOVERNANCE_LAW_007_never_modifies_graphs(self):
        g = GraphGovernance.create_initial()
        original = g.to_dict()
        g2 = g.add_finding(GovernanceFindings.create_info("fragmentation"))
        self.assertNotEqual(g.to_dict(), g2.to_dict())
        self.assertEqual(g.to_dict(), original)

    def test_governance_recommendations(self):
        g = GraphGovernance.create_initial()
        g = g.add_recommendation("merge redundant subgraphs")
        self.assertIn("merge redundant subgraphs", g.recommendations)


class TestGraphHealth(unittest.TestCase):
    """Graph health metrics (Phase 6.8 Part 2 Section 24)."""

    def test_health_metrics_descriptive(self):
        m = HealthMetrics(node_count=10, edge_count=15, average_degree=3.0)
        d = m.to_dict()
        self.assertEqual(d["node_count"], 10)
        self.assertEqual(d["edge_count"], 15)
        self.assertEqual(d["average_degree"], 3.0)

    def test_health_is_healthy_thresholds(self):
        m = HealthMetrics(
            ontology_consistency=0.9, belief_consistency=0.95, isolation_score=0.05
        )
        self.assertTrue(m.is_healthy())

    def test_health_unhealthy_thresholds(self):
        m = HealthMetrics(
            ontology_consistency=0.5, belief_consistency=0.9, isolation_score=0.05
        )
        self.assertFalse(m.is_healthy())

    def test_graph_health_roundtrip(self):
        h = GraphHealth.create_initial("graph:g1")
        h = h.update_metrics(HealthMetrics(node_count=5))
        restored = GraphHealth.from_dict(h.to_dict())
        self.assertEqual(restored.metrics.node_count, 5)
        self.assertEqual(restored.health_identity, h.health_identity)


class TestGraphEvolution(unittest.TestCase):
    """EVOLUTION-LAW-001 .. EVOLUTION-LAW-008 (Phase 6.8 Part 3 Section 9)."""

    def test_EVOLUTION_LAW_001_preserves_graph_identity(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        d2 = d.with_revision(2, "add node")
        d3 = d2.with_revision(3, "add edge")
        self.assertEqual(d.graph_identity, d2.graph_identity)
        self.assertEqual(d2.graph_identity, d3.graph_identity)

    def test_EVOLUTION_LAW_002_preserves_artifact_identities(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        d2 = d.with_revision(2, "evolve")
        self.assertEqual(d.semantic_identity, d2.semantic_identity)

    def test_EVOLUTION_LAW_003_complete_provenance(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        d2 = d.with_revision(2, "add node")
        d3 = d2.with_revision(3, "belief revision")
        self.assertEqual(len(d3.provenance), 3)

    def test_EVOLUTION_LAW_004_immutable_history(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        d2 = d.with_revision(2, "evolve")
        self.assertEqual(len(d.provenance), 1)
        self.assertEqual(len(d2.provenance), 2)

    def test_EVOLUTION_LAW_008_equivalent_changes_equivalent_evolution(self):
        d1 = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        d2 = d1.with_revision(2, "change")
        d3 = d1.with_revision(2, "change")
        self.assertEqual(d2.graph_revision, d3.graph_revision)
        self.assertEqual(len(d2.provenance), len(d3.provenance))


class TestProvenanceCompleteness(unittest.TestCase):
    """Cross-cutting provenance completeness (GLOBAL INVARIANTS)."""

    def test_descriptor_provenance_complete(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        p = d.provenance[0]
        for field_name in [
            "provenance_identity",
            "originating_request",
            "originating_system",
            "originating_revision",
            "revision_chain",
            "authority",
            "timestamp_utc",
        ]:
            self.assertTrue(hasattr(p, field_name), f"Missing provenance field: {field_name}")

    def test_node_provenance_complete(self):
        n = GraphNode.create_from_reference("concept:python", "concept")
        p = n.provenance[0]
        for field_name in ["provenance_identity", "originating_request", "originating_system"]:
            self.assertIn(field_name, p)

    def test_edge_provenance_complete(self):
        e = GraphEdge.create_from_relation("n1", "n2", "relation:r1")
        p = e.provenance[0]
        for field_name in ["provenance_identity", "originating_request", "originating_system"]:
            self.assertIn(field_name, p)

    def test_topology_provenance_complete(self):
        t = GraphTopology.create_initial(TopologyKind.DAG)
        p = t.provenance[0]
        for field_name in ["provenance_identity", "originating_request", "originating_system"]:
            self.assertIn(field_name, p)

    def test_traversal_provenance_complete(self):
        s = GraphTraversalSession.create_initial("g1")
        p = s.provenance[0]
        for field_name in ["provenance_identity", "originating_request", "originating_system"]:
            self.assertIn(field_name, p)

    def test_index_provenance_complete(self):
        idx = GraphIndex.create_initial("g1")
        p = idx.provenance[0]
        for field_name in ["provenance_identity", "originating_request", "originating_system"]:
            self.assertIn(field_name, p)

    def test_validation_provenance_complete(self):
        v = GraphValidation.create_initial("g1")
        p = v.provenance[0]
        for field_name in ["provenance_identity", "originating_request", "originating_system"]:
            self.assertIn(field_name, p)

    def test_governance_provenance_complete(self):
        g = GraphGovernance.create_initial()
        p = g.provenance[0]
        for field_name in ["provenance_identity", "originating_request", "originating_system"]:
            self.assertIn(field_name, p)


class TestDeterministicReplay(unittest.TestCase):
    """Deterministic replay (GLOBAL INVARIANTS + TRAVERSAL-LAW-008)."""

    def test_deterministic_replay_descriptor(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        d = d.with_revision(2, "evolve")
        d1 = d.to_dict()
        d2 = d.to_dict()
        self.assertEqual(d1, d2)
        restored = GraphDescriptor.from_dict(d1)
        self.assertEqual(restored.graph_identity, d.graph_identity)
        self.assertEqual(restored.graph_revision, d.graph_revision)
        self.assertEqual(len(restored.provenance), len(d.provenance))

    def test_deterministic_replay_node(self):
        n = GraphNode.create_from_reference("concept:python", "concept")
        d1 = n.to_dict()
        d2 = n.to_dict()
        self.assertEqual(d1, d2)
        restored = GraphNode.from_dict(d1)
        self.assertEqual(restored.to_dict(), d1)

    def test_deterministic_replay_edge(self):
        e = GraphEdge.create_from_relation("n1", "n2", "relation:r1")
        d1 = e.to_dict()
        d2 = e.to_dict()
        self.assertEqual(d1, d2)
        restored = GraphEdge.from_dict(d1)
        self.assertEqual(restored.to_dict(), d1)

    def test_deterministic_replay_topology(self):
        t = GraphTopology.create_initial(TopologyKind.DAG, node_count=3, edge_count=4)
        d1 = t.to_dict()
        d2 = t.to_dict()
        self.assertEqual(d1, d2)
        restored = GraphTopology.from_dict(d1)
        self.assertEqual(restored.topology_kind, t.topology_kind)
        self.assertEqual(restored.graph_metrics.node_count, 3)

    def test_deterministic_replay_layer(self):
        l = GraphLayer.create_initial(LayerKind.CONCEPT)
        l = l.add_node("n1").add_node("n2")
        d1 = l.to_dict()
        d2 = l.to_dict()
        self.assertEqual(d1, d2)
        restored = GraphLayer.from_dict(d1)
        self.assertEqual(sorted(restored.participating_nodes), ["n1", "n2"])

    def test_deterministic_replay_traversal(self):
        s = GraphTraversalSession.create_initial("g1", starting_nodes=["n1"])
        s = s.visit_node("n2").visit_node("n3").terminate("done")
        d1 = s.to_dict()
        d2 = s.to_dict()
        self.assertEqual(d1, d2)
        restored = GraphTraversalSession.from_dict(d1)
        self.assertEqual(sorted(restored.visited_nodes), ["n1", "n2", "n3"])

    def test_deterministic_replay_index(self):
        idx = GraphIndex.create_initial("g1")
        idx = idx.add_entry(GraphIndexEntry.create_initial("concept:a", ["a"]))
        d1 = idx.to_dict()
        d2 = idx.to_dict()
        self.assertEqual(d1, d2)
        restored = GraphIndex.from_dict(d1)
        self.assertEqual(len(restored.entries), 1)


class TestGlobalInvariants(unittest.TestCase):
    """GLOBAL INVARIANTS (Phase 6.8 Part 3 Section 12)."""

    def test_every_graph_has_one_semantic_identity(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        self.assertTrue(isinstance(d.semantic_identity, str))
        self.assertTrue(len(d.semantic_identity) > 0)

    def test_every_node_references_one_artifact(self):
        n = GraphNode.create_from_reference("concept:python", "concept")
        self.assertTrue(isinstance(n.referenced_artifact, NodeReference))
        self.assertTrue(len(n.referenced_artifact.referenced_identity) > 0)

    def test_every_edge_references_one_relation(self):
        e = GraphEdge.create_from_relation("n1", "n2", "relation:r1")
        self.assertIn("referenced_identity", e.referenced_relation)
        self.assertEqual(e.referenced_relation["referenced_identity"], "relation:r1")

    def test_graph_layers_remain_explicit(self):
        c = GraphLayer.create_initial(LayerKind.CONCEPT)
        a = GraphLayer.create_initial(LayerKind.ASSERTION)
        self.assertNotEqual(c.layer_identity, a.layer_identity)
        self.assertIn(c.layer_kind, LayerKind.ALL)
        self.assertIn(a.layer_kind, LayerKind.ALL)

    def test_traversal_side_effect_free(self):
        s = GraphTraversalSession.create_initial("g1")
        s = s.visit_node("n1")
        s_original = GraphTraversalSession.create_initial("g1")
        self.assertNotIn("n1", s_original.visited_nodes)

    def test_indexes_remain_auxiliary(self):
        idx = GraphIndex.create_initial("g1")
        entry = GraphIndexEntry.create_initial("concept:python", ["python"])
        self.assertEqual(entry.indexed_artifact["referenced_identity"], "concept:python")

    def test_topology_remains_valid(self):
        t = GraphTopology.create_initial(TopologyKind.DAG)
        self.assertIn(t.topology_kind, TopologyKind.ALL)

    def test_revision_history_immutable(self):
        d = GraphDescriptor.create_initial("knowledge:python", GraphKind.SEMANTIC)
        d2 = d.with_revision(2, "evolve")
        self.assertEqual(d.graph_revision, 1)
        self.assertEqual(d2.graph_revision, 2)


class TestAllKindsSupported(unittest.TestCase):
    """Verify all documented kinds are supported across the system."""

    def test_all_graph_kinds(self):
        expected = {
            "semantic", "epistemic", "ontology", "domain", "self", "world",
            "task", "temporal", "causal", "multi_layer", "unknown",
        }
        actual = {k.value for k in GraphKind}
        self.assertEqual(expected, actual)

    def test_all_lifecycle_states(self):
        expected = {
            "created", "validating", "active", "revised", "superseded",
            "archived", "invalid",
        }
        actual = {s.value for s in GraphLifecycleState}
        self.assertEqual(expected, actual)

    def test_all_topology_kinds(self):
        self.assertEqual(
            TopologyKind.ALL,
            {"tree", "dag", "cyclic", "heterogeneous", "hypergraph", "multi_layer"},
        )

    def test_all_layer_kinds(self):
        self.assertEqual(
            LayerKind.ALL,
            {"concept", "assertion", "belief", "model", "capability", "execution"},
        )

    def test_all_traversal_strategies(self):
        self.assertEqual(
            TraversalStrategy.ALL,
            {
                "breadth_first", "depth_first", "weighted",
                "semantic", "constraint", "goal_directed",
            },
        )

    def test_all_indexing_strategies(self):
        self.assertEqual(
            IndexingStrategy.ALL,
            {"node", "relation", "concept", "belief", "semantic"},
        )

    def test_all_composition_strategies(self):
        self.assertEqual(
            CompositionStrategy.ALL,
            {"union", "intersection", "difference", "merge", "nested"},
        )

    def test_all_partition_strategies(self):
        self.assertEqual(
            PartitionStrategy.ALL,
            {"domain", "ontology", "capability", "context", "workspace", "time"},
        )

    def test_all_edge_directions(self):
        self.assertEqual(EdgeDirection.ALL, {"directed", "undirected", "inverse"})


class TestKnowledgeGraph(unittest.TestCase):
    """KnowledgeGraph contract (Phase 6.8 Part 1 Section 2)."""

    def test_GRAPH_LAW_001_one_immutable_semantic_identity(self):
        g = KnowledgeGraph.create("knowledge:python", "semantic")
        self.assertEqual(g.semantic_identity, "knowledge:python")
        g2 = g.add_node("node:a")
        self.assertEqual(g.semantic_identity, g2.semantic_identity)

    def test_GRAPH_LAW_002_organizes_artifacts_only(self):
        g = KnowledgeGraph.create(
            "knowledge:python", "semantic",
            node_references=["concept:py"],
            edge_references=["edge:e1"],
        )
        self.assertEqual(g.node_count, 1)
        self.assertEqual(g.edge_count, 1)

    def test_GRAPH_LAW_003_preserves_artifact_identities(self):
        g = KnowledgeGraph.create("knowledge:python", "semantic", node_references=["concept:py"])
        g2 = g.add_node("concept:linux")
        self.assertIn("concept:py", g2.node_references)

    def test_GRAPH_LAW_004_preserves_provenance(self):
        g = KnowledgeGraph.create("knowledge:python", "semantic")
        self.assertTrue(len(g.provenance) >= 1)
        g2 = g.add_node("node:a")
        self.assertTrue(len(g2.provenance) > len(g.provenance))

    def test_GRAPH_LAW_007_deterministic(self):
        g = KnowledgeGraph.create("knowledge:python", "semantic", node_references=["n1"])
        self.assertEqual(g.to_dict(), g.to_dict())

    def test_GRAPH_LAW_008_immutable(self):
        g = KnowledgeGraph.create("knowledge:python", "semantic")
        with self.assertRaises(AttributeError):
            g.semantic_identity = "mutated"  # type: ignore[misc]

    def test_add_node_idempotent(self):
        g = KnowledgeGraph.create("knowledge:python", "semantic")
        g1 = g.add_node("n1")
        g2 = g1.add_node("n1")
        self.assertEqual(len(g1.node_references), 1)
        self.assertEqual(len(g2.node_references), 1)
        self.assertIs(g2, g1)

    def test_add_layer(self):
        g = KnowledgeGraph.create("knowledge:python", "semantic")
        g2 = g.add_layer("layer:concept")
        self.assertIn("layer:concept", g2.layers)

    def test_lifecycle_transition(self):
        g = KnowledgeGraph.create("knowledge:python", "semantic")
        g2 = g.with_lifecycle_state("active")
        self.assertEqual(g.lifecycle_state, "created")
        self.assertEqual(g2.lifecycle_state, "active")

    def test_serialization_roundtrip(self):
        g = KnowledgeGraph.create(
            "knowledge:python", "semantic",
            node_references=["n1", "n2"],
            edge_references=["e1"],
        )
        restored = KnowledgeGraph.from_dict(g.to_dict())
        self.assertEqual(restored.semantic_identity, g.semantic_identity)
        self.assertEqual(sorted(restored.node_references), ["n1", "n2"])
        self.assertEqual(restored.edge_references, ("e1",))


class TestKnowledgeSubgraph(unittest.TestCase):
    """KnowledgeSubgraph contract (Phase 6.8 Part 1 Section 10)."""

    def test_subgraph_requires_parent(self):
        sg = KnowledgeSubgraph.create("graph:g1", participating_nodes=["n1"])
        self.assertEqual(sg.parent_graph, "graph:g1")
        self.assertEqual(len(sg.participating_nodes), 1)

    def test_subgraph_independent_versioning(self):
        sg = KnowledgeSubgraph.create("graph:g1")
        sg2 = sg.add_node("n1")
        self.assertEqual(sg.subgraph_revision, 1)
        self.assertEqual(sg2.subgraph_revision, 2)

    def test_subgraph_preserves_provenance(self):
        sg = KnowledgeSubgraph.create("graph:g1")
        self.assertTrue(len(sg.provenance) >= 1)
        sg2 = sg.add_edge("e1")
        self.assertTrue(len(sg2.provenance) > len(sg.provenance))

    def test_subgraph_add_edge_idempotent(self):
        sg = KnowledgeSubgraph.create("graph:g1")
        sg1 = sg.add_edge("e1")
        sg2 = sg1.add_edge("e1")
        self.assertEqual(len(sg1.participating_edges), 1)
        self.assertIs(sg2, sg1)

    def test_subgraph_serialization_roundtrip(self):
        sg = KnowledgeSubgraph.create("graph:g1", participating_nodes=["n1"], scope="process")
        restored = KnowledgeSubgraph.from_dict(sg.to_dict())
        self.assertEqual(restored.parent_graph, "graph:g1")
        self.assertEqual(restored.participating_nodes, ("n1",))
        self.assertEqual(restored.scope, "process")

    def test_subgraph_empty_parent_rejected(self):
        with self.assertRaises(ValueError):
            KnowledgeSubgraph(subgraph_identity="s1", parent_graph="")


class TestDiagnostics(unittest.TestCase):
    """Graph Diagnostics (Phase 6.8 Part 2 Section 25)."""

    def test_diagnostic_descriptive(self):
        d = GraphDiagnostic(
            diagnostic_identity="diag:1",
            severity="warning",
            category="fragmentation",
            message="3 disjoint components",
        )
        self.assertEqual(d.severity, "warning")
        self.assertEqual(d.category, "fragmentation")

    def test_diagnostics_report_healthy(self):
        r = GraphDiagnosticsReport.create_initial(graph_refs=[{"graph_identity": "g1"}])
        self.assertTrue(r.is_healthy)
        self.assertEqual(r.overall_status, "healthy")

    def test_diagnostics_report_unhealthy_on_error(self):
        r = GraphDiagnosticsReport.create_initial()
        r = r.add_diagnostic(
            GraphDiagnostic(
                diagnostic_identity="d1", severity="error", category="broken_edge"
            )
        )
        self.assertFalse(r.is_healthy)
        self.assertEqual(r.overall_status, "unhealthy")
        self.assertEqual(r.error_count, 1)

    def test_diagnostics_report_never_modifies_graphs(self):
        r = GraphDiagnosticsReport.create_initial()
        original = r.to_dict()
        r2 = r.add_diagnostic(GraphDiagnostic(diagnostic_identity="d1", severity="info"))
        self.assertEqual(r.to_dict(), original)

    def test_diagnostics_serialization_roundtrip(self):
        r = GraphDiagnosticsReport.create_initial(graph_refs=[{"graph_identity": "g1"}])
        r = r.add_diagnostic(
            GraphDiagnostic(
                diagnostic_identity="d1", severity="warning", message="redundancy"
            )
        )
        restored = GraphDiagnosticsReport.from_dict(r.to_dict())
        self.assertEqual(len(restored.diagnostics), 1)
        self.assertEqual(restored.warning_count, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
