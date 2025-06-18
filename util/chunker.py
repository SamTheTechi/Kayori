from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text, size=175, overlaping=25):
    if (len(text) > size):
        split = RecursiveCharacterTextSplitter(
            chunk_size=size, chunk_overlap=overlaping)
        chunks = split.split_text(text)
        return chunks
    else:
        return [text]
