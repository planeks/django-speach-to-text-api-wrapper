def split_stream_by_chunks(stream, chunk_size):
    """
    Splits bytes stream into chunks with given size

    Args:
        stream: bytes stream
        chunk_size: size of every chunk

    Returns:
        result: list of chunks
    """

    result = []
    stream_size = len(stream)
    n_chunks = stream_size // chunk_size
    for i in range(n_chunks if n_chunks * chunk_size == stream_size else n_chunks + 1):
        result.append(stream[i * chunk_size:i * chunk_size + chunk_size])
    return result
