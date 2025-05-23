import typing

from hpotk.constants.hpo.onset import ONSETS

from hpotk.model import TermId, Identified

def get_clinical_course_type(identifier: TermId) -> str:
    if identifier in ONSETS:
        return "onset"
    else:
        pass
