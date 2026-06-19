from fluxly.node import NodeExecution

from .output import ExtractOutput


class ExtractExecution(NodeExecution):
    output: ExtractOutput = ExtractOutput()
