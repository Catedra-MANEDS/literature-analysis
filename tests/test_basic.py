import sys
import unittest
from pathlib import Path

# Add project root to path to ensure modules are found
sys.path.append(str(Path(__file__).parent.parent))

from analysis import bibliography


class TestBibliographyAnalysis(unittest.TestCase):
    def test_argument_parser(self):
        """Test that arguments can be parsed (basic check)."""
        args = bibliography.parse_arguments([])
        # Test that arguments are parsed with defaults
        self.assertIsNotNone(args)
        self.assertIsNone(args.data_dir)
        self.assertFalse(args.save_plots)
        self.assertEqual(args.output_dir, "results")
        self.assertEqual(args.topic_keyword, "travel")

    def test_paths_exist(self):
        """Test that critical script paths are resolved correctly relative to the file."""
        base_dir = Path(bibliography.__file__).parent.resolve()
        self.assertTrue(base_dir.exists())
        self.assertTrue((base_dir / "data").exists())


if __name__ == "__main__":
    unittest.main()
