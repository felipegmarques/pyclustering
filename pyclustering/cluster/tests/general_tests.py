"""!

@brief Unit-tests for other cluster functionality

@authors Andrei Novikov (pyclustering@yandex.ru)
@date 2014-2016
@copyright GNU Public License

@cond GNU_PUBLIC_LICENSE
    PyClustering is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    PyClustering is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
@endcond

"""

import unittest;

# Generate images without having a window appear.
import matplotlib;
matplotlib.use('Agg');

from pyclustering.samples.definitions import SIMPLE_SAMPLES, FCPS_SAMPLES;

from pyclustering.utils import read_sample;

from pyclustering.cluster import cluster_visualizer;
from pyclustering.cluster.dbscan import dbscan;


class Test(unittest.TestCase):
    def testVisualize3DClustersOneCanvas(self):
        sample = read_sample(FCPS_SAMPLES.SAMPLE_HEPTA);
         
        dbscan_instance = dbscan(sample, 0.5, 3, True);
        dbscan_instance.process();
        clusters = dbscan_instance.get_clusters();
         
        visualizer = cluster_visualizer();
        visualizer.append_clusters(clusters, sample, markersize = 30);
        visualizer.show();
     
    def testVisualize3DClustersTwoCanvases(self):
        sample_tetra = read_sample(FCPS_SAMPLES.SAMPLE_TETRA);
        sample_hepta = read_sample(FCPS_SAMPLES.SAMPLE_HEPTA);
             
        # Two canvas visualization
        visualizer = cluster_visualizer(2);
        visualizer.append_clusters([ sample_tetra ], None, 0, markersize = 30);
        visualizer.append_clusters([ sample_hepta ], None, 1, markersize = 30);
        visualizer.show();
     
    def testVisualize2DClustersOneCanvas(self):
        sample = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE4);
         
        dbscan_instance = dbscan(sample, 0.7, 3, False);
        dbscan_instance.process();
        clusters = dbscan_instance.get_clusters();
         
        visualizer = cluster_visualizer();
        visualizer.append_clusters(clusters, sample, markersize = 5);
        visualizer.show();
         
    def testVisualize2DClustersThreeCanvases(self):
        sample_simple1 = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE1);
        sample_simple2 = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE2);
        sample_simple3 = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE3);
             
        dbscan_instance = dbscan(sample_simple1, 0.4, 2, False);
        dbscan_instance.process();
        clusters_sample1 = dbscan_instance.get_clusters();
             
        dbscan_instance = dbscan(sample_simple2, 1, 2, False);
        dbscan_instance.process();
        clusters_sample2 = dbscan_instance.get_clusters();
     
        dbscan_instance = dbscan(sample_simple3, 0.7, 3, False);
        dbscan_instance.process();
        clusters_sample3 = dbscan_instance.get_clusters();
             
        visualizer = cluster_visualizer(3);
        visualizer.append_clusters(clusters_sample1, sample_simple1, 0, markersize = 5);
        visualizer.append_clusters(clusters_sample2, sample_simple2, 1, markersize = 5);
        visualizer.append_clusters(clusters_sample3, sample_simple3, 2, markersize = 5);
        visualizer.show();
     
    def testVisualize2DAnd3DClusters(self):
        sample_2d = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE1);
        sample_3d = read_sample(FCPS_SAMPLES.SAMPLE_HEPTA);
         
        visualizer = cluster_visualizer(2, 2);
        visualizer.append_clusters([ sample_2d ], None, 0, markersize = 5);
        visualizer.append_clusters([ sample_3d ], None, 1, markersize = 30);
        visualizer.show();
    
    def testVisualizeRectangeRepresentation2x2(self):
        sample_simple1 = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE1);
        sample_simple2 = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE2);
        sample_simple3 = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE3);
          
        visualizer = cluster_visualizer(3, 2);
        visualizer.append_clusters([ sample_simple1 ], None, 0, markersize = 5);
        visualizer.append_clusters([ sample_simple2 ], None, 1, markersize = 5);
        visualizer.append_clusters([ sample_simple3 ], None, 2, markersize = 5);
        visualizer.show();
    
    def testVisualizeRectangeRepresentation3x5(self):
        visualizer = cluster_visualizer(15, 5);
        
        for i in range(15):
            sample = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE1);
            visualizer.append_clusters([ sample ], None, i, markersize = 5);
        
        visualizer.show();

if __name__ == "__main__":
    unittest.main();