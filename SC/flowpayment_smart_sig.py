#sample_smart_sig.py
from pyteal import *
from beaker import *

"""Basic Donation Escrow"""

class delegated_signature(LogicSignature):

    one_month_time: Final[ApplicationStateValue] = ApplicationStateValue(stack_type=TealType.uint64, default=Int(Int(2629800)))
    
    Fee = Int(1000)

    
    #Only the flow receiver account can execute the payment transaction
    def evaluate():
        return And(
        Txn.type_enum() == TxnType.Payment,
        Txn.fee() <= Fee,
        Txn.receiver() == Global.current_application_address,
        Global.group_size() == Int(1),
        Txn.rekey_to() == Global.zero_address()
        )
    # Mode.Signature specifies that this is a smart signature
        return compile()

