import asyncio
from spade import agent, behaviour, message

class PingPongAgent(agent.Agent):
    class ChatBehav(behaviour.CyclicBehaviour):
        def __init__(self, partner_jid):
            super().__init__()
            self.partner_jid = partner_jid
            self.sent_first = False  # Para iniciar a conversa

        async def run(self):
            # Recebe mensagem
            msg = await self.receive(timeout=5)
            if msg:
                print(f"[{self.agent.name}] recebeu: {msg.body}")
                reply = msg.make_reply()
                reply.body = f"Eco: {msg.body}"
                await self.send(reply)
                print(f"[{self.agent.name}] respondeu: {reply.body}")
            else:
                # Se não recebeu nada, envia primeira mensagem apenas uma vez
                if not self.sent_first:
                    msg = message.Message(
                        to=self.partner_jid,
                        body=f"Olá do {self.agent.name}!"
                    )
                    await self.send(msg)
                    print(f"[{self.agent.name}] enviou: {msg.body}")
                    self.sent_first = True

    async def setup(self):
        # O JID do parceiro é passado na criação do agente
        partner_jid = self.behaviours[0].partner_jid if self.behaviours else None
        self.add_behaviour(self.ChatBehav(partner_jid))
        print(f"Agente {self.name} iniciado.")


async def main():
    # Usuários já registrados no Prosody:
    # docker exec -it prosody prosodyctl register agent1 localhost senha123
    # docker exec -it prosody prosodyctl register agent2 localhost senha456

    # Criando agentes
    agent1 = PingPongAgent("agent1@localhost", "senha123")
    agent2 = PingPongAgent("agent2@localhost", "senha456")

    # Configura parceiros
    beh1 = agent1.ChatBehav("agent2@localhost")
    beh2 = agent2.ChatBehav("agent1@localhost")
    agent1.add_behaviour(beh1)
    agent2.add_behaviour(beh2)

    # Inicia agentes
    await agent1.start()
    await agent2.start()

    print("Ping-pong iniciado! Ctrl+C para parar.")

    try:
        # Loop infinito
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Parando agentes...")
        await agent1.stop()
        await agent2.stop()

if __name__ == "__main__":
    asyncio.run(main())
