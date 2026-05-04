UPDATE document_holder
SET
    reference_no = COALESCE(%s, reference_no),
    tag_number = COALESCE(%s, tag_number),
    title = COALESCE(%s, title)
WHERE id = %s;
