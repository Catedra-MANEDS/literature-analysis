import sys
import unittest
from pathlib import Path

# Add project root to path to ensure modules are found
sys.path.append(str(Path(__file__).parent.parent))

from analysis import bibliography


class TestBibliographyAnalysis(unittest.TestCase):
    def test_argument_parser(self):
        """Test that arguments can be parsed (basic check)."""
        parser = bibliography.parse_arguments()
        # We can't easily parse args here without mocking sys.argv,
        # but we can check the parser object exists.
        self.assertIsNotNone(parser)

    def test_paths_exist(self):
        """Test that critical script paths are resolved correctly relative to the file."""
        base_dir = Path(bibliography.__file__).parent.resolve()
        self.assertTrue(base_dir.exists())
        self.assertTrue((base_dir / "data").exists())


if __name__ == "__main__":
    unittest.main()
