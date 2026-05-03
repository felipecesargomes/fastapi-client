import asyncio
import time

async def fazer_pedido_assincrono(id_pedido):
    print(f"[Async] Começando pedido {id_pedido}...")
    await asyncio.sleep(2) # Tempo em espera
    print(f"[Async] Pedido {id_pedido} pronto!")

def fazer_pedido_sincrono(id_pedido):
    print(f"[Sync] Começando pedido {id_pedido}...")
    time.sleep(2) # Tempo em espera
    print(f"[Sync] Pedido {id_pedido} pronto!")

def executar_sincrono():
    print("--- INICIANDO MODO SÍNCRONO ---")
    inicio = time.time()

    fazer_pedido_sincrono(1)
    fazer_pedido_sincrono(2)
    fazer_pedido_sincrono(3)

    fim = time.time()
    print(f"--- Tempo total Síncrono: {fim - inicio:.2f} segundos ---\n")

async def executar_assincrono():
    print("--- INICIANDO MODO ASSÍNCRONO ---")
    inicio = time.time()

    await asyncio.gather(
        fazer_pedido_assincrono(1),
        fazer_pedido_assincrono(2),
        fazer_pedido_assincrono(3),
    )

    fim = time.time()
    print(f"--- Tempo total Assíncrono: {fim - inicio:.2f} segundos ---")

if __name__ == "__main__":
    asyncio.run(executar_assincrono());