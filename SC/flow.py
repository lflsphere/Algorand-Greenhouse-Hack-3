#!/usr/bin/env python3
from pyteal import *
from beaker import *
import os
import json
from typing import Final

APP_CREATOR = Seq(creator := AppParam.creator(Int(0)), creator.value())

class Flow(Application):

    """
    receivers: Final[AccountStateValue] = AccountStateValue(
        stack_type = TealType.uint64,
        default = Int(1),
        descr = "An int stored for each account that opts in",
        static = False,
    )
    receivers: Final[AccountStateValue] = AccountStateValue(stack_type=abi.DynamicArray[TealType.address], default=Bytes(""))
    """ 

    # Global State
    # - durée d'un mois en secondes (pour 1 an = 365,25 j et 12 mois dans 1 an)
    one_month_time: Final[ApplicationStateValue] = ApplicationStateValue(stack_type=TealType.uint64, default=Int(Int(2629800)))


    # Create Application
    @create
    def create(self):
        return self.initialize_application_state()

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



    # c'est que le sender qui create
    @external
    def create_flow(self, sender: abi.Account, receiver: abi.Account, flowRate: abi.Uint64): #, axfer: abi.AssetTransferTransaction)
        return Seq(

            # vérifier que la SS a été créée ou pas (en fait c'est peut être pas très grave)
            Assert(App.box_create(Bytes(Concat(sender.address(), receiver.address())), Int(24))), # il faut pas que des méchants puissent créer des boxes de leur côté (=> vérif box_array)
            
            first_month = Int(Mul(flowRate, self.one_month_time.get())), 
            # il va sans doute falloir d'abord faire payer le first_month puis créer le flow (cf. comment ligne 62) et donc verifier dans le create que le first month a été créé.
            self.pay_by_tx_sender(Global.current_application_address, first_month), # receiver = smart contract ou utiliser la SS ici plutôt

            App.box_put(Bytes(Concat(sender.address(), receiver.address())), Bytes(Concat(Itob(flowRate), Itob(Global.latest_timestamp), Itob(first_month))))
            
        )

    @external(read_only = True)
    def read_flow_rate(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Bytes(Concat(sender.address(), receiver.address()), Int(0), Int(8))))

    @external(read_only = True)
    def read_timestamp(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Bytes(Concat(sender.address(), receiver.address()), Int(8), Int(8))))
    
    @external(read_only = True)
    def read_first_month(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Bytes(Concat(sender.address(), receiver.address()), Int(16), Int(8))))
    
    """
    on n'utilise plus de zone tampon
    @external(read_only = True)
    def read_former_payments(self, sender: abi.Account, receiver: abi.Account, *, output: Bytes): # on ne vérifie pas que la box existe
        return output.set(App.box_extract(Bytes(Concat(sender.address(), receiver.address()), Int(17), Int(8))))
    """

    # c'est que le sender qui update
    @external
    def update_flow(self, sender: abi.Account, receiver: abi.Account, new_flowRate: abi.Uint64, axfer: abi.AssetTransferTransaction):
        return Seq(

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

        
            former_flow_rate = Bytes(read_flow_rate(sender, receiver)),
            former_timestamp = Bytes(read_timestamp(sender, receiver)),
            former_payments = Bytes(read_former_payments(sender, receiver)),
            due_payment = BytesMul(Bytes("base16", former_flow_rate), Bytes("base16", former_timestamp)),
            # payment_so_far = BytesAdd(Bytes("base16", last_payment), Bytes("base16", former_payments)), plus de zone tampon

            self.pay_by_tx_sender(receiver = Global.current_application_address, due_payment), # receiver = smart contract ou utiliser la SS ici plutôt


            App.box_replace(Bytes(Concat(sender.address(), receiver.address())), Int(0), Bytes(Concat(Itob(new_flowRate), Itob(Global.latest_timestamp))))

           

        )

    @external
    def claim(self, sender: abi.Account, receiver: abi.Account):
        # faire l'appel à la SS 
        # faire un claim de la somme latest_payment avec la SS comme ça pas besoin de zone tampon ?


    


    
    
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
    app = Auction(version=8)

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