from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from uuid import UUID
import uuid
from pathlib import Path
import os
import chromadb
from fastapi import HTTPException
from chromadb.config import Settings
from dotenv import load_dotenv
load_dotenv()

client = chromadb.HttpClient(host='localhost', port=9786, settings=Settings(anonymized_telemetry=False))

def PDF_to_documents(file_paths: list, chunk_size: int=500, chunk_overlap=100, separator="", dataset_id="") -> list[Document]:
    """
    Load and split PDF files into documents.
    :param file_paths: a list of file paths
    :param chunk_size: the size of each chunk
    :param chunk_overlap: the overlap between chunks
    :param separator: the separator between chunks
    :return: a list of documents
    """
    print(chunk_size, chunk_overlap, separator)
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separator=separator,
        length_function=len
    )
    documents = []
    for file_path in file_paths:
        # 提取文件名
        filename = os.path.basename(file_path)  
        # 加载PDF的完整内容
        loader = PyPDFLoader(file_path)
        full_text = loader.load()
        
        # 计算总字数
        total_word_count = sum(len(page.page_content) for page in full_text)
        
        # 分割文档
        temp_documents = loader.load_and_split(text_splitter=text_splitter)
        
        count = 1
        chunk_sum_num = len(temp_documents)

        article_id = str(uuid.uuid4()) # 注意：放在循环外，所有分块共享一个article_id
        
        for document in temp_documents:
            document.metadata["filename"] = filename
            document.metadata["chunk_count"] = count
            document.metadata["chunk_sum_num"] = chunk_sum_num
            document.metadata["total_word_count"] = total_word_count  # 添加总字数到metadata
            document.metadata["chunk_word_count"] = len(document.page_content)  # 添加分块字数到metadata
            document.metadata["document_metadata_id"] = str(uuid.uuid4())  # 添加document_id到metadata
            document.metadata["article_id"] = article_id  # 添加article_id到metadata
            document.metadata["dataset_id"] = str(dataset_id)  # 添加dataset_id到metadata
            count += 1
        
        documents.extend(temp_documents)
    
    return documents


# 获取 vectorstore 的存储路径
# vectorstore_dir = Path("static/vectorstore")
# def get_vectorstore_path(dataset_id: UUID) -> str:
#     vectorstore_path = vectorstore_dir / str(dataset_id)
#     vectorstore_path.mkdir(parents=True, exist_ok=True)
#     return str(vectorstore_path)

# def load_vectorstore(dataset_id: UUID, embedding_function = OpenAIEmbeddings()) -> Chroma:
#     vectorstore_path = get_vectorstore_path(dataset_id)
#     print(f"Loading vectorstore from {vectorstore_path}")
    
#     vectorstore = Chroma(
#         embedding_function = embedding_function,
#         persist_directory = vectorstore_path
#     )
#     return vectorstore

def load_vectorstore(dataset_id: UUID, embedding_function = OpenAIEmbeddings()) -> Chroma:
    # vectorstore_path = get_vectorstore_path(dataset_id)
    # collection = client.get_or_create_collection(dataset_id)
    print(f"Loading vectorstore id: {dataset_id}")
    
    vectorstore = Chroma(
        client=client,
        collection_name=str(dataset_id),
        embedding_function=embedding_function,
    )
    return vectorstore



def transform_data(data, keep_keys, new_keys=None):
    """
    将字典数组转换为数组字典，保留指定的key。
    
    参数:
    data (dict): 包含多个数组的字典，每个数组表示某种类型的数据。
    keep_keys (list): 要保留的key的列表。

    返回:
    list: 转换后的数组字典。
    """
    # 初始化新的数据结构
    transformed_data = []

    # 获取数据的长度
    # 默认使用第一个key的长度
    keyword = keep_keys[0]
    data_length = len(data[keyword])
    
    # 遍历索引并填充新的数据结构
    for i in range(data_length):
        entry = {new_keys[index]: data[key][i] for index, key in enumerate(keep_keys) if key in data}
        transformed_data.append(entry)

    return transformed_data


def retrieval_similarity_search(dataset_ids: list[UUID], query: str, k: int, min_relevance: float):
    print(k)
    if k < 1:
        return []
    all_docs_and_scores = []
    for dataset_id in dataset_ids:
        try:
            # 加载向量数据库
            vectorstore = load_vectorstore(dataset_id)
            docs_and_scores = vectorstore.similarity_search_with_score(query=query, k=k)
            all_docs_and_scores.extend([
                {
                    **document.__dict__,
                    "score": 1 - score
                } for document, score in docs_and_scores if 1 - score >= min_relevance
            ])
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # 按照分数从高到低排序，并选出前k个结果
    sorted_docs_and_scores = sorted(all_docs_and_scores, key=lambda x: x['score'], reverse=True)[:k]
    return sorted_docs_and_scores

