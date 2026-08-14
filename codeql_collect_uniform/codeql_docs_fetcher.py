#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import time
import logging
import chromadb
from typing import List, Dict, Any, Set
from pathlib import Path
from bs4 import BeautifulSoup
import re
import hashlib
from urllib.parse import urljoin, urlparse
from datetime import datetime
import concurrent.futures
import threading
from queue import Queue
import os
from src.config import CHROMA_DB_PATH, JAVA_LIBRARY_QLPACK_PATH, JAVA_SECURITY_QLPACK_PATH, CPP_SECURITY_QLPACK_PATH,CPP_LIBRARY_QLPACK_PATH,get_chroma_client,PYTHON_LIBRARY_QLPACK_PATH,PYTHON_SECURITY_QLPACK_PATH
from src.retriever.bge_embedding import sequential_encode
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# JAVA_SECURITY_QLPACK_PATH="/opt/codeql-bundle-2.23.3/qlpacks/codeql/java-queries/1.8.2/Security/CWE"
# JAVA_LIBRARY_QLPACK_PATH="/opt/codeql-bundle-2.23.3/qlpacks/codeql/java-all/7.7.2/semmle/code/java"

# CPP_SECURITY_QLPACK_PATH="/opt/codeql-bundle-2.23.3/qlpacks/codeql/cpp-queries/1.5.2/Security/CWE"
# CPP_LIBRARY_QLPACK_PATH="/opt/codeql-bundle-2.23.3/qlpacks/codeql/cpp-all/6.0.0/semmle/code/cpp"

# PYTHON_SECURITY_QLPACK_PATH="/opt/codeql-bundle-2.23.3/qlpacks/codeql/python-queries/1.6.7/Security"
# PYTHON_LIBRARY_QLPACK_PATH="/opt/codeql-bundle-2.23.3/qlpacks/codeql/python-all/4.0.17/semmle/python"


class CodeQLDocsFetcher:
    
    def __init__(self, data_dir: str = None, max_workers: int = 8): 
        if data_dir is None:
            data_dir = CHROMA_DB_PATH 
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.chroma_client = get_chroma_client()
        self.chroma_lock = threading.Lock()

        # BGE-large-en-v1.5 model path for pre-computing embeddings via sequential_encode
        self.bge_model_path = "/root/code_check/src/retriever/embedding_model/bge-large-en-v1.5"

        self.max_workers = max_workers
        self.request_delay = 0.5  
        
        self.session_pool = Queue()
        for _ in range(max_workers):
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (compatible; CodeQL-Documentation-Fetcher/1.0)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            })
            self.session_pool.put(session)
        
        # Track visited URLs with thread safety
        self.visited_urls = set()
        self.visited_lock = threading.Lock()
        
        # Progress tracking
        self.progress = {
            'total_urls': 0,
            'fetched': 0,
            'failed': 0,
            'start_time': None
        }
        self.progress_lock = threading.Lock()
        self.codeql_ql_reference={
            'ql_reference': {
                'base_url': 'https://codeql.github.com/docs/ql-language-reference/',
                'collection': 'codeql_ql_reference'
            }
        }
        # Documentation sources
        self.java_doc_sources = {
            'java_stdlib': {
                'base_url': 'https://codeql.github.com/codeql-standard-libraries/java/index.html',
                'collection': 'java_codeql_stdlib'
            },
            'language_guides': {
                'urls': [
                    'https://codeql.github.com/docs/codeql-language-guides/abstract-syntax-tree-classes-for-working-with-java-programs/',
                    'https://codeql.github.com/docs/codeql-language-guides/basic-query-for-java-code/',
                    'https://codeql.github.com/docs/codeql-language-guides/codeql-library-for-java/',
                    'https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-java/',
                    'https://codeql.github.com/docs/codeql-language-guides/navigating-the-call-graph/',
                    'https://codeql.github.com/docs/codeql-language-guides/annotations-in-java/'
                ],
                'collection': 'java_codeql_language_guides'
            },
            'local_codeql_queries': {
                'local_path': JAVA_LIBRARY_QLPACK_PATH,
                'collection': 'java_codeql_local_queries'
            },
            'local_codeql_security_queries': {
                'local_path': JAVA_SECURITY_QLPACK_PATH,
                'collection': 'java_codeql_local_queries'
            }
        }
        self.cpp_doc_sources = {
            'cpp_stdlib': {
                'base_url': 'https://codeql.github.com/codeql-standard-libraries/cpp/index.html',
                'collection': 'cpp_codeql_stdlib'
            },
            'language_guides': {
                'urls': [
                    'https://codeql.github.com/docs/codeql-language-guides/basic-query-for-cpp-code/',
                    'https://codeql.github.com/docs/codeql-language-guides/codeql-library-for-cpp/',
                    'https://codeql.github.com/docs/codeql-language-guides/functions-in-cpp/',
                    'https://codeql.github.com/docs/codeql-language-guides/expressions-types-and-statements-in-cpp/',
                    'https://codeql.github.com/docs/codeql-language-guides/conversions-and-classes-in-cpp/',
                    'https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-cpp/',
                    'https://codeql.github.com/docs/codeql-language-guides/refining-a-query-to-account-for-edge-cases/',
                    'https://codeql.github.com/docs/codeql-language-guides/detecting-a-potential-buffer-overflow/',
                    'https://codeql.github.com/docs/codeql-language-guides/using-the-guards-library-in-cpp/',
                    'https://codeql.github.com/docs/codeql-language-guides/using-range-analsis-in-cpp/',
                    'https://codeql.github.com/docs/codeql-language-guides/hash-consing-and-value-numbering/',
                    'https://codeql.github.com/docs/codeql-language-guides/advanced-dataflow-scenarios-cpp/',
                    'https://codeql.github.com/docs/codeql-language-guides/customizing-library-models-for-cpp/'
                ],
                'collection': 'cpp_codeql_language_guides'
            },
            'local_codeql_queries': {
                'local_path': CPP_LIBRARY_QLPACK_PATH,
                'collection': 'cpp_codeql_local_queries'
            },
            'local_codeql_security_queries': {
                'local_path': CPP_SECURITY_QLPACK_PATH,
                'collection': 'cpp_codeql_local_queries'
            }
        }
        self.python_doc_sources = {
                    'python_stdlib': {
                        'base_url': 'https://codeql.github.com/codeql-standard-libraries/python/index.html',
                        'collection': 'python_codeql_stdlib'
                    },
                    'language_guides': {
                        'urls': [
                            'https://codeql.github.com/docs/codeql-language-guides/basic-query-for-python-code/',
                            'https://codeql.github.com/docs/codeql-language-guides/codeql-library-for-python/',
                            'https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-python/',
                            'https://codeql.github.com/docs/codeql-language-guides/using-api-graphs-in-python/',
                            'https://codeql.github.com/docs/codeql-language-guides/functions-in-python/',
                            'https://codeql.github.com/docs/codeql-language-guides/expressions-and-statements-in-python/',
                            'https://codeql.github.com/docs/codeql-language-guides/analyzing-control-flow-in-python/',
                            'https://codeql.github.com/docs/codeql-language-guides/customizing-library-models-for-python/'
                        ],
                        'collection': 'python_codeql_language_guides'
                    },
                    'local_codeql_queries': {
                        'local_path': PYTHON_LIBRARY_QLPACK_PATH,
                        'collection': 'python_codeql_local_queries'
                    },
                    'local_codeql_security_queries': {
                        'local_path': PYTHON_SECURITY_QLPACK_PATH,
                        'collection': 'python_codeql_local_queries'
                    }
                }


        
    
    def get_session(self) -> requests.Session:
        return self.session_pool.get()
    
    def return_session(self, session: requests.Session) -> None:
        self.session_pool.put(session)
    
    def setup_collections(self) -> Dict[str, chromadb.Collection]:
        """Setup ChromaDB collections for different document types."""
        collections = {}

        # Gather all unique collection names from the three source groups
        collection_descriptions = {
            'codeql_ql_reference': 'CodeQL QL Language Reference (shared)',
            
            'java_codeql_stdlib': 'CodeQL Java Standard Library Documentation',
            'java_codeql_language_guides': 'CodeQL Java Language Guides',
            'java_codeql_local_queries': 'Local CodeQL Java Queries and Libraries',

            'cpp_codeql_stdlib': 'CodeQL C++ Standard Library Documentation',
            'cpp_codeql_language_guides': 'CodeQL C++ Language Guides',
            'cpp_codeql_local_queries': 'Local CodeQL C++ Queries and Libraries',

            'python_codeql_stdlib': 'CodeQL Python Standard Library Documentation',
            'python_codeql_language_guides': 'CodeQL Python Language Guides',
            'python_codeql_local_queries': 'Local CodeQL Python Queries and Libraries'
        }

        # Collect all referenced collection names from source dicts
        used_collections = set()
        for src in self.codeql_ql_reference.values():
            used_collections.add(src['collection'])
        # for src in self.java_doc_sources.values():
        #     used_collections.add(src['collection'])
        # for src in self.cpp_doc_sources.values():
        #     used_collections.add(src['collection'])
        for src in self.python_doc_sources.values():
            used_collections.add(src['collection'])

        for name in used_collections:
            description = collection_descriptions.get(name, f'CodeQL Documentation - {name}')
            try:
                collection = self.chroma_client.get_collection(name=name)
                logger.info(f"Using existing collection: {name} ({collection.count()} docs)")
            except:
                collection = self.chroma_client.create_collection(
                    name=name,
                    metadata={"description": description}
                )
                logger.info(f"Created new collection: {name}")

            collections[name] = collection

        return collections
    
    def fetch_page_content(self, url: str) -> Dict[str, Any]:
        """Fetch and process a single page with error handling."""
        # Check if already visited
        with self.visited_lock:
            if url in self.visited_urls:
                return None
            self.visited_urls.add(url)
        
        session = self.get_session()
        try:
            time.sleep(self.request_delay)  # Rate limiting
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            # Process content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            if title:
                title_text = title.get_text().strip()
            else:
                title_tag = soup.find('title')
                title_text = title_tag.get_text().strip() if title_tag else url.split('/')[-1]
            
            # Extract main content
            content_div = (soup.find('main') or 
                          soup.find('div', class_='content') or 
                          soup.find('article') or
                          soup.find('div', class_='documentation'))
            
            if content_div:
                for elem in content_div.find_all(['nav', 'aside', 'footer', 'header', 'script', 'style']):
                    elem.decompose()
                content_text = self._extract_structured_content(content_div)
            else:
                content_text = soup.get_text()
            
            # Extract metadata and code examples
            metadata = self._extract_page_metadata(soup, url)
            code_examples = self._extract_code_examples(soup)
            
            # Update progress
            with self.progress_lock:
                self.progress['fetched'] += 1
                if self.progress['fetched'] % 100 == 0:
                    logger.info(f"Progress: {self.progress['fetched']}/{self.progress['total_urls']} pages")
            
            return {
                'url': url,
                'title': title_text,
                'content': content_text,
                'metadata': metadata,
                'code_examples': code_examples,
                'fetch_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            with self.progress_lock:
                self.progress['failed'] += 1
            logger.error(f"Error fetching {url}: {e}")
            return None
        finally:
            self.return_session(session)
    
    def _extract_structured_content(self, content_div) -> str:
        """Extract structured content preserving formatting."""
        content_parts = []
        
        for element in content_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'code', 'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'table']):
            if element.name.startswith('h'):
                level = '#' * int(element.name[1])
                content_parts.append(f"\n{level} {element.get_text().strip()}\n")
            elif element.name == 'pre':
                code_text = element.get_text().strip()
                content_parts.append(f"\n```\n{code_text}\n```\n")
            elif element.name == 'code':
                content_parts.append(f"`{element.get_text().strip()}`")
            elif element.name in ['ul', 'ol']:
                list_items = element.find_all('li', recursive=False)
                for li in list_items:
                    content_parts.append(f"- {li.get_text().strip()}")
                content_parts.append("")
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    content_parts.append(f"{text}\n")
        
        return '\n'.join(content_parts)
    
    def _extract_page_metadata(self, soup, url: str) -> Dict[str, Any]:
        """Extract metadata from the page."""
        metadata = {
            'url': url,
            'source': 'codeql_docs',
            'type': 'documentation'
        }
        
        # Determine document type from URL
        if '/codeql-standard-libraries/java/' in url:
            metadata['doc_type'] = 'java_stdlib'
            metadata['language'] = 'java'
        elif '/codeql-standard-libraries/cpp/' in url:
            metadata['doc_type'] = 'cpp_stdlib'
            metadata['language'] = 'cpp'
        elif '/codeql-standard-libraries/python/' in url:
            metadata['doc_type'] = 'python_stdlib'
            metadata['language'] = 'python'
        elif '/ql-language-reference/' in url:
            metadata['doc_type'] = 'ql_reference'
        elif '/codeql-language-guides/' in url:
            metadata['doc_type'] = 'language_guide'
            if '-java' in url or 'java' in url:
                metadata['language'] = 'java'
            elif '-cpp' in url or 'cpp' in url or 'c++' in url.lower():
                metadata['language'] = 'cpp'
            elif '-python' in url or 'python' in url:
                metadata['language'] = 'python'

        return metadata
    
    def _extract_code_examples(self, soup) -> List[Dict[str, str]]:
        """Extract code examples from the page."""
        examples = []
        code_blocks = soup.find_all(['pre', 'code'])
        
        for i, block in enumerate(code_blocks):
            code_text = block.get_text().strip()
            if len(code_text) < 20:
                continue
            
            language = "codeql"
            if any(keyword in code_text for keyword in ['public class', 'private', 'void', 'String']):
                language = "java"
            
            examples.append({
                'code': code_text,
                'language': language,
                'index': i
            })
        
        return examples
    
    def get_all_links(self, base_url: str, url_pattern: str = None) -> List[str]:
        """Get all documentation links from a base URL."""
        logger.info(f"Fetching links from: {base_url}")
        
        session = self.get_session()
        try:
            response = session.get(base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = [base_url]  # Include the base page
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Skip external links and fragments
                if href.startswith('http') and not href.startswith('https://codeql.github.com/'):
                    continue
                if href.startswith('#'):
                    continue
                
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, href)
                
                # Apply URL pattern filter if provided
                if url_pattern and url_pattern not in full_url:
                    continue
                
                # Only include HTML pages
                if full_url.endswith('.html') or (not full_url.endswith('.html') and '/docs/' in full_url):
                    if full_url not in links:
                        links.append(full_url)
            
            logger.info(f"Found {len(links)} links from {base_url}")
            return links
            
        except Exception as e:
            logger.error(f"Error fetching links from {base_url}: {e}")
            return [base_url]
        finally:
            self.return_session(session)
    
    def load_local_codeql_queries(self, local_path: str) -> List[Dict[str, Any]]:
        logger.info(f"Loading local CodeQL queries from: {local_path}")
        
        if not os.path.exists(local_path):
            logger.error(f"Local path does not exist: {local_path}")
            return []
        
        query_files = []
        
        for root, dirs, files in os.walk(local_path):
            for file in files:
                if file.endswith(('.ql', '.qll')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        metadata = self._extract_query_metadata(content, file_path, local_path)
                        
                        query_files.append({
                            'file_path': file_path,
                            'relative_path': os.path.relpath(file_path, local_path),
                            'filename': file,
                            'content': content,
                            'metadata': metadata,
                            'file_type': 'query' if file.endswith('.ql') else 'library'
                        })
                        
                    except Exception as e:
                        logger.error(f"Error reading {file_path}: {e}")
                        continue
        
        logger.info(f"Loaded {len(query_files)} CodeQL files from local filesystem")
        return query_files
    
    def _extract_query_metadata(self, content: str, file_path: str, base_path: str) -> Dict[str, Any]:
        """Extract metadata from CodeQL query/library files."""
        is_security = '/Security/' in file_path or '/security/' in file_path or '/CWE' in file_path

        metadata = {
            'source': 'local_codeql_cwe' if is_security else 'local_codeql',
            'type': 'query' if file_path.endswith('.ql') else 'library',
            'file_path': file_path,
            'relative_path': os.path.relpath(file_path, base_path)
        }

        # Extract @metadata comments
        metadata_patterns = {
            'name': r'@name\s+(.+)',
            'description': r'@description\s+(.+)',
            'kind': r'@kind\s+(.+)',
            'tags': r'@tags\s+(.+)',
            'cwe': r'@id\s+(CWE-\d+)',
            'precision': r'@precision\s+(.+)',
            'severity': r'@severity\s+(.+)',
        }

        for key, pattern in metadata_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata[key] = match.group(1).strip()

        # Extract CWE number from path or filename
        cwe_path_match = re.search(r'CWE-?(\d+)', file_path)
        if cwe_path_match:
            metadata['cwe_number'] = cwe_path_match.group(1)

        # Determine category from path
        if is_security:
            metadata['category'] = 'security'
        elif '/dataflow/' in file_path:
            metadata['category'] = 'dataflow'
        elif '/taint/' in file_path:
            metadata['category'] = 'taint'
        elif '/ast/' in file_path:
            metadata['category'] = 'ast'
        else:
            metadata['category'] = 'general'

        return metadata
    
    def store_documents(self, documents: List[Dict[str, Any]],
                                collection: chromadb.Collection) -> None:
        if not documents:
            return

        texts = [doc['text'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        ids = [doc['id'] for doc in documents]

        # Pre-compute embeddings in one batch via sequential_encode (CPU-optimized)
        logger.info(f"Encoding {len(texts)} documents with BGE (batch_size=128)...")
        embeddings = sequential_encode(texts, self.bge_model_path, batch_size=128)
        # Convert numpy array to list-of-lists for ChromaDB
        embedding_list = embeddings.tolist()

        # Single write with pre-computed embeddings
        write_batch = 200  # ChromaDB handles larger batches when embeddings are pre-computed
        for i in range(0, len(texts), write_batch):
            with self.chroma_lock:
                try:
                    collection.add(
                        documents=texts[i:i+write_batch],
                        embeddings=embedding_list[i:i+write_batch],
                        metadatas=metadatas[i:i+write_batch],
                        ids=ids[i:i+write_batch]
                    )
                    logger.info(f"Stored {min(i+write_batch, len(texts))}/{len(texts)} documents")
                except Exception as e:
                    logger.error(f"Error storing batch: {e}")
    
    def process_url_batch(self, urls: List[str], collection_name: str, 
                         collections: Dict[str, chromadb.Collection]) -> None:
        collection = collections[collection_name]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all fetch tasks
            future_to_url = {
                executor.submit(self.fetch_page_content, url): url 
                for url in urls
            }
            
            # Collect results
            documents = []
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    doc_data = future.result()
                    if doc_data:
                        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
                        doc_id = f"{collection_name}_{url_hash}"
                        main_doc = {
                            'text': f"# {doc_data['title']}\n\nURL: {doc_data['url']}\n\n{doc_data['content']}",
                            'metadata': doc_data['metadata'],
                            'id': doc_id
                        }
                        documents.append(main_doc)
                        
                        for j, example in enumerate(doc_data['code_examples']):
                            if len(example['code']) > 30:
                                example_doc = {
                                    'text': f"Code Example from {doc_data['title']}:\n\n```{example['language']}\n{example['code']}\n```",
                                    'metadata': {
                                        **doc_data['metadata'],
                                        'type': 'code_example',
                                        'example_language': example['language'],
                                        'parent_title': doc_data['title']
                                    },
                                    'id': f"{doc_id}_example_{j}"
                                }
                                documents.append(example_doc)
                
                except Exception as e:
                    logger.error(f"Error processing result for {url}: {e}")
        
        # Store all documents
        if documents:
            self.store_documents(documents, collection)
            logger.info(f"Completed batch: {len(documents)} documents stored")
    
    def fetch_all_documentation(self) -> None:
        self.progress['start_time'] = datetime.now()
        logger.info("Starting CodeQL documentation fetch...")

        # Setup collections
        collections = self.setup_collections()

        # --- 1. Shared QL Language Reference ---
        all_url_batches = []

        logger.info("Collecting QL Language Reference URLs...")
        ql_ref_src = self.codeql_ql_reference['ql_reference']
        ql_ref_links = self.get_all_links(
            ql_ref_src['base_url'],
            url_pattern='/docs/ql-language-reference/'
        )
        all_url_batches.append((ql_ref_links, ql_ref_src['collection']))

        # --- 2. Java documentation sources (disabled) ---
        # logger.info("Collecting Java Standard Library URLs...")
        # java_stdlib_src = self.java_doc_sources['java_stdlib']
        # java_stdlib_links = self.get_all_links(java_stdlib_src['base_url'])
        # all_url_batches.append((java_stdlib_links, java_stdlib_src['collection']))
        #
        # logger.info("Collecting Java Language Guide URLs...")
        # java_guide_src = self.java_doc_sources['language_guides']
        # all_url_batches.append((java_guide_src['urls'], java_guide_src['collection']))

        # --- 3. C++ documentation sources (disabled) ---
        # logger.info("Collecting C++ Standard Library URLs...")
        # cpp_stdlib_src = self.cpp_doc_sources['cpp_stdlib']
        # cpp_stdlib_links = self.get_all_links(cpp_stdlib_src['base_url'])
        # all_url_batches.append((cpp_stdlib_links, cpp_stdlib_src['collection']))
        #
        # logger.info("Collecting C++ Language Guide URLs...")
        # cpp_guide_src = self.cpp_doc_sources['language_guides']
        # all_url_batches.append((cpp_guide_src['urls'], cpp_guide_src['collection']))

        # --- 4. Python documentation sources ---
        logger.info("Collecting Python Standard Library URLs...")
        python_stdlib_src = self.python_doc_sources['python_stdlib']
        python_stdlib_links = self.get_all_links(python_stdlib_src['base_url'])
        all_url_batches.append((python_stdlib_links, python_stdlib_src['collection']))

        logger.info("Collecting Python Language Guide URLs...")
        python_guide_src = self.python_doc_sources['language_guides']
        all_url_batches.append((python_guide_src['urls'], python_guide_src['collection']))

        # Calculate total URLs
        total_urls = sum(len(urls) for urls, _ in all_url_batches)
        self.progress['total_urls'] = total_urls
        logger.info(f"Total URLs to process: {total_urls}")

        for urls, collection_name in all_url_batches:
            logger.info(f"Processing {len(urls)} URLs for {collection_name}")
            batch_size = 100
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i+batch_size]
                logger.info(f"Processing batch {i//batch_size + 1} for {collection_name}")
                self.process_url_batch(batch_urls, collection_name, collections)

        # --- 5. Local CodeQL queries (Java) (disabled) ---
        # self._fetch_local_queries(
        #     library_src=self.java_doc_sources['local_codeql_queries'],
        #     security_src=self.java_doc_sources['local_codeql_security_queries'],
        #     collections=collections
        # )

        # --- 6. Local CodeQL queries (C++) (disabled) ---
        # self._fetch_local_queries(
        #     library_src=self.cpp_doc_sources['local_codeql_queries'],
        #     security_src=self.cpp_doc_sources['local_codeql_security_queries'],
        #     collections=collections
        # )

        # --- 7. Local CodeQL queries (Python) ---
        self._fetch_local_queries(
            library_src=self.python_doc_sources['local_codeql_queries'],
            security_src=self.python_doc_sources['local_codeql_security_queries'],
            collections=collections
        )

        self._print_final_statistics(collections)

    def _fetch_local_queries(self, library_src: Dict[str, Any],
                             security_src: Dict[str, Any],
                             collections: Dict[str, chromadb.Collection]) -> None:
        """Load local .ql/.qll files from library and security paths and store them."""
        collection_name = library_src['collection']  # both share the same collection
        local_path = library_src['local_path']
        security_path = security_src['local_path']

        logger.info(f"Loading local library queries from: {local_path}")
        local_queries = self.load_local_codeql_queries(local_path)

        logger.info(f"Loading local security queries from: {security_path}")
        security_queries = self.load_local_codeql_queries(security_path)

        all_local_queries = local_queries + security_queries
        if not all_local_queries:
            return

        documents = []
        for query_file in all_local_queries:
            main_text = f"# {query_file['filename']}\n\n"
            main_text += f"**Type**: {query_file['file_type']}\n"
            main_text += f"**Path**: {query_file['relative_path']}\n"
            main_text += f"**Category**: {query_file['metadata'].get('category', 'general')}\n\n"

            if 'cwe_number' in query_file['metadata']:
                main_text += f"**CWE**: CWE-{query_file['metadata']['cwe_number']}\n"
            if 'name' in query_file['metadata']:
                main_text += f"**Name**: {query_file['metadata']['name']}\n"
            if 'description' in query_file['metadata']:
                main_text += f"**Description**: {query_file['metadata']['description']}\n"

            if query_file['metadata'].get('category') == 'security':
                doc_id = f"cwe_query_{query_file['relative_path'].replace('/', '_').replace('.', '_')}"
            else:
                doc_id = f"local_query_{query_file['relative_path'].replace('/', '_').replace('.', '_')}"

            main_text += f"\n```codeql\n{query_file['content']}\n```"

            documents.append({
                'text': main_text,
                'metadata': query_file['metadata'],
                'id': doc_id
            })

        self.store_documents(documents, collections[collection_name])
        logger.info(f"Stored {len(documents)} local query documents in '{collection_name}'")
    
    def _print_final_statistics(self, collections: Dict[str, chromadb.Collection]) -> None:
        end_time = datetime.now()
        duration = end_time - self.progress['start_time']
        
        logger.info("=" * 60)
        logger.info("DOCUMENTATION FETCH COMPLETE")
        logger.info("=" * 60)
        
        logger.info(f"Duration: {duration}")
        logger.info(f"Total pages processed: {self.progress['fetched']}")
        logger.info(f"Failed pages: {self.progress['failed']}")
        logger.info(f"Success rate: {self.progress['fetched']/(self.progress['fetched']+self.progress['failed'])*100:.1f}%")
        
        logger.info("\nCollection Statistics:")
        total_docs = 0
        for name, collection in collections.items():
            count = collection.count()
            total_docs += count
            logger.info(f"  {name}: {count} documents")
        
        logger.info(f"\nTotal documents in ChromaDB: {total_docs}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="fetch of comprehensive CodeQL documentation")
    parser.add_argument("--data-dir", help="ChromaDB data directory",
                       default=CHROMA_DB_PATH)
    parser.add_argument("--workers", type=int, default=8,
                       help="Number of parallel workers")
    parser.add_argument("--java-library-path", help="Path to local Java CodeQL library qlpack",
                       default=JAVA_LIBRARY_QLPACK_PATH)
    parser.add_argument("--java-security-path", help="Path to local Java CodeQL security qlpack",
                       default=JAVA_SECURITY_QLPACK_PATH)
    parser.add_argument("--cpp-library-path", help="Path to local C++ CodeQL library qlpack",
                       default=CPP_LIBRARY_QLPACK_PATH)
    parser.add_argument("--cpp-security-path", help="Path to local C++ CodeQL security qlpack",
                       default=CPP_SECURITY_QLPACK_PATH)
    parser.add_argument("--python-library-path", help="Path to local Python CodeQL library qlpack",
                       default=PYTHON_LIBRARY_QLPACK_PATH)
    parser.add_argument("--python-security-path", help="Path to local Python CodeQL security qlpack",
                       default=PYTHON_SECURITY_QLPACK_PATH)     
    

    args = parser.parse_args()

    try:
        fetcher = CodeQLDocsFetcher(
            data_dir=args.data_dir,
            max_workers=args.workers
        )

        # fetcher.java_doc_sources['local_codeql_queries']['local_path'] = args.java_library_path
        # fetcher.java_doc_sources['local_codeql_security_queries']['local_path'] = args.java_security_path
        # fetcher.cpp_doc_sources['local_codeql_queries']['local_path'] = args.cpp_library_path
        # fetcher.cpp_doc_sources['local_codeql_security_queries']['local_path'] = args.cpp_security_path
        fetcher.python_doc_sources['local_codeql_queries']['local_path'] = args.python_library_path
        fetcher.python_doc_sources['local_codeql_security_queries']['local_path'] = args.python_security_path


        fetcher.fetch_all_documentation()

        print(f"\n documentation fetch completed successfully!")
        print(f" ChromaDB location: {args.data_dir}")

    except KeyboardInterrupt:
        print("\n fetch interrupted")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
    #保存log
   
