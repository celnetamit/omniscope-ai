"""
Citation Manager for Report Generation
Handles bibliography database and citation formatting in multiple styles
"""

from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
import re

CitationStyle = Literal["APA", "MLA", "Chicago", "Nature", "Science"]

class Citation:
    """Model for a single citation"""
    
    def __init__(
        self,
        citation_id: str,
        authors: List[str],
        year: int,
        title: str,
        journal: Optional[str] = None,
        volume: Optional[str] = None,
        issue: Optional[str] = None,
        pages: Optional[str] = None,
        doi: Optional[str] = None,
        url: Optional[str] = None,
        publisher: Optional[str] = None,
        book_title: Optional[str] = None,
        citation_type: str = "article"
    ):
        self.citation_id = citation_id
        self.authors = authors
        self.year = year
        self.title = title
        self.journal = journal
        self.volume = volume
        self.issue = issue
        self.pages = pages
        self.doi = doi
        self.url = url
        self.publisher = publisher
        self.book_title = book_title
        self.citation_type = citation_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert citation to dictionary"""
        return {
            "citation_id": self.citation_id,
            "authors": self.authors,
            "year": self.year,
            "title": self.title,
            "journal": self.journal,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "doi": self.doi,
            "url": self.url,
            "publisher": self.publisher,
            "book_title": self.book_title,
            "citation_type": self.citation_type
        }


class CitationManager:
    """
    Citation manager for handling bibliography and formatting
    
    Requirements: 5.3
    """
    
    def __init__(self, style: CitationStyle = "APA"):
        """
        Initialize citation manager
        
        Args:
            style: Citation style (APA, MLA, Chicago, Nature, Science)
        """
        self.style = style
        self.citations: Dict[str, Citation] = {}
        self.citation_order: List[str] = []
    
    def add_citation(self, citation: Citation) -> str:
        """
        Add a citation to the bibliography
        
        Args:
            citation: Citation object
            
        Returns:
            Citation ID
        """
        if citation.citation_id not in self.citations:
            self.citations[citation.citation_id] = citation
            self.citation_order.append(citation.citation_id)
        return citation.citation_id
    
    def add_citation_from_dict(self, citation_data: Dict[str, Any]) -> str:
        """
        Add a citation from dictionary data
        
        Args:
            citation_data: Dictionary containing citation information
            
        Returns:
            Citation ID
        """
        citation = Citation(**citation_data)
        return self.add_citation(citation)
    
    def get_citation(self, citation_id: str) -> Optional[Citation]:
        """Get a citation by ID"""
        return self.citations.get(citation_id)
    
    def remove_citation(self, citation_id: str):
        """Remove a citation from the bibliography"""
        if citation_id in self.citations:
            del self.citations[citation_id]
            self.citation_order.remove(citation_id)
    
    def format_citation(self, citation_id: str, style: Optional[CitationStyle] = None) -> str:
        """
        Format a single citation in the specified style
        
        Args:
            citation_id: ID of the citation to format
            style: Citation style (uses manager's default if not specified)
            
        Returns:
            Formatted citation string
        """
        citation = self.citations.get(citation_id)
        if not citation:
            return ""
        
        style = style or self.style
        
        if style == "APA":
            return self._format_apa(citation)
        elif style == "MLA":
            return self._format_mla(citation)
        elif style == "Chicago":
            return self._format_chicago(citation)
        elif style == "Nature":
            return self._format_nature(citation)
        elif style == "Science":
            return self._format_science(citation)
        else:
            return self._format_apa(citation)
    
    def _format_authors(self, authors: List[str], style: CitationStyle, max_authors: int = None) -> str:
        """Format author list according to style"""
        if not authors:
            return "Unknown"
        
        if style == "APA":
            if len(authors) == 1:
                return authors[0]
            elif len(authors) == 2:
                return f"{authors[0]} & {authors[1]}"
            elif len(authors) <= 7:
                return ", ".join(authors[:-1]) + f", & {authors[-1]}"
            else:
                return f"{authors[0]} et al."
        
        elif style == "MLA":
            if len(authors) == 1:
                return authors[0]
            elif len(authors) == 2:
                return f"{authors[0]}, and {authors[1]}"
            else:
                return f"{authors[0]}, et al."
        
        elif style == "Chicago":
            if len(authors) == 1:
                return authors[0]
            elif len(authors) <= 3:
                return ", ".join(authors[:-1]) + f", and {authors[-1]}"
            else:
                return f"{authors[0]} et al."
        
        elif style in ["Nature", "Science"]:
            if len(authors) <= 5:
                return ", ".join(authors)
            else:
                return f"{authors[0]} et al."
        
        return ", ".join(authors)
    
    def _format_apa(self, citation: Citation) -> str:
        """Format citation in APA style"""
        authors = self._format_authors(citation.authors, "APA")
        year = citation.year
        title = citation.title
        
        if citation.citation_type == "article":
            journal = citation.journal or "Unknown Journal"
            formatted = f"{authors} ({year}). {title}. {journal}"
            
            if citation.volume:
                formatted += f", {citation.volume}"
                if citation.issue:
                    formatted += f"({citation.issue})"
            
            if citation.pages:
                formatted += f", {citation.pages}"
            
            if citation.doi:
                formatted += f". https://doi.org/{citation.doi}"
            
            formatted += "."
        
        elif citation.citation_type == "book":
            publisher = citation.publisher or "Unknown Publisher"
            formatted = f"{authors} ({year}). {title}. {publisher}."
        
        else:
            formatted = f"{authors} ({year}). {title}."
        
        return formatted
    
    def _format_mla(self, citation: Citation) -> str:
        """Format citation in MLA style"""
        authors = self._format_authors(citation.authors, "MLA")
        title = f'"{citation.title}"'
        
        if citation.citation_type == "article":
            journal = citation.journal or "Unknown Journal"
            formatted = f"{authors}. {title}. {journal}"
            
            if citation.volume:
                formatted += f", vol. {citation.volume}"
                if citation.issue:
                    formatted += f", no. {citation.issue}"
            
            formatted += f", {citation.year}"
            
            if citation.pages:
                formatted += f", pp. {citation.pages}"
            
            formatted += "."
        
        elif citation.citation_type == "book":
            publisher = citation.publisher or "Unknown Publisher"
            formatted = f"{authors}. {title}. {publisher}, {citation.year}."
        
        else:
            formatted = f"{authors}. {title}. {citation.year}."
        
        return formatted
    
    def _format_chicago(self, citation: Citation) -> str:
        """Format citation in Chicago style"""
        authors = self._format_authors(citation.authors, "Chicago")
        title = citation.title
        year = citation.year
        
        if citation.citation_type == "article":
            journal = citation.journal or "Unknown Journal"
            formatted = f"{authors}. {year}. \"{title}.\" {journal}"
            
            if citation.volume:
                formatted += f" {citation.volume}"
                if citation.issue:
                    formatted += f", no. {citation.issue}"
            
            if citation.pages:
                formatted += f": {citation.pages}"
            
            if citation.doi:
                formatted += f". https://doi.org/{citation.doi}"
            
            formatted += "."
        
        elif citation.citation_type == "book":
            publisher = citation.publisher or "Unknown Publisher"
            formatted = f"{authors}. {year}. {title}. {publisher}."
        
        else:
            formatted = f"{authors}. {year}. {title}."
        
        return formatted
    
    def _format_nature(self, citation: Citation) -> str:
        """Format citation in Nature style"""
        authors = self._format_authors(citation.authors, "Nature")
        title = citation.title
        
        if citation.citation_type == "article":
            journal = citation.journal or "Unknown Journal"
            formatted = f"{authors}. {title}. {journal}"
            
            if citation.volume:
                formatted += f" {citation.volume}"
            
            if citation.pages:
                formatted += f", {citation.pages}"
            
            formatted += f" ({citation.year})."
            
            if citation.doi:
                formatted += f" https://doi.org/{citation.doi}"
        
        elif citation.citation_type == "book":
            publisher = citation.publisher or "Unknown Publisher"
            formatted = f"{authors}. {title}. ({publisher}, {citation.year})."
        
        else:
            formatted = f"{authors}. {title} ({citation.year})."
        
        return formatted
    
    def _format_science(self, citation: Citation) -> str:
        """Format citation in Science style"""
        authors = self._format_authors(citation.authors, "Science")
        title = citation.title
        
        if citation.citation_type == "article":
            journal = citation.journal or "Unknown Journal"
            formatted = f"{authors}, {title}. {journal}"
            
            if citation.volume:
                formatted += f" {citation.volume}"
            
            if citation.pages:
                formatted += f", {citation.pages}"
            
            formatted += f" ({citation.year})."
        
        elif citation.citation_type == "book":
            publisher = citation.publisher or "Unknown Publisher"
            formatted = f"{authors}, {title} ({publisher}, {citation.year})."
        
        else:
            formatted = f"{authors}, {title} ({citation.year})."
        
        return formatted
    
    def get_bibliography(self, style: Optional[CitationStyle] = None) -> List[str]:
        """
        Get formatted bibliography in the specified style
        
        Args:
            style: Citation style (uses manager's default if not specified)
            
        Returns:
            List of formatted citations
        """
        style = style or self.style
        bibliography = []
        
        for citation_id in self.citation_order:
            formatted = self.format_citation(citation_id, style)
            if formatted:
                bibliography.append(formatted)
        
        return bibliography
    
    def insert_citation(self, citation_id: str, in_text: bool = True) -> str:
        """
        Generate in-text citation reference
        
        Args:
            citation_id: ID of the citation
            in_text: Whether this is an in-text citation
            
        Returns:
            Formatted in-text citation
        """
        citation = self.citations.get(citation_id)
        if not citation:
            return "[?]"
        
        if self.style == "APA":
            if len(citation.authors) == 1:
                return f"({citation.authors[0].split()[-1]}, {citation.year})"
            elif len(citation.authors) == 2:
                last_names = [a.split()[-1] for a in citation.authors[:2]]
                return f"({last_names[0]} & {last_names[1]}, {citation.year})"
            else:
                return f"({citation.authors[0].split()[-1]} et al., {citation.year})"
        
        elif self.style == "MLA":
            if len(citation.authors) == 1:
                return f"({citation.authors[0].split()[-1]} {citation.pages or ''})"
            else:
                return f"({citation.authors[0].split()[-1]} et al. {citation.pages or ''})"
        
        elif self.style in ["Nature", "Science"]:
            # Numbered citations
            index = self.citation_order.index(citation_id) + 1
            return f"[{index}]"
        
        else:
            return f"({citation.authors[0].split()[-1]}, {citation.year})"
    
    def set_style(self, style: CitationStyle):
        """Change the citation style"""
        self.style = style
    
    def clear(self):
        """Clear all citations"""
        self.citations.clear()
        self.citation_order.clear()
    
    def export_bibtex(self) -> str:
        """Export bibliography in BibTeX format"""
        bibtex_entries = []
        
        for citation_id in self.citation_order:
            citation = self.citations[citation_id]
            
            entry_type = "article" if citation.citation_type == "article" else "book"
            entry = f"@{entry_type}{{{citation_id},\n"
            
            # Add authors
            authors_str = " and ".join(citation.authors)
            entry += f"  author = {{{authors_str}}},\n"
            
            # Add title
            entry += f"  title = {{{citation.title}}},\n"
            
            # Add year
            entry += f"  year = {{{citation.year}}},\n"
            
            # Add journal/publisher specific fields
            if citation.citation_type == "article":
                if citation.journal:
                    entry += f"  journal = {{{citation.journal}}},\n"
                if citation.volume:
                    entry += f"  volume = {{{citation.volume}}},\n"
                if citation.issue:
                    entry += f"  number = {{{citation.issue}}},\n"
                if citation.pages:
                    entry += f"  pages = {{{citation.pages}}},\n"
                if citation.doi:
                    entry += f"  doi = {{{citation.doi}}},\n"
            elif citation.citation_type == "book":
                if citation.publisher:
                    entry += f"  publisher = {{{citation.publisher}}},\n"
            
            entry += "}\n"
            bibtex_entries.append(entry)
        
        return "\n".join(bibtex_entries)
    
    def import_from_dict_list(self, citations_data: List[Dict[str, Any]]):
        """Import multiple citations from a list of dictionaries"""
        for citation_data in citations_data:
            self.add_citation_from_dict(citation_data)
