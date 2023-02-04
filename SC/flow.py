#!/usr/bin/env python3
from pyteal import *
from beaker import *
import os
import json
from typing import Final

APP_CREATOR = AppParam.creator.value()

class Flow(Application):

    """
    receivers: Final[AccountStateValue] = AccountStateValue(
        stack_type = TealType.uint64,
        default = Int(1),$
        descr = "An int stored for each account that opts in",
        static = False,
    )
    receivers: Final[AccountStateValue] = AccountStateValue(stack_type=abi.DynamicArray[TealType.address], default=Bytes(""))
    """ 

    # Global State
    # - durée d'un mois en secondes (pour 1 an = 365,25 j et 12 mois dans 1 an)
    one_month_time: Final[ApplicationStateValue] = ApplicationStateValue(stack_type=TealType.uint64, default=Int(Int(2629800)))

    class DelegatedSignature(LogicSignature):
        
        Fee = Int(1000)

        def __init__(self, version: int, sender: abi.Account, receiver: abi.Account):
            self.sender = sender.get()
            self.receiver = receiver.get()
        LogicSignature.__init__(self, MAX_TEAL_VERSION)

        #Only the receiver account can execute the payment transaction
        def evaluate(self):
            return And(
            Txn.type_enum() == TxnType.Payment,
            Txn.fee() <= Fee,
            Txn.amount == calculate_due_payment(self.sender, self.receiver), # the receiver has to  withdraw exactly the pending flow. For BtoC usecases, it is up to the B to withdraw when it suits best the C; otherwise the C will be likely to change for another B.
            Txn.sender() == self.receiver.address(),
            Global.group_size() == Int(1),
            Txn.rekey_to() == Global.zero_address()
            )
        # return compile() Spécifique au smart signature (classe LogicSignature) PASBESOINNORMALEMENT



    


    # Create Application
    @create
    def create(self):
        return Seq(
            self.initialize_application_state(),
            self.initialize_account_state()
        )            

    """
    # Opt app into ASA
    @external(authorize=Authorize.only(APP_CREATOR))
    def opt_into_asset(self, asset: abi.Asset):
        return Seq(
            Assert(self.asa == Int(0)),
            self.asa.set(asset.asset_id()),
            InnerTxnBuilder.Execute({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.fee: Int(0),
                TxnField.asset_receiver: Global.current_application_address(),
                TxnField.xfer_asset: asset.asset_id(),
                TxnField.asset_amount: Int(0)
            })
        )
    """

    @internal(TealType.none)
    def pay(self, receiver, amount):
        return InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: receiver,
            TxnField.amount: amount,
            TxnField.fee: Int(0)
        })

    @internal(TealType.none)
    def pay_by_tx_sender(self, receiver, amount):
        return InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.sender : Txn.sender(), # devrait ne pas marcher car si le sender doit être le SC (cf. dev portal) MAIS on utilise la SS pour que le SC puisse on-behalf du sender puisse payer le receiver
            TxnField.receiver: receiver,
            TxnField.amount: amount,
            TxnField.fee: Int(0)
        })

    max_list = List(abi.Address, 1000)
    senders_to_receivers = Mapping(abi.Address, max_list)
    receivers_to_senders = Mapping(abi.Address, max_list)
    flows = Mapping(abi.)

    # c'est que le sender qui create
    @external
    def create_flow(self, sender: abi.Account, receiver: abi.Account, flowRate: abi.Uint64): #, axfer: abi.AssetTransferTransaction)
        return Seq(

            Assert(Txn.sender() == sender.address()),

            # vérifier que la SS a été créée ou pas (en fait c'est peut être pas très grave)

            Assert(self.Bytes(Concat(sender.address(), receiver.address())).exists()), # il faut pas que des méchants puissent créer des boxes de leur côté (=> vérif box_array)
            
            
            # le payment du first month sera en atomic transaction avec le create_flow

            App.box_put(Bytes(Concat(sender.address(), receiver.address())), Bytes(Concat(Itob(flowRate.get()), Itob(Global.latest_timestamp()), Itob(Int(Mul(flowRate.get(), self.one_month_time.get()))), Bytes(LSigPrecompile(self.DelegatedSignature(MAX_TEAL_VERSION, sender.get(), receiver.get())))))),
            self.senders_to_receivers[sender.address()].set(max_list[receiver.address()),
            self.receivers_to_senders[receiver.address()].set(sender.address())
        )

    @internal
    def read_flow_rate(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Bytes(Concat(sender.address(), receiver.address()), Int(0), Int(8))))

    @internal
    def read_timestamp(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Bytes(Concat(sender.address(), receiver.address()), Int(8), Int(8))))
    
    @internal
    def read_first_month(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Bytes(Concat(sender.address(), receiver.address()), Int(16), Int(8))))
    
    @internal
    def read_box(self, box_name: Bytes, *, output: Bytes):
        return output.set(App.box_get(Bytes(box_name.get())).value())


    """
    on n'utilise plus de zone tampon
    @external(read_only = True)
    def read_former_payments(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Bytes(Concat(sender.address(), receiver.address()), Int(17), Int(8))))
    """

    @external(read_only=True) 
    def calculate_due_payment(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes):
        return output.set(BytesMul(Bytes("base16", Bytes(read_flow_rate(sender.get(), receiver.get()))), Bytes("base16", Bytes(read_timestamp(sender.get(), receiver.get())))))

    # c'est que le sender qui update
    @external
    def update_flow(self, sender: abi.Account, receiver: abi.Account, new_flowRate: abi.Uint64, axfer: abi.AssetTransferTransaction):
        return Seq(
            
            Assert(Txn.sender() == sender.address()),

            # le payment de calculate_due_payment  sera en atomic transaction avec le update_flow

            App.box_replace(Bytes(Concat(sender.address(), receiver.address())), Int(0), Bytes(Concat(Itob(new_flowRate.get()), Itob(Global.latest_timestamp())))),




            """
            self.asa_amount.set(axfer.get().asset_amount()),
            self.auction_end.set(length.get() + Global.latest_timestamp()),
            self.highest_bid.set(starting_price.get())
           

           
            Assert(self.auction_end.get() == Int(0)),
            Assert(axfer.get().asset_receiver() == Global.current_application_address()),
            Assert(axfer.get().xfer_asset() == self.asa.get()),

            Assert(App.box_create(Bytes(Concat(sender.address(), receiver.address()), Int(64)))),
        
            box_content := App.box_get(Bytes(Concat(sender.address(), receiver.address()))),
            Assert(box_content.hasValue()),
            """
           

        )

    @internal()
    def sender_enough_algos(self, amount: abi.Uint64):
        return If(Txn.sender.balance.get() > amount, claim())
    
    


    
    
    """
    # Bid
    # Place a new bid and return previous bid
    @external
    def bid(self, payment: abi.PaymentTransaction, previous_bidder: abi.Account):
        return Seq(
            Assert(Global.latest_timestamp() < self.auction_end.get()),
            Assert(payment.get().amount() > self.highest_bid.get()),
            Assert(Txn.sender() == payment.get().sender()),
            Assert(payment.get().receiver() == Global.current_application_address()),
            If(
                self.highest_bidder.get() != Bytes(""),
                Seq(
                    Assert(self.highest_bidder.get() == previous_bidder.address()),
                    self.pay(self.highest_bidder.get(), self.highest_bid.get())
                )
            ),
            self.highest_bid.set(payment.get().amount()),
            self.highest_bidder.set(payment.get().sender())
        )

    # Claim bid
    # Let's the auctioner claim the highest bid once the auction has ended
    @external
    def claim_bid(self):
        return Seq(
            Assert(Global.latest_timestamp() > self.auction_end.get()),
            self.pay(APP_CREATOR, self.highest_bid.get())
        )

    # Claim asset
    # Let's the highest bidder claim the asset once the auction has ended
    @external
    def claim_asset(self, asset: abi.Asset, creator: abi.Account):
        return Seq(
            Assert(Global.latest_timestamp() > self.auction_end.get()),
            Assert(creator.address() == APP_CREATOR),
            Assert(asset.asset_id() == self.asa.get()),
            InnerTxnBuilder.Execute({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.fee: Int(0),
                TxnField.xfer_asset: asset.asset_id(),
                TxnField.asset_amount: self.asa_amount.get(),
                TxnField.asset_receiver: self.highest_bidder.get(),
                TxnField.asset_close_to: APP_CREATOR
            })
        )
    """

    # Delete app
    # Send MBR funds to creator and delete app
    @delete
    def delete():
        return InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.fee: Int(0), 
            TxnField.receiver: APP_CREATOR,
            TxnField.amount: Int(0),
            TxnField.close_remainder_to: APP_CREATOR
        })



if __name__ == "__main__":

    app = Flow()

    if os.path.exists("approval.teal"):
        os.remove("approval.teal")

    if os.path.exists("approval.teal"):
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