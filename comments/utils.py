
def annotate_comment_tree(comments):
    if not comments:
        return

    iterator = iter(comments)
    current = next(iterator)

    current.open = True

    for next_comment in iterator:
        if next_comment.depth > current.depth:
            next_comment.open = True
        else:
            current.close = list(range(current.depth - next_comment.depth))
            if next_comment.root_id != current.root_id:
                # if exist next_comment thread, close current thread
                current.close.append(1)
                next_comment.open = True

        yield current
        current = next_comment

    current.close = range(current.depth)
    yield current
