from beaker import *
from pyteal import *


class App(Application):

    dico = ApplicationStateValue(stack_type=bytes())

    @create
    def create(self):
        return Approve()

    @external
    def foo(self, *, output: abi.String):
        return output.set(Bytes("Hello World"))

    @external 
    def create_flow(self, sender: abi.Address, receiver:  abi.Address, flow: abi.Int, *):



app = App(version=8)
app.dump()

creator = sandbox.kmd.get_accounts()[0]

app_client = client.application_client.ApplicationClient(
    client=sandbox.clients.get_algod_client(),
    app=app,
    sender=creator.address,
    signer=creator.signer,
)

app_client.create()

print(app_client.call(App.foo).return_value)