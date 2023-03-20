#!/usr/bin/env python3

from beaker import *

from pyteal import *
from beaker.lib.storage.mapping import *
from beaker.lib.storage._list import *
import os
import json
from typing import (Final, Literal) 

from beaker.client import ApplicationClient, LogicException
from beaker.sandbox import get_algod_client, get_accounts
from beaker import (
    Application,
    ApplicationStateValue,
    AccountStateValue,
    create,
    opt_in,
    external,
)
from pyteal import abi, TealType, Bytes, Int, Txn


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

    
    senders_to_receivers = Mapping(abi.Address, abi.StaticArray[abi.Address, Literal[999]], Bytes("stor")),
    @external(read_only = True)
    def read_senders_to_receivers(self, sender: abi.Account, *, output: abi.StaticArray[abi.Address, Literal[999]]):
        return self.senders_to_receivers[sender.address()].get()

    receivers_to_senders = Mapping(abi.Address, abi.StaticArray[abi.Address, Literal[999]], Bytes("rtos")),
    @external(read_only = True)
    def read_receivers_to_senders(self, receiver: abi.Account, *, output: abi.StaticArray[abi.Address, Literal[999]]):
        return self.senders_to_receivers[sender.address()].get()

    @opt_in
    def opt_in(self):
        return self.initialize_account_state()

    @internal(TealType.none)
    def pay_escrow(self, amount: abi.Uint64):
        return InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: Global.current_application_address(),
            TxnField.amount: amount.get(),
            TxnField.fee: Int(0)
        })
    
    @external
    def fund(self, payment: abi.PaymentTransaction):
        return Seq(
            Assert(Txn.sender() == payment.get().sender()),
            self.pay_escrow(payment.get().amount()),
            self.accounts_balance[Txn.sender()].set(Add(self.accounts_balance[Txn.sender()], payment.get().amount()))

        )

    @internal
    def add_receiver_to_receivers(self, sender: abi.Account, receiver: abi.Account):
        return Seq(
            (receivers := Concat(abi.Address(self.senders_to_receivers[sender.address()].get(), receiver.address()))),
            self.senders_to_receivers[sender.address()].set(receivers)
        )

    @internal
    def delete_receiver_to_receivers(self, sender: abi.Account, receiver: abi.Account):
        return Seq(
            (receivers := Concat(abi.Address(self.senders_to_receivers[sender.address()].get(), receiver.address()))),
            self.senders_to_receivers[sender.address()].set(receivers)
        )

    @internal
    def add_sender_to_senders(self, sender: abi.Account, receiver: abi.Account):
        return Seq(
            (senders := Concat(abi.Address(self.receivers_to_senders[receiver.address()].get(), sender.address()))),
            self.receivers_to_senders[receiver.address()].set(senders)
        )

    # c'est que le sender qui create
    @external
    def create_flow(self, receiver: abi.Account, flow_rate: abi.Uint64): #, axfer: abi.AssetTransferTransaction)
        return Seq(

            Assert(Txn.sender() != receiver.get()),
            
            # checking if the balance of the account is > to a one_month_time payment
            Assert(self.accounts_balance[Txn.sender()] > Mul(self.one_month_time, flow_rate.get())),

            Assert(self.Bytes(Concat(Txn.sender().address(), receiver.address())).exists() == False), # il faut pas que des méchants puissent créer des boxes de leur côté (=> vérif box_array)
            
            self.add_receiver_to_receivers(Txn.sender(), receiver.get()),
            self.add_sender_to_senders(Txn.sender(), receiver.get()),

            App.box_put(Bytes(Concat(Txn.sender().address(), receiver.address())), Bytes(Concat(Itob(flow_rate.get()), Itob(Global.latest_timestamp()))))

        )

    @internal(TealType.bytes)
    def read_flow_rate(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Bytes(Concat(sender.address(), receiver.address()), Int(0), Int(8))))

    @internal(TealType.bytes)
    def read_timestamp(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Bytes(Concat(sender.address(), receiver.address()), Int(8), Int(8))))
    
    """
    @internal
    def read_box(self, box_name: Bytes, *, output: Bytes):
        return output.set(App.box_get(Bytes(box_name.get())).value())
    """
    
    @external(read_only=True) 
    def calculate_due_payment(self, sender: abi.Account, receiver: abi.Account, *, output: abi.Uint64):
        return output.set(Mul(Btoi(Bytes(read_flow_rate(sender.get(), receiver.get()))), Int(Minus(Global.latest_timestamp(), Btoi(read_timestamp(sender.get(), receiver.get()))))))


    """
    # c'est que le sender qui update
    @external
    def update_flow(self, receiver: abi.Account, new_flow_rate: abi.Uint64):
        return Seq(

            Assert(Txn.sender() != receiver.get()),
            
            # checking if the balance of the account is > to a one_month_time payment
            Assert(self.accounts_balance[Txn.sender()] > Mul(self.one_month_time, new_flow_rate.get())),

            Assert(self.Bytes(Concat(Txn.sender().address(), receiver.address())).exists()), # il faut pas que des méchants puissent créer des boxes de leur côté (=> vérif box_array)
            

            # le payment de calculate_due_payment  sera en atomic transaction avec le update_flow

            App.box_replace(Bytes(Concat(Txn.sender().address(), receiver.address())), Int(0), Bytes(Concat(Itob(new_flow_rate.get()), Itob(Global.latest_timestamp())))),
           

        )
    """

    @external
    def claim_flow(self, sender: abi.Account):
        return Seq(
            Assert(self.Bytes(Concat(sender.address(), Txn.sender().address())).exists()),

            self.accounts_balance[Txn.sender()].set(Minus(self.accounts_balance[sender.get()], calculate_due_payment(sender.get(), Txn.sender()))),

            InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.sender: Global.current_application_address(),
            TxnField.receiver: Txn.sender(),
            TxnField.amount: calculate_due_payment(sender.get(), Txn.sender()),
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
            TxnField.receiver: APP_CREATOR,
            TxnField.amount: Int(0),
            TxnField.close_remainder_to: APP_CREATOR
        })


def demo():

    accts = get_accounts()

    acct = accts.pop()

    client = get_algod_client()

    app = FlowEscrow()

    app_client = ApplicationClient(client, app, signer=acct.signer)
    app_id, app_address, transaction_id = app_client.create()
    print(
        f"DEPLOYED: App ID: {app_id} Address: {app_address} Transaction ID: {transaction_id}"
    )

    app_client.opt_in()
    print("Opted in")

    """
    app_client.call(StateExample.set_account_state_val, v=123)
    result = app_client.call(StateExample.get_account_state_val)
    print(f"Set/get acct state result: {result.return_value}")

    app_client.call(StateExample.set_dynamic_account_state_val, k=123, v="stuff")
    result = app_client.call(StateExample.get_dynamic_account_state_val, k=123)
    print(f"Set/get dynamic acct state result: {result.return_value}")

    try:
        app_client.call(StateExample.set_app_state_val, v="Expect fail")
    except LogicException as e:
        print(f"Task failed successfully: {e}")
        result = app_client.call(StateExample.get_app_state_val)
        print(f"Set/get app state result: {result.return_value}")

    app_client.call(StateExample.set_dynamic_app_state_val, k=15, v=123)
    result = app_client.call(StateExample.get_dynamic_app_state_val, k=15)
    print(f"Set/get dynamic app state result: {result.return_value}")
    """

if __name__ == "__main__":
    demo()

"""
if __name__ == "__main__":

    app = FlowEscrow(version=8)

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