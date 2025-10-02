import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message


# ---------------- Traffic Light Agent ----------------
class TrafficLightAgent(Agent):
    class LightControlBehaviour(CyclicBehaviour):
        async def run(self):
            # Alterna entre RED e GREEN
            if not hasattr(self, "state"):
                self.state = "RED"

            if self.state == "RED":
                self.state = "GREEN"
            else:
                self.state = "RED"

            print(f"[{self.agent.name}] LIGHT: {self.state}")

            # Recebe mensagens de veículos
            msg = await self.receive(timeout=1)
            if msg:
                print(f"[{self.agent.name}] Recebi mensagem de {msg.sender}: {msg.body}")

            await asyncio.sleep(3)

    async def setup(self):
        b = self.LightControlBehaviour()
        self.add_behaviour(b)


# ---------------- Vehicle Agent ----------------
class VehicleAgent(Agent):
    class SendRequestBehaviour(OneShotBehaviour):
        async def run(self):
            msg = Message(to="trafficlight@localhost")
            msg.body = "Cheguei à interseção!"
            await self.send(msg)
            print(f"[{self.agent.name}] Mensagem enviada para Traffic Light")

    async def setup(self):
        b = self.SendRequestBehaviour()
        self.add_behaviour(b)


# ---------------- Main ----------------
async def main():
    traffic_light = TrafficLightAgent("trafficlight@localhost", "senha")
    vehicle = VehicleAgent("vehicle@localhost", "senha")

    await traffic_light.start()
    await vehicle.start()

    # Mantém os agentes rodando enquanto estão ativos
    while traffic_light.is_alive() or vehicle.is_alive():
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
