def select_documents(documents, max_chars):
    if type(max_chars) is not int or max_chars < 1:
        raise ValueError('Positive integer character budget required')
    result, seen, used = [], {}, 0
    for doc in documents:
        key = (doc.metadata['source'], doc.metadata['revision'])
        if key in seen:
            if seen[key] != doc.page_content:
                raise ValueError('Same source/revision identifies conflicting content')
            continue
        seen[key] = doc.page_content
        if used + len(doc.page_content) <= max_chars:
            result.append(doc)
            used += len(doc.page_content)
    return result
