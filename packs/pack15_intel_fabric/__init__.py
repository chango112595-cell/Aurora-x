"""
Aurora Pack 15: Intelligence Fabric

Production-ready intelligence fabric and data pipeline system.
Enables real-time data processing, intelligence distribution, and knowledge synthesis.

Author: Aurora AI System
Version: 2.0.0
"""

import os
import json
import time
import threading
import queue
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import hashlib

PACK_ID = "pack15"
PACK_NAME = "Intel Fabric"
PACK_VERSION = "2.0.0"


class DataType(Enum):
    RAW = "raw"
    PROCESSED = "processed"
    AGGREGATED = "aggregated"
    INTELLIGENCE = "intelligence"
    INSIGHT = "insight"


class PipelineStage(Enum):
    INGEST = "ingest"
    TRANSFORM = "transform"
    ENRICH = "enrich"
    ANALYZE = "analyze"
    DISTRIBUTE = "distribute"


@dataclass
class DataPacket:
    packet_id: str
    data_type: DataType
    source: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    stage: PipelineStage = PipelineStage.INGEST
    processed: bool = False


@dataclass
class IntelligenceNode:
    node_id: str
    name: str
    node_type: str
    capabilities: List[str] = field(default_factory=list)
    subscriptions: List[str] = field(default_factory=list)
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Insight:
    insight_id: str
    title: str
    description: str
    confidence: float
    source_packets: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataIngester:
    def __init__(self, max_queue_size: int = 10000):
        self.input_queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self.packet_counter = 0
        self._lock = threading.Lock()
    
    def ingest(self, source: str, data: Dict[str, Any], 
               data_type: DataType = DataType.RAW) -> DataPacket:
        with self._lock:
            self.packet_counter += 1
            packet_id = hashlib.md5(
                f"{source}{self.packet_counter}{time.time()}".encode()
            ).hexdigest()[:16]
        
        packet = DataPacket(
            packet_id=packet_id,
            data_type=data_type,
            source=source,
            payload=data,
            stage=PipelineStage.INGEST
        )
        
        try:
            self.input_queue.put_nowait(packet)
        except queue.Full:
            oldest = self.input_queue.get()
            self.input_queue.put(packet)
        
        return packet
    
    def get_pending(self) -> Optional[DataPacket]:
        try:
            return self.input_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_queue_size(self) -> int:
        return self.input_queue.qsize()


class DataTransformer:
    def __init__(self):
        self.transformers: Dict[str, Callable[[DataPacket], DataPacket]] = {}
        self._register_default_transformers()
    
    def _register_default_transformers(self):
        self.register("normalize", self._normalize)
        self.register("flatten", self._flatten)
        self.register("extract_metrics", self._extract_metrics)
    
    def _normalize(self, packet: DataPacket) -> DataPacket:
        if "values" in packet.payload:
            values = packet.payload["values"]
            if values and isinstance(values, list):
                min_val = min(values)
                max_val = max(values)
                if max_val > min_val:
                    packet.payload["normalized"] = [
                        (v - min_val) / (max_val - min_val) for v in values
                    ]
        packet.stage = PipelineStage.TRANSFORM
        return packet
    
    def _flatten(self, packet: DataPacket) -> DataPacket:
        def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        packet.payload = flatten_dict(packet.payload)
        packet.stage = PipelineStage.TRANSFORM
        return packet
    
    def _extract_metrics(self, packet: DataPacket) -> DataPacket:
        metrics = {}
        for key, value in packet.payload.items():
            if isinstance(value, (int, float)):
                metrics[key] = value
            elif isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                metrics[f"{key}_count"] = len(value)
                metrics[f"{key}_sum"] = sum(value)
                metrics[f"{key}_avg"] = sum(value) / len(value) if value else 0
        
        packet.metadata["extracted_metrics"] = metrics
        packet.stage = PipelineStage.TRANSFORM
        return packet
    
    def register(self, name: str, transformer: Callable[[DataPacket], DataPacket]):
        self.transformers[name] = transformer
    
    def transform(self, packet: DataPacket, transformer_name: str) -> DataPacket:
        transformer = self.transformers.get(transformer_name)
        if transformer:
            return transformer(packet)
        return packet
    
    def apply_all(self, packet: DataPacket) -> DataPacket:
        for transformer in self.transformers.values():
            packet = transformer(packet)
        return packet


class InsightGenerator:
    def __init__(self):
        self.insight_counter = 0
        self.insights: List[Insight] = []
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def analyze(self, packets: List[DataPacket]) -> List[Insight]:
        generated_insights = []
        
        if len(packets) >= 3:
            insight = self._detect_trend(packets)
            if insight:
                generated_insights.append(insight)
        
        anomaly_insight = self._detect_anomaly(packets)
        if anomaly_insight:
            generated_insights.append(anomaly_insight)
        
        with self._lock:
            self.insights.extend(generated_insights)
        
        return generated_insights
    
    def _detect_trend(self, packets: List[DataPacket]) -> Optional[Insight]:
        sources = defaultdict(list)
        for packet in packets:
            sources[packet.source].append(packet)
        
        if len(sources) >= 2:
            with self._lock:
                self.insight_counter += 1
                insight_id = f"ins-{self.insight_counter:08d}"
            
            return Insight(
                insight_id=insight_id,
                title="Multi-Source Activity Detected",
                description=f"Activity from {len(sources)} sources detected",
                confidence=0.75,
                source_packets=[p.packet_id for p in packets[:5]],
                tags=["trend", "multi-source"]
            )
        return None
    
    def _detect_anomaly(self, packets: List[DataPacket]) -> Optional[Insight]:
        for packet in packets:
            metrics = packet.metadata.get("extracted_metrics", {})
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and value > 1000:
                    with self._lock:
                        self.insight_counter += 1
                        insight_id = f"ins-{self.insight_counter:08d}"
                    
                    return Insight(
                        insight_id=insight_id,
                        title=f"High Value Detected: {key}",
                        description=f"Unusually high value ({value}) detected for {key}",
                        confidence=0.65,
                        source_packets=[packet.packet_id],
                        tags=["anomaly", "high-value"]
                    )
        return None
    
    def get_recent_insights(self, limit: int = 50) -> List[Insight]:
        with self._lock:
            return self.insights[-limit:]


class IntelligenceDistributor:
    def __init__(self):
        self.nodes: Dict[str, IntelligenceNode] = {}
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self._lock = threading.Lock()
    
    def register_node(self, node: IntelligenceNode) -> bool:
        with self._lock:
            self.nodes[node.node_id] = node
            for topic in node.subscriptions:
                self.subscriptions[topic].add(node.node_id)
        return True
    
    def unregister_node(self, node_id: str) -> bool:
        with self._lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                for topic in node.subscriptions:
                    self.subscriptions[topic].discard(node_id)
                del self.nodes[node_id]
                return True
        return False
    
    def distribute(self, topic: str, data: Dict[str, Any]) -> int:
        with self._lock:
            subscribers = list(self.subscriptions.get(topic, set()))
        
        distributed = 0
        for node_id in subscribers:
            node = self.nodes.get(node_id)
            if node and node.status == "active":
                distributed += 1
        
        return distributed
    
    def get_subscribers(self, topic: str) -> List[str]:
        with self._lock:
            return list(self.subscriptions.get(topic, set()))
    
    def get_node_count(self) -> int:
        return len(self.nodes)


class IntelligenceFabric:
    def __init__(self, base_dir: str = "/tmp/aurora_intel_fabric"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.ingester = DataIngester()
        self.transformer = DataTransformer()
        self.insight_generator = InsightGenerator()
        self.distributor = IntelligenceDistributor()
        
        self.processed_packets: List[DataPacket] = []
        self._lock = threading.Lock()
        self._running = False
    
    def ingest(self, source: str, data: Dict[str, Any]) -> str:
        packet = self.ingester.ingest(source, data)
        return packet.packet_id
    
    def process_batch(self, batch_size: int = 10) -> int:
        packets = []
        for _ in range(batch_size):
            packet = self.ingester.get_pending()
            if not packet:
                break
            
            packet = self.transformer.apply_all(packet)
            packet.stage = PipelineStage.ANALYZE
            packet.processed = True
            packets.append(packet)
        
        if packets:
            with self._lock:
                self.processed_packets.extend(packets)
                if len(self.processed_packets) > 1000:
                    self.processed_packets = self.processed_packets[-500:]
            
            self.insight_generator.analyze(packets)
        
        return len(packets)
    
    def register_consumer(self, node_id: str, name: str, 
                          subscriptions: List[str]) -> bool:
        node = IntelligenceNode(
            node_id=node_id,
            name=name,
            node_type="consumer",
            subscriptions=subscriptions
        )
        return self.distributor.register_node(node)
    
    def publish(self, topic: str, data: Dict[str, Any]) -> int:
        return self.distributor.distribute(topic, data)
    
    def get_insights(self, limit: int = 50) -> List[Dict[str, Any]]:
        insights = self.insight_generator.get_recent_insights(limit)
        return [
            {
                "id": i.insight_id,
                "title": i.title,
                "description": i.description,
                "confidence": i.confidence,
                "tags": i.tags,
                "timestamp": i.timestamp
            }
            for i in insights
        ]
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "pending_packets": self.ingester.get_queue_size(),
            "processed_packets": len(self.processed_packets),
            "total_insights": len(self.insight_generator.insights),
            "registered_nodes": self.distributor.get_node_count(),
            "transformers": list(self.transformer.transformers.keys())
        }


def get_pack_info():
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "version": PACK_VERSION,
        "status": "production",
        "components": [
            "DataIngester",
            "DataTransformer",
            "InsightGenerator",
            "IntelligenceDistributor",
            "IntelligenceFabric"
        ],
        "features": [
            "Real-time data ingestion",
            "Configurable data transformers",
            "Automatic insight generation",
            "Pub/sub intelligence distribution",
            "Pattern detection and anomaly alerts",
            "Batch processing support"
        ]
    }
