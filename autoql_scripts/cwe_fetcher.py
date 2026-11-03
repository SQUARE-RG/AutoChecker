#!/usr/bin/env python3
import requests
import time
import logging
import sys
import chromadb
from typing import List, Dict, Any, Set, Optional
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import tempfile
import os
from datetime import datetime
import concurrent.futures
import threading
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import get_chroma_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CWEFetcher:
    """Fetcher for CWE data with ChromaDB storage and hierarchical relationship mapping."""
    
    def __init__(self, max_workers: int = 4):
        """
        Args:
            max_workers: Maximum number of concurrent workers
        """
        # Setup ChromaDB client using shared HTTP client
        self.chroma_client = get_chroma_client()
        self.chroma_lock = threading.Lock()
        
        # Processing settings
        self.max_workers = max_workers
        
        # CWE data URLs
        self.cwe_xml_url = "https://cwe.mitre.org/data/xml/cwec_latest.xml.zip"
        self.cwe_schema_url = "https://cwe.mitre.org/data/xsd/cwe_schema_latest.xsd"
        
        # Data storage
        self.weaknesses = {}
        self.categories = {}
        self.views = {}
        self.relationships = []
        
        # Progress tracking
        self.progress = {
            'total_items': 0,
            'processed': 0,
            'start_time': None
        }
    
    def download_cwe_data(self) -> str:
        """Download and extract CWE XML data."""
        logger.info("Downloading CWE XML data...")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "cwec_latest.xml.zip"
            
            # Download ZIP file
            response = requests.get(self.cwe_xml_url, timeout=300)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extract XML file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the XML file
            xml_files = list(Path(temp_dir).glob("*.xml"))
            if not xml_files:
                raise FileNotFoundError("No XML file found in downloaded ZIP")
            
            xml_path = xml_files[0]
            logger.info(f"Downloaded and extracted: {xml_path.name}")
            
            # Read XML content
            with open(xml_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def parse_cwe_xml(self, xml_content: str) -> None:
        """Parse CWE XML data and extract weaknesses, categories, and relationships."""
        logger.info("Parsing CWE XML data...")
        
        root = ET.fromstring(xml_content)
        
        # Define namespace (updated to match actual XML)
        ns = {'cwe': 'http://cwe.mitre.org/cwe-7'}
        
        # Parse weaknesses (they are under Weaknesses container)
        weaknesses_container = root.find('cwe:Weaknesses', ns)
        if weaknesses_container is not None:
            weaknesses = weaknesses_container.findall('cwe:Weakness', ns)
            for weakness in weaknesses:
                self._parse_weakness(weakness, ns)
        
        # Parse categories (they are under Categories container)
        categories_container = root.find('cwe:Categories', ns)
        if categories_container is not None:
            categories = categories_container.findall('cwe:Category', ns)
            for category in categories:
                self._parse_category(category, ns)
        
        # Parse views (they are under Views container)
        views_container = root.find('cwe:Views', ns)
        if views_container is not None:
            views = views_container.findall('cwe:View', ns)
            for view in views:
                self._parse_view(view, ns)
        
        # Parse relationships
        self._extract_relationships(root, ns)
        
        total_items = len(self.weaknesses) + len(self.categories) + len(self.views)
        self.progress['total_items'] = total_items
        
        logger.info(f"Parsed {len(self.weaknesses)} weaknesses, {len(self.categories)} categories, {len(self.views)} views")
        logger.info(f"Found {len(self.relationships)} relationships")
    
    def _parse_weakness(self, weakness_elem, ns: dict) -> None:
        """Parse a single weakness element."""
        weakness_id = weakness_elem.get('ID')
        if not weakness_id:
            return
        
        weakness_data = {
            'id': weakness_id,
            'type': 'weakness',
            'name': weakness_elem.get('Name', ''),
            'abstraction': weakness_elem.get('Abstraction', ''),
            'structure': weakness_elem.get('Structure', ''),
            'status': weakness_elem.get('Status', ''),
        }
        
        # Extract description
        desc_elem = weakness_elem.find('.//cwe:Description', ns)
        if desc_elem is not None:
            weakness_data['description'] = ' '.join(desc_elem.itertext()).strip()

        # Extract extended description
        ext_desc_elem = weakness_elem.find('.//cwe:Extended_Description', ns)
        if ext_desc_elem is not None:
            weakness_data['extended_description'] = ' '.join(ext_desc_elem.itertext()).strip()
        
        # Extract likelihood of exploit
        likelihood_elem = weakness_elem.find('.//cwe:Likelihood_Of_Exploit', ns)
        if likelihood_elem is not None:
            weakness_data['likelihood_of_exploit'] = likelihood_elem.text or ''
        
        # Extract common consequences
        consequences = []
        for consequence in weakness_elem.findall('.//cwe:Consequence', ns):
            consequence_data = {}
            scope_elem = consequence.find('.//cwe:Scope', ns)
            if scope_elem is not None:
                consequence_data['scope'] = scope_elem.text
            
            impact_elem = consequence.find('.//cwe:Impact', ns)
            if impact_elem is not None:
                consequence_data['impact'] = impact_elem.text
            
            note_elem = consequence.find('.//cwe:Note', ns)
            if note_elem is not None:
                consequence_data['note'] = ' '.join(note_elem.itertext()).strip()
            
            if consequence_data:
                consequences.append(consequence_data)
        
        weakness_data['consequences'] = consequences
        
        # Extract potential mitigations
        mitigations = []
        for mitigation in weakness_elem.findall('.//cwe:Mitigation', ns):
            mitigation_data = {}
            phase_elem = mitigation.find('.//cwe:Phase', ns)
            if phase_elem is not None:
                mitigation_data['phase'] = phase_elem.text
            
            description_elem = mitigation.find('.//cwe:Description', ns)
            if description_elem is not None:
                text = ' '.join(description_elem.itertext()).strip()
                if text:
                    mitigation_data['description'] = text
            
            if mitigation_data:
                mitigations.append(mitigation_data)
        
        weakness_data['mitigations'] = mitigations
        
        self.weaknesses[weakness_id] = weakness_data
    
    def _parse_category(self, category_elem, ns: dict) -> None:
        """Parse a single category element."""
        category_id = category_elem.get('ID')
        if not category_id:
            return
        
        category_data = {
            'id': category_id,
            'type': 'category',
            'name': category_elem.get('Name', ''),
            'status': category_elem.get('Status', ''),
        }
        
        # Extract summary
        summary_elem = category_elem.find('.//cwe:Summary', ns)
        if summary_elem is not None:
            category_data['summary'] = summary_elem.text or ''
        
        self.categories[category_id] = category_data
    
    def _parse_view(self, view_elem, ns: dict) -> None:
        """Parse a single view element."""
        view_id = view_elem.get('ID')
        if not view_id:
            return
        
        view_data = {
            'id': view_id,
            'type': 'view',
            'name': view_elem.get('Name', ''),
            'type_attr': view_elem.get('Type', ''),
            'status': view_elem.get('Status', ''),
        }
        
        # Extract objective
        objective_elem = view_elem.find('.//cwe:Objective', ns)
        if objective_elem is not None:
            view_data['objective'] = objective_elem.text or ''
        
        self.views[view_id] = view_data
    
    def _extract_relationships(self, root, ns: dict) -> None:
        """Extract all parent-child and other relationships."""
        # Parse relationships from Related_Weaknesses in weaknesses
        weaknesses_container = root.find('cwe:Weaknesses', ns)
        if weaknesses_container is not None:
            for weakness in weaknesses_container.findall('cwe:Weakness', ns):
                weakness_id = weakness.get('ID')
                
                related_weaknesses = weakness.find('cwe:Related_Weaknesses', ns)
                if related_weaknesses is not None:
                    for related in related_weaknesses.findall('cwe:Related_Weakness', ns):
                        target_id = related.get('CWE_ID')
                        nature = related.get('Nature', '')
                        
                        if target_id and nature:
                            self.relationships.append({
                                'source_id': weakness_id,
                                'target_id': target_id,
                                'nature': nature,
                                'source_type': 'weakness',
                                'target_type': 'weakness'
                            })
        
        # Parse relationships for categories
        categories_container = root.find('cwe:Categories', ns)
        if categories_container is not None:
            for category in categories_container.findall('cwe:Category', ns):
                category_id = category.get('ID')
                
                # Category members
                members = category.find('cwe:Members', ns)
                if members is not None:
                    for member in members.findall('cwe:Member', ns):
                        member_id = member.get('CWE_ID')
                        if member_id:
                            self.relationships.append({
                                'source_id': category_id,
                                'target_id': member_id,
                                'nature': 'HasMember',
                                'source_type': 'category',
                                'target_type': self._get_item_type(member_id)
                            })
        
        # Parse relationships for views
        views_container = root.find('cwe:Views', ns)
        if views_container is not None:
            for view in views_container.findall('cwe:View', ns):
                view_id = view.get('ID')
                
                # View members
                members = view.find('cwe:Members', ns)
                if members is not None:
                    for member in members.findall('cwe:Member', ns):
                        member_id = member.get('CWE_ID')
                        if member_id:
                            self.relationships.append({
                                'source_id': view_id,
                                'target_id': member_id,
                                'nature': 'HasMember',
                                'source_type': 'view',
                                'target_type': self._get_item_type(member_id)
                            })
    
    def _get_item_type(self, item_id: str) -> str:
        """Determine the type of a CWE item by ID."""
        if item_id in self.weaknesses:
            return 'weakness'
        elif item_id in self.categories:
            return 'category'
        elif item_id in self.views:
            return 'view'
        else:
            return 'unknown'
    
    def setup_collection(self) -> chromadb.Collection:
        """Setup ChromaDB collection for CWE data."""
        collection_name = 'cwe_data'
        
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
            logger.info(f"Using existing collection: {collection_name} ({collection.count()} docs)")
        except:
            collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={
                    "description": "CWE (Common Weakness Enumeration) data with hierarchical relationships",
                    "source": "https://cwe.mitre.org/",
                    "created_at": datetime.now().isoformat()
                }
            )
            logger.info(f"Created new collection: {collection_name}")
        
        return collection
    
    def prepare_documents(self) -> List[Dict[str, Any]]:
        """Prepare all CWE data as documents for ChromaDB storage."""
        documents = []
        
        # Process weaknesses
        for weakness_id, weakness in self.weaknesses.items():
            text_content = self._format_weakness_text(weakness)
            metadata = self._prepare_weakness_metadata(weakness)
            
            documents.append({
                'text': text_content,
                'metadata': metadata,
                'id': f"cwe_weakness_{weakness_id}"
            })
        
        # Process categories
        for category_id, category in self.categories.items():
            text_content = self._format_category_text(category)
            metadata = self._prepare_category_metadata(category)
            
            documents.append({
                'text': text_content,
                'metadata': metadata,
                'id': f"cwe_category_{category_id}"
            })
        
        # Process views
        for view_id, view in self.views.items():
            text_content = self._format_view_text(view)
            metadata = self._prepare_view_metadata(view)
            
            documents.append({
                'text': text_content,
                'metadata': metadata,
                'id': f"cwe_view_{view_id}"
            })
        
        # Add relationship documents
        relationship_docs = self._prepare_relationship_documents()
        documents.extend(relationship_docs)
        
        return documents
    
    def _format_weakness_text(self, weakness: Dict[str, Any]) -> str:
        """Format weakness data as searchable text."""
        text_parts = [
            f"# CWE-{weakness['id']}: {weakness['name']}",
            f"**Type**: Weakness",
            f"**Abstraction**: {weakness.get('abstraction', 'N/A')}",
            f"**Structure**: {weakness.get('structure', 'N/A')}",
            f"**Status**: {weakness.get('status', 'N/A')}",
            ""
        ]
        
        if weakness.get('description'):
            text_parts.extend([
                "## Description",
                weakness['description'],
                ""
            ])
        
        if weakness.get('extended_description'):
            text_parts.extend([
                "## Extended Description",
                weakness['extended_description'],
                ""
            ])
        
        if weakness.get('likelihood_of_exploit'):
            text_parts.extend([
                "## Likelihood of Exploit",
                weakness['likelihood_of_exploit'],
                ""
            ])
        
        if weakness.get('consequences'):
            text_parts.append("## Common Consequences")
            for consequence in weakness['consequences']:
                text_parts.append(f"- **Scope**: {consequence.get('scope', 'N/A')}")
                text_parts.append(f"  **Impact**: {consequence.get('impact', 'N/A')}")
                if consequence.get('note'):
                    text_parts.append(f"  **Note**: {consequence['note']}")
                text_parts.append("")
        
        if weakness.get('mitigations'):
            text_parts.append("## Potential Mitigations")
            for mitigation in weakness['mitigations']:
                if mitigation.get('phase'):
                    text_parts.append(f"- **Phase**: {mitigation['phase']}")
                if mitigation.get('description'):
                    text_parts.append(f"  **Description**: {mitigation['description']}")
                text_parts.append("")
        
        return '\n'.join(text_parts)
    
    def _format_category_text(self, category: Dict[str, Any]) -> str:
        """Format category data as searchable text."""
        text_parts = [
            f"# CWE-{category['id']}: {category['name']}",
            f"**Type**: Category",
            f"**Status**: {category.get('status', 'N/A')}",
            ""
        ]
        
        if category.get('summary'):
            text_parts.extend([
                "## Summary",
                category['summary'],
                ""
            ])
        
        return '\n'.join(text_parts)
    
    def _format_view_text(self, view: Dict[str, Any]) -> str:
        """Format view data as searchable text."""
        text_parts = [
            f"# CWE-{view['id']}: {view['name']}",
            f"**Type**: View",
            f"**View Type**: {view.get('type_attr', 'N/A')}",
            f"**Status**: {view.get('status', 'N/A')}",
            ""
        ]
        
        if view.get('objective'):
            text_parts.extend([
                "## Objective",
                view['objective'],
                ""
            ])
        
        return '\n'.join(text_parts)
    
    def _prepare_weakness_metadata(self, weakness: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for weakness."""
        metadata = {
            'cwe_id': weakness['id'],
            'cwe_type': 'weakness',
            'name': weakness['name'],
            'abstraction': weakness.get('abstraction', ''),
            'structure': weakness.get('structure', ''),
            'status': weakness.get('status', ''),
            'source': 'cwe_mitre',
            'has_consequences': len(weakness.get('consequences', [])) > 0,
            'has_mitigations': len(weakness.get('mitigations', [])) > 0,
        }
        
        # parent = CWEs that this weakness declares itself ChildOf
        parents = list(dict.fromkeys(
            r['target_id'] for r in self.relationships
            if r['source_id'] == weakness['id'] and r['nature'] == 'ChildOf'
        ))
        # children = CWEs that declare themselves ChildOf this weakness
        children = list(dict.fromkeys(
            r['source_id'] for r in self.relationships
            if r['target_id'] == weakness['id'] and r['nature'] == 'ChildOf'
        ))

        metadata['parent_ids'] = ','.join(parents) if parents else ''
        metadata['child_ids'] = ','.join(children) if children else ''
        metadata['relationship_count'] = len(parents) + len(children)
        
        return metadata
    
    def _prepare_category_metadata(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for category."""
        metadata = {
            'cwe_id': category['id'],
            'cwe_type': 'category',
            'name': category['name'],
            'status': category.get('status', ''),
            'source': 'cwe_mitre',
        }
        
        # Add relationship info
        members = [r['target_id'] for r in self.relationships 
                  if r['source_id'] == category['id'] and r['nature'] == 'HasMember']
        
        metadata['member_ids'] = ','.join(members) if members else ''
        metadata['member_count'] = len(members)
        
        return metadata
    
    def _prepare_view_metadata(self, view: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for view."""
        metadata = {
            'cwe_id': view['id'],
            'cwe_type': 'view',
            'name': view['name'],
            'view_type': view.get('type_attr', ''),
            'status': view.get('status', ''),
            'source': 'cwe_mitre',
        }
        
        # Add relationship info
        members = [r['target_id'] for r in self.relationships 
                  if r['source_id'] == view['id'] and r['nature'] == 'HasMember']
        
        metadata['member_ids'] = ','.join(members) if members else ''
        metadata['member_count'] = len(members)
        
        return metadata
    
    def _prepare_relationship_documents(self) -> List[Dict[str, Any]]:
        """Prepare relationship data as separate documents."""
        relationship_docs = []
        
        # Group relationships by nature
        relationship_groups = {}
        for rel in self.relationships:
            nature = rel['nature']
            if nature not in relationship_groups:
                relationship_groups[nature] = []
            relationship_groups[nature].append(rel)
        
        # Create documents for each relationship type
        for nature, rels in relationship_groups.items():
            text_content = f"# CWE Relationships: {nature}\n\n"
            text_content += f"This document contains all CWE relationships of type '{nature}'.\n\n"
            
            for rel in rels:
                source_name = self._get_item_name(rel['source_id'])
                target_name = self._get_item_name(rel['target_id'])
                
                text_content += f"- CWE-{rel['source_id']} ({source_name}) {nature} CWE-{rel['target_id']} ({target_name})\n"
            
            metadata = {
                'cwe_type': 'relationship',
                'relationship_nature': nature,
                'relationship_count': len(rels),
                'source': 'cwe_mitre'
            }
            
            relationship_docs.append({
                'text': text_content,
                'metadata': metadata,
                'id': f"cwe_relationships_{nature.lower()}"
            })
        
        return relationship_docs
    
    def _get_item_name(self, item_id: str) -> str:
        """Get the name of a CWE item by ID."""
        if item_id in self.weaknesses:
            return self.weaknesses[item_id]['name']
        elif item_id in self.categories:
            return self.categories[item_id]['name']
        elif item_id in self.views:
            return self.views[item_id]['name']
        else:
            return 'Unknown'
    
    def store_documents(self, documents: List[Dict[str, Any]], collection: chromadb.Collection) -> None:
        """Store documents in ChromaDB with batching."""
        if not documents:
            return
        
        logger.info(f"Storing {len(documents)} documents in ChromaDB...")
        
        # Store in chunks
        chunk_size = 100
        for i in range(0, len(documents), chunk_size):
            chunk = documents[i:i+chunk_size]
            
            texts = [doc['text'] for doc in chunk]
            metadatas = [doc['metadata'] for doc in chunk]
            ids = [doc['id'] for doc in chunk]
            
            with self.chroma_lock:
                try:
                    collection.add(
                        documents=texts,
                        metadatas=metadatas,
                        ids=ids
                    )
                    logger.info(f"Stored chunk {i//chunk_size + 1}: {len(chunk)} documents")
                except Exception as e:
                    logger.error(f"Error storing chunk: {e}")
        
        logger.info(f"Successfully stored all {len(documents)} documents")
    
    def fetch_and_store_cwe_data(self) -> None:
        self.progress['start_time'] = datetime.now()
        logger.info("Starting CWE data fetch and storage...")

        try:
            xml_content = self.download_cwe_data()
            self.parse_cwe_xml(xml_content)
            documents = self.prepare_documents()
            collection = self.setup_collection()
            self.store_documents(documents, collection)
            self._print_final_statistics(collection)

        except Exception as e:
            logger.error(f"Error during CWE data fetch: {e}")
            raise 
    
    def _print_final_statistics(self, collection: chromadb.Collection) -> None:
        """Print final statistics."""
        end_time = datetime.now()
        duration = end_time - self.progress['start_time']
        
        logger.info("=" * 60)
        logger.info("CWE DATA FETCH COMPLETE")
        logger.info("=" * 60)
        
        logger.info(f"Duration: {duration}")
        logger.info(f"Weaknesses: {len(self.weaknesses)}")
        logger.info(f"Categories: {len(self.categories)}")
        logger.info(f"Views: {len(self.views)}")
        logger.info(f"Relationships: {len(self.relationships)}")
        logger.info(f"Total documents in ChromaDB: {collection.count()}")


def main():
    """Main function to run the CWE data fetch."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch CWE data and store in ChromaDB")
    parser.add_argument("--workers", type=int, default=4,
                       help="Number of concurrent workers")

    args = parser.parse_args()

    try:
        fetcher = CWEFetcher(max_workers=args.workers)
        fetcher.fetch_and_store_cwe_data()
        
        print("\nCWE data fetch completed successfully!")
        
    except KeyboardInterrupt:
        print("\nFetch interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()