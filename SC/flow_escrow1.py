

#!/usr/bin/env python3

from beaker import *
from pyteal import *
from beaker.lib.storage.mapping import *
from beaker.lib.storage._list import *
import os
import json
from typing import (Final, Literal) 

# APP_CREATOR = AppParam.creator.value()

class FlowEscrow(Application):



    # Global State
    # - durée d'un mois en secondes (pour 1 an = 365,25 j et 12 mois dans 1 an)
    one_month_time: Final[ApplicationStateValue] = ApplicationStateValue(stack_type=TealType.uint64, default=Int(2629800))

    # Local State
    # paires (tokens, balance) pour chaque account qui aura opt-in
    accounts_balance : Final[AccountStateValue] = AccountStateValue(
        stack_type = TealType.uint64,
        default = Int(0),
        descr = "the amt of Algos each account has",
    )



    # Create Application
    @create
    def create(self):
        return Seq(
            self.initialize_application_state(),
        )

    
    senders_to_receivers = Mapping(abi.Address, abi.StaticArray[abi.Address, Literal[999]], Bytes("stor"))
    receivers_to_senders = Mapping(abi.Address, abi.StaticArray[abi.Address, Literal[999]], Bytes("rtos"))

    """
    @external(read_only = True)
    def read_senders_to_receivers(self, sender: abi.Account, *, output: abi.StaticArray[abi.Address, Literal[999]]):
        return self.senders_to_receivers[sender.address()].get()

    @external(read_only = True)
    def read_receivers_to_senders(self, receiver: abi.Account, *, output: abi.StaticArray[abi.Address, Literal[999]]):
        return self.senders_to_receivers[sender.address()].get()
    """

    @opt_in
    def opt_in(self):
        return self.initialize_account_state()

    
    
    @external()
    def fund_escrow(self, amount: abi.Uint64):
        return Seq(
            Assert(self.accounts_balance[Txn.sender()].exists()),
            InnerTxnBuilder.Execute({
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Global.current_application_address(),
                    TxnField.amount: amount.get(),
                    TxnField.fee: Int(0)
            }),
            self.accounts_balance[Txn.sender()].set(Add(self.accounts_balance[Txn.sender()], amount.get()))
            
        )

    @internal(TealType.none)
    def add_receiver_to_receivers(self, sender: abi.Address, receiver: abi.Address):
        return Seq(
            (receivers := Concat(abi.Address(self.senders_to_receivers[sender.get()].get(), receiver.get()))),
            self.senders_to_receivers[sender.get()].set(receivers)
        )

    

    @internal(TealType.none)
    def add_sender_to_senders(self, sender: abi.Address, receiver: abi.Address):
        return Seq(
            (senders := Concat(abi.Address(self.receivers_to_senders[receiver.get()].get(), sender.get()))),
            self.receivers_to_senders[receiver.get()].set(senders)
        )

    # c'est que le sender qui create ( #, axfer: abi.AssetTransferTransaction))
    @external()
    def create_flow(self, sender: abi.Account(), receiver: abi.Account, flow_rate: abi.Uint64):
        return Seq(

            Assert(Txn.sender() == sender.address()),
            # checking if the balance of the account is > to a one_month_time payment
            Assert(self.accounts_balance[Txn.sender()] > Mul(self.one_month_time, flow_rate.get())),

            Assert(App.box_get(Concat(sender.address(), receiver.address())).hasValue()),
            
            self.add_receiver_to_receivers(sender, receiver.address()),
            self.add_sender_to_senders(sender, receiver.address()),

            App.box_put(Bytes(Concat(sender.address(), receiver.address())), Bytes(Concat(Itob(flow_rate.get()), Itob(Global.latest_timestamp()))))

        )

    #@internal(TealType.bytes)
    def read_flow_rate(self, sender: abi.Address(), receiver: abi.Address(), *, output: abi.Uint64): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Btoi(Bytes(Concat(sender.get(), receiver.get()), Int(0), Int(8)))))

    #@internal(TealType.bytes)
    def read_timestamp(self, sender: abi.Account, receiver: abi.Account, *, output: abi.Uint64): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Btoi(Bytes(Concat(sender.get(), receiver.get()), Int(8), Int(8)))))
    
    """
    @internal
    def read_box(self, box_name: Bytes, *, output: Bytes):
        return output.set(App.box_get(Bytes(box_name.get())).value())
    """
    
    @internal 
    def calculate_due_payment(self, sender: abi.Address, receiver: abi.Address(), *, output: abi.Uint64):
        return output.set(Mul(read_flow_rate(sender.get(), receiver.get()))), Int(Minus(Global.latest_timestamp(), read_timestamp(sender.get(), receiver.get())))




    @external
    def claim_flow(self, sender: abi.Account):
        return Seq(
            Assert(self.Bytes(Concat(sender.address(), Txn.sender())).exists()),

            self.accounts_balance[Txn.sender()].set(Minus(self.accounts_balance[sender.get()], calculate_due_payment(sender.address(), Txn.sender()))),

            InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.sender: Global.current_application_address(),
            TxnField.receiver: Txn.sender(),
            TxnField.amount: calculate_due_payment(sender.address(), Txn.sender()),
            TxnField.fee: Int(0)
            })
        )
    

    """
    @external
    def delete_flow(self, sender: abi.Account, receiver: abi.Account):
        return Seq(
            Assert(Or(Txn.sender() == sender.get(), Txn.sender() == receiver.get())),
            Assert(App.box_delete(Bytes(Concat(sender.address(), receiver.address())))),
            self.senders_to_receivers[sender.get()].
        )
    """

    # Delete app
    # Send MBR funds to creator and delete app
    @delete(authorize=Authorize.only(Global.creator_address()))
    def delete():
        return InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.fee: Int(0), 
            TxnField.receiver: Global.creator_address(),
            TxnField.amount: Int(0),
            TxnField.close_remainder_to: Global.creator_address()
        })




    """
    app = FlowEscrow()

    if os.path.exists("approval.teal"):
        os.remove("approval.teal")

    if os.path.exists("clear.teal"):
        os.remove("clear.teal")

    if os.path.exists("abi.json"):
        os.remove("abi.json")

    if os.path.exists("app_spec.json"):
        os.remove("app_spec.json")

    with open("approval.teal", "w") as f:
        f.write(app.approval_program)

    with open("clear.teal", "w") as f:
        f.write(app.clear_program)

    with open("abi.json", "w") as f:
        f.write(json.dumps(app.contract.dictify(), indent=4))

    with open("app_spec.json", "w") as f:
        f.write(json.dumps(app.application_spec(), indent=4))

    """


