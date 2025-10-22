from flowcli.node import NodeExecution

from .output import BetaOutput


class BetaNodeExecution(NodeExecution):
    output: BetaOutput = BetaOutput()
