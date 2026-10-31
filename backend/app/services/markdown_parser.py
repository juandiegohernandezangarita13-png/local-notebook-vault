import re
from typing import Dict, List, Any

def parse_markdown_metadata(content: str) -> Dict[str, Any]:
    # Extraer enlaces estilo [[enlace]]
    wikilinks = re.findall(r"\[\[(.*?)\]\]", content)
    
    # Extraer tags estilo #etiqueta
    tags = re.findall(r"(?:^|\s)#([a-zA-Z0-9_\-]+)", content)
    
    # Extraer título de primer nivel si existe
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Sin título"
    
    return {
        "title": title,
        "wikilinks": list(set(wikilinks)),
        "tags": list(set(tags)),
        "word_count": len(content.split())
    }
