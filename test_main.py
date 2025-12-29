import unittest
from unittest.mock import patch
from main import main

class TestMain(unittest.TestCase):

    @patch('os.system')
    def test_main(self, mock_system):
        main()
        mock_system.assert_called_once_with('streamlit run streamlit_app.py')

if __name__ == '__main__':
    unittest.main()
