from unittest import TestCase
from utilities.slippy_maps import degree_to_tile_number, tile_number_to_degree, tile_bounds, project_point


class TestSlippyMaps(TestCase):
    def test_convert_degree_to_tile(self):
        self.assertEqual(degree_to_tile_number(0, 0, 0), (0, 0))
        self.assertEqual(degree_to_tile_number(0, 0, 1), (1, 1))
        self.assertEqual(degree_to_tile_number(0.000001, 0.000001, 1), (1, 0))

    def test_convert_tile_to_degree(self):
        self.assertEqual(tile_number_to_degree(1, 1, 1), (0, 0))
        self.assertEqual(tile_number_to_degree(2, 2, 2), (0, 0))
        self.assertEqual(tile_number_to_degree(0, 0, 2), (85.0511287798066,-180))
        self.assertEqual(tile_number_to_degree(0, 0, 4), (85.0511287798066,-180))
        self.assertEqual(tile_number_to_degree(0, 8, 4), (0,-180))

    def test_bounds(self):
        self.assertEqual(tile_bounds(1,1,1), ((0.0, 0.0), (-85.0511287798066, 180.0)))

    def test_project_point(self):
        pass
