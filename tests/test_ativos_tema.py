"""Teste TEXTUAL do Painel de ativos: o tema segue o sistema e as cores só vivem nas variáveis. Sem rede."""
import re
import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "monitor" / "ativos" / "index.html").read_text(encoding="utf-8")


class Tema(unittest.TestCase):
    def test_segue_o_sistema(self):
        self.assertIn("prefers-color-scheme: dark", HTML)
        self.assertIn("color-scheme:light", HTML)
        self.assertIn("color-scheme:dark", HTML)

    def test_cores_so_nas_variaveis(self):
        css = HTML[HTML.index("<style>"):HTML.index("</style>")]
        fora = re.sub(r":root \{[^}]*\}", "", css)
        fora = re.sub(r"@media \(prefers-color-scheme: dark\) \{\s*\}", "", fora)
        self.assertEqual(re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)", fora), [])

    def test_js_sem_cor_fixa(self):
        js = HTML[HTML.index("<script>"):]
        self.assertEqual(re.findall(r"#[0-9a-fA-F]{6}\b", js), [])


if __name__ == "__main__":
    unittest.main()
