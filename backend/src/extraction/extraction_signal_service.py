import re
from typing import Dict, List, Any

class ExtractionSignalService:
    @staticmethod
    def extract_signals(text: str) -> Dict[str, Any]:
        """
        Analyzes text to extract signals for sustainability profile fields.
        Returns a dictionary of signals found.
        """
        text_lower = text.lower()
        signals = {}
        
        # 1. Framework Mentions
        frameworks = {
            "brsr": r"\b(brsr|sebi)\b",
            "gri": r"\bgri\b",
            "tcfd": r"\btcfd\b",
            "ifrs_s1": r"\b(ifrs s1|ifrs s-1)\b",
            "ifrs_s2": r"\b(ifrs s2|ifrs s-2)\b",
            "csrd": r"\bcsrd\b",
            "esrs": r"\besrs\b",
            "cdp": r"\bcdp\b",
            "sbti": r"\bsbti\b",
            "ghg_protocol": r"\bghg protocol\b",
        }
        found_frameworks = []
        for fw, pattern in frameworks.items():
            match = re.search(pattern, text_lower)
            if match:
                snippet = ExtractionSignalService._get_snippet(text, match.start())
                found_frameworks.append({"framework": fw, "snippet": snippet})
        
        signals["frameworks"] = found_frameworks

        # 2. Certifications
        certs = {
            "iso-14001": r"\biso[\s-]?14001\b",
            "iso-50001": r"\biso[\s-]?50001\b",
            "iso-45001": r"\biso[\s-]?45001\b",
            "iso-9001": r"\biso[\s-]?9001\b",
            "iso-14064": r"\biso[\s-]?14064\b"
        }
        found_certs = []
        for cert, pattern in certs.items():
            match = re.search(pattern, text_lower)
            if match:
                snippet = ExtractionSignalService._get_snippet(text, match.start())
                found_certs.append({"cert": cert, "snippet": snippet})
                
        signals["certifications"] = found_certs

        # 3. Emissions Terms
        scope_1_2 = bool(re.search(r"scope 1.*?scope 2|scope 1 and (scope )?2", text_lower))
        scope_3 = bool(re.search(r"scope 3", text_lower))
        
        if scope_1_2 or scope_3:
            match = re.search(r"scope [123]", text_lower)
            signals["emissions"] = {
                "scope_1_2": scope_1_2,
                "scope_3": scope_3,
                "snippet": ExtractionSignalService._get_snippet(text, match.start() if match else 0)
            }

        # 4. Energy Terms
        energy_match = re.search(r"\b(energy consumption|electricity use|energy intensity|mwh|gwh)\b", text_lower)
        if energy_match:
            signals["energy"] = {
                "mentioned": True,
                "snippet": ExtractionSignalService._get_snippet(text, energy_match.start())
            }

        # 5. Goals
        goals_map = {
            "net-zero": r"\b(net zero|net-zero)\b",
            "sbti": r"\b(science based target|sbti)\b",
            "renewables": r"\b(100% renewable|re100|shift to renewable)\b",
            "sdg": r"\b(sdg|sustainable development goal)\b"
        }
        found_goals = []
        for goal, pattern in goals_map.items():
            match = re.search(pattern, text_lower)
            if match:
                snippet = ExtractionSignalService._get_snippet(text, match.start())
                found_goals.append({"goal": goal, "snippet": snippet})
        signals["goals"] = found_goals

        # 6. Operational & Industry Clues
        manufacturing_match = re.search(r"\b(manufacturing plants|factories|production facilities)\b", text_lower)
        if manufacturing_match:
            signals["operations"] = {
                "type": "manufacturing",
                "snippet": ExtractionSignalService._get_snippet(text, manufacturing_match.start())
            }

        supply_chain_match = re.search(r"\b(supplier audits|supply chain|procurement sustainability|vendor code)\b", text_lower)
        if supply_chain_match:
            signals["supply_chain"] = {
                "mentioned": True,
                "snippet": ExtractionSignalService._get_snippet(text, supply_chain_match.start())
            }

        # 7. Assurance
        assurance_match = re.search(r"\b(limited assurance|reasonable assurance|independent assurance)\b", text_lower)
        if assurance_match:
            signals["assurance"] = {
                "mentioned": True,
                "snippet": ExtractionSignalService._get_snippet(text, assurance_match.start())
            }

        return signals

    @staticmethod
    def _get_snippet(text: str, index: int, window: int = 150) -> str:
        """Helper to get a window of text around a match."""
        start = max(0, index - window // 2)
        end = min(len(text), index + window // 2)
        snippet = text[start:end]
        # Clean up newlines and excessive spaces
        snippet = re.sub(r'\s+', ' ', snippet).strip()
        return f"...{snippet}..."
