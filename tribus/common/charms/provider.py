"""Charm Factory

Register a set of input handlers and spawn the correct charm
implementation.
"""
from tribus.common.errors import CharmError
import os.path


def _is_bundle(filename):
    """is_bundle(filename) -> boolean"""
    return os.path.isfile(filename) and filename.endswith(".charm")


def get_charm_from_path(specification):
    """
    Given the specification of a charm (usually a pathname) map it
    to an implementation and create an instance of the proper type.
    """
    if _is_bundle(specification):
        from tribus.common.charms.bundle import CharmBundle
        return CharmBundle(specification)
    elif os.path.isdir(specification):
        from tribus.common.charms.directory import CharmDirectory
        return CharmDirectory(specification)

    raise CharmError(
        specification, "unable to process %s into a charm" % specification)
