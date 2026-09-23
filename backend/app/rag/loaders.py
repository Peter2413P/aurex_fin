def get_loader_for_file(file_path: str):
    ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
    
    if ext == 'pdf':
        from langchain_community.document_loaders.pdf import PyMuPDFLoader
        return PyMuPDFLoader(file_path)
    elif ext == 'docx':
        from langchain_community.document_loaders.docx2txt import Docx2txtLoader
        return Docx2txtLoader(file_path)
    elif ext == 'pptx':
        from langchain_community.document_loaders.powerpoint import UnstructuredPowerPointLoader
        return UnstructuredPowerPointLoader(file_path)
    elif ext == 'csv':
        from langchain_community.document_loaders.csv_loader import CSVLoader
        return CSVLoader(file_path)
    elif ext == 'txt':
        from langchain_community.document_loaders.text import TextLoader
        return TextLoader(file_path, autodetect_encoding=True)
    elif ext == 'md':
        from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
        return UnstructuredMarkdownLoader(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

