import asyncio
from database_setup import AsyncSessionLocal
from models import Node
from sqlalchemy import select

async def check_nodes():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Node))
        nodes = result.scalars().all()
        
        print("\n=== Current Node Status ===")
        for node in nodes:
            print(f"Node: {node.hostname}")
            print(f"  ID: {node.id}")
            print(f"  Status: {node.status}")
            print(f"  Last Seen: {node.last_seen}")
            print(f"  IP: {node.ip_address}")
            print()

if __name__ == "__main__":
    asyncio.run(check_nodes())
