"""
Heartbeat Monitor - Background task to detect offline nodes
"""

import asyncio
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import models
from db import AsyncSessionLocal
from websocket import manager


class HeartbeatMonitor:
    """Monitors node heartbeats and marks nodes offline if no heartbeat received."""
    
    def __init__(self, check_interval: int = 30, timeout: int = 90):
        """
        Args:
            check_interval: How often to check for stale nodes (seconds)
            timeout: How long without heartbeat before marking offline (seconds)
        """
        self.check_interval = check_interval
        self.timeout = timeout
        self.running = False
        self.task = None
    
    async def start(self):
        """Start the heartbeat monitoring task."""
        if self.running:
            logger.warning("HeartbeatMonitor is already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._monitor_loop())
        logger.info(f"HeartbeatMonitor started: check_interval={self.check_interval}s, timeout={self.timeout}s")
    
    async def stop(self):
        """Stop the heartbeat monitoring task."""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("HeartbeatMonitor stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                await self._check_stale_nodes()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_stale_nodes(self):
        """Check for nodes that haven't sent heartbeats recently."""
        async with AsyncSessionLocal() as session:
            try:
                # Calculate the cutoff time
                cutoff_time = datetime.utcnow() - timedelta(seconds=self.timeout)
                
                # Find all nodes that are marked online but haven't updated recently
                stmt = select(models.Node).where(
                    models.Node.status == "online",
                    models.Node.last_seen < cutoff_time
                )
                result = await session.execute(stmt)
                stale_nodes = result.scalars().all()
                
                if stale_nodes:
                    logger.info(f"Found {len(stale_nodes)} stale nodes")
                    
                    for node in stale_nodes:
                        # Mark as offline
                        node.status = "offline"
                        logger.info(f"Node '{node.hostname}' marked offline (last seen: {node.last_seen})")
                        
                        # Broadcast status change via WebSocket
                        await manager.broadcast({
                            "type": "node_updated",
                            "data": {
                                "id": node.id,
                                "hostname": node.hostname,
                                "ip_address": node.ip_address,
                                "group": node.group,
                                "status": "offline",
                                "last_seen": node.last_seen.isoformat() if node.last_seen else None,
                            }
                        })
                    
                    await session.commit()
                    logger.info(f"Marked {len(stale_nodes)} nodes as offline")
                
            except Exception as e:
                logger.error(f"Error checking stale nodes: {e}")
                await session.rollback()


# Global instance
heartbeat_monitor = HeartbeatMonitor(check_interval=30, timeout=90)
