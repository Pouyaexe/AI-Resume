import aspose.words as aw

def markdown_to_docx_using_aspose(markdown_text):
    """
    Convert a markdown text to a DOCX file using Aspose.Words.
    
    Args:
        markdown_text (str): The markdown text to be converted to DOCX.
        
    Returns:
        aspose.words.Document: A DOCX file containing the formatted resume.
    """
    # Create a blank document.
    doc = aw.Document()

    # Use a document builder to add content to the document.
    builder = aw.DocumentBuilder(doc)

    # Split the markdown text into lines.
    lines = markdown_text.split("\n")

    for line in lines:
        line = line.strip()

        if line.startswith("###"):  # Heading level 3
            builder.paragraph_format.style_identifier = aw.StyleIdentifier.HEADING_3
            builder.writeln(line.replace("###", "").strip())
        elif line.startswith("##"):  # Heading level 2
            builder.paragraph_format.style_identifier = aw.StyleIdentifier.HEADING_2
            builder.writeln(line.replace("##", "").strip())
        elif line.startswith("* "):  # Bullet point
            builder.paragraph_format.style_identifier = aw.StyleIdentifier.LIST_PARAGRAPH
            builder.writeln(line.replace("* ", "").strip())
        elif "**" in line:  # Bold text
            parts = line.split("**")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Bold part
                    builder.bold = True
                    builder.write(part)
                    builder.bold = False
                else:
                    builder.write(part)
            builder.writeln("")
        else:
            builder.paragraph_format.style_identifier = aw.StyleIdentifier.NORMAL
            builder.writeln(line)

    return doc


def convert_aspose_doc_to_bytes(doc):
    """
    Convert an Aspose.Words Document object to bytes for file download.
    
    Args:
        doc (aspose.words.Document): The docx file as a Document object.
        
    Returns:
        io.BytesIO: The docx file in bytes.
    """
    docx_buffer = io.BytesIO()
    doc.save(docx_buffer, aw.SaveFormat.DOCX)
    docx_buffer.seek(0)
    return docx_buffer
