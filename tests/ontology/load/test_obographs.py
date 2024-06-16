import typing
import pytest

import hpotk
import hpotk as hp
from hpotk.model import TermId, MinimalTerm
from hpotk.ontology.load.obographs import *


class TestLoad:

    def test_load_minimal_ontology(self, fpath_toy_hpo: str):
        o: hp.ontology.MinimalOntology = load_minimal_ontology(fpath_toy_hpo)

        assert o is not None, "Ontology must not be None"
        assert isinstance(o, hp.ontology.MinimalOntology)
        assert o.version == '2022-10-05'
        assert 393 == len(o), "There must be 393 terms in the ontology"
        assert 557 == len(list(o.term_ids)), "There must be 557 term IDs in the ontology"
        assert 557 == len(set(o.term_ids)), "There must be 557 unique term IDs in the ontology"
        assert all([term_id in o for term_id in o.term_ids]), "The ontology must contain all term IDs"
        assert all([o.get_term(k) is not None for k in o.term_ids]), \
            "The `get_term` must get primary term for any term ID from ontology"
        assert all([o.get_term(k.value) is not None for k in o.term_ids]), \
            "The `get_term` must get primary term for any term ID value from ontology"
        assert all([o.get_term(k).identifier == k or k in o.get_term(k).alt_term_ids for k in o.term_ids]), \
            "Each term ID must be either primary or alternative ID"

    def test_load_ontology(self, fpath_toy_hpo: str):
        o: hp.ontology.Ontology = load_ontology(fpath_toy_hpo)

        assert o is not None, "Ontology must not be None"
        assert isinstance(o, hp.ontology.Ontology)

        assert o.version == '2022-10-05'
        assert 393 == len(o), "There must be 393 terms in the ontology"
        assert 557 == len(list(o.term_ids)), "There must be 557 term IDs in the ontology"
        assert 557 == len(set(o.term_ids)), "There must be 557 unique term IDs in the ontology"
        assert all(term_id in o for term_id in o.term_ids), \
            "The ontology must contain all term IDs"
        assert all(o.get_term(k) is not None for k in o.term_ids), \
            "The `get_term` must get primary term for any term ID from ontology"
        assert all(o.get_term(k).identifier == k or k in o.get_term(k).alt_term_ids for k in o.term_ids), \
            "Each term ID must be either primary or alternative ID"

    def test_load_minimal_ontology_backed_by_csr(self, fpath_toy_hpo: str):
        term_factory = hp.ontology.load.obographs.MinimalTermFactory()
        graph_factory = hp.graph.CsrGraphFactory()
        o: hp.ontology.MinimalOntology = load_minimal_ontology(
            fpath_toy_hpo,
            term_factory=term_factory,
            graph_factory=graph_factory,
        )
        assert o is not None, "Ontology must not be None"

        arachnodactyly = TermId.from_curie("HP:0001166")
        assert all(
            [
                val.value in {"HP:0001238", "HP:0100807"}
                for val in (o.graph.get_parents(arachnodactyly))
            ]
        )
        assert len(list(o.graph.get_children(arachnodactyly))) == 0

    @pytest.mark.skip
    def test_print_stats(self, fpath_toy_hpo: str):
        import json

        with open(fpath_toy_hpo) as fh:
            graphs = json.load(fh)

        graph = graphs["graphs"][0]
        all_nodes = graph["nodes"]
        all_edges = graph["edges"]
        print(f"All nodes: {len(all_nodes)}, all edges: {len(all_edges)}")
        current_nodes = self._get_current_nodes(all_nodes)
        print(f"Current nodes: {len(current_nodes)}")
        # Getting the number of all term IDs is too complicated to be implemented here at this moment.
        # The functionality should be implemented later if necessary.

    @staticmethod
    def _get_current_nodes(nodes):
        result = []
        for node in nodes:
            if "meta" in node:
                meta = node["meta"]
                if "deprecated" in meta:
                    deprecated = meta["deprecated"]
                    if not deprecated:
                        result.append(node)
                else:
                    result.append(node)
        return result


class TestTerms:
    """
    We only load the ontology once, and we test the properties of the loaded data.
    """

    @pytest.fixture(scope="class")
    def toy_ontology(self, fpath_toy_hpo: str) -> hpotk.Ontology:
        return load_ontology(fpath_toy_hpo)

    def test_term_properties(self, toy_ontology: hpotk.Ontology):
        # Test properties of a Term
        term = toy_ontology.get_term("HP:0001626")

        assert term is not None
        assert term.identifier.value == "HP:0001626"
        assert term.name == "Abnormality of the cardiovascular system"
        definition = term.definition
        assert definition.definition == "Any abnormality of the cardiovascular system."
        assert definition.xrefs == ("HPO:probinson",)
        assert (
            term.comment
            == "The cardiovascular system consists of the heart, vasculature, and the lymphatic system."
        )

        assert not term.is_obsolete
        assert term.alt_term_ids == (TermId.from_curie("HP:0003116"),)

        synonyms = term.synonyms
        assert len(synonyms) == 3

        one = synonyms[0]
        assert one.name == "Cardiovascular disease"
        assert one.category == hp.model.SynonymCategory.RELATED
        assert one.synonym_type == hp.model.SynonymType.LAYPERSON_TERM
        assert one.xrefs is None

        two = synonyms[1]
        assert two.name == "Cardiovascular abnormality"
        assert two.category == hp.model.SynonymCategory.EXACT
        assert two.synonym_type == hp.model.SynonymType.LAYPERSON_TERM
        assert two.xrefs is None

        three = synonyms[2]
        assert three.name == "Abnormality of the cardiovascular system"
        assert three.category == hp.model.SynonymCategory.EXACT
        assert three.synonym_type == hp.model.SynonymType.LAYPERSON_TERM
        assert three.xrefs is None

        assert term.xrefs == tuple(
            TermId.from_curie(curie)
            for curie in (
                "UMLS:C0243050",
                "UMLS:C0007222",
                "MSH:D018376",
                "SNOMEDCT_US:49601007",
                "MSH:D002318",
            )
        )

    def test_synonym_properties(self, toy_ontology: hpotk.Ontology):
        term = toy_ontology.get_term("HP:0001627")
        assert term is not None

        synonym = term.synonyms[7]
        assert synonym.name == "Abnormally shaped heart"
        assert synonym.category == hp.model.SynonymCategory.EXACT
        assert synonym.synonym_type == hp.model.SynonymType.LAYPERSON_TERM
        assert synonym.xrefs == [TermId.from_curie("ORCID:0000-0001-5208-3432")]


class TestLoadMaxo:

    def test_load_minimal_maxo(
        self,
        fpath_real_maxo: str,
    ):
        maxo = load_minimal_ontology(fpath_real_maxo, prefixes_of_interest={"MAXO"})

        assert maxo.version == "2024-05-24"

        # Check root
        root = maxo.graph.root
        assert root is not None
        assert root.value == "MAXO:0000001"

        # Check all MAxO terms are in the graph
        for term in maxo.terms:
            assert (
                term.identifier in maxo.graph
            ), f"{term.identifier.value} should be in the graph"

        # Check we loaded a specific number of terms
        assert len(maxo) == 1788

        # Check we have certain number of terms in the graph
        descendants = set(maxo.graph.get_descendants(root))
        assert len(descendants) == len(maxo) - 1  # -1 for the root

        # Check all terms are in the graph
        cda_curie = "MAXO:0000043"  # communicable disease avoidance
        cda_term: typing.Optional[MinimalTerm] = maxo.get_term(cda_curie)
        assert cda_term is not None

        assert cda_term.name == "communicable disease avoidance"

        ancestors = list(maxo.graph.get_ancestors(cda_term))

        assert set(anc.value for anc in ancestors) == {
            "MAXO:0000001",  # medical action
            "MAXO:0000002",  # therapeutic procedure
            "MAXO:0000151",  # therapeutic avoidance intervention
            "MAXO:0000042",  # preventable disease avoidance recommendation
        }
