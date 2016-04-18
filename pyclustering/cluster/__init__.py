"""!

@brief pyclustering module for cluster analysis.

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

import matplotlib.pyplot as plt;
import matplotlib.gridspec as gridspec;

import math;


class canvas_cluster_descr:
    """!
    @brief Description of cluster for representation on canvas.
    
    """

    def __init__(self, cluster, data, marker, markersize):
        """!
        @brief Constructor of cluster representation on the canvas.
        
        @param[in] cluster (list): Single cluster that consists of objects or indexes from data.
        @param[in] data (list): Objects that should be displayed, can be None if clusters consist of objects instead of indexes.
        @param[in] marker (string): Type of marker that is used for drawing objects.
        @param[in] markersize (uint): Size of marker that is used for drawing objects.
        
        """
        ## Cluster that may consist of objects or indexes of objects from data.
        self.cluster = cluster;
        
        ## Data where objects are stored. It can be None if clusters consist of objects instead of indexes.
        self.data = data;
        
        ## Marker that is used for drawing objects.
        self.marker = marker;
        
        ## Size of marker that is used for drawing objects.
        self.markersize = markersize;
    

class cluster_visualizer:
    """!
    @brief Common visualizer of clusters on 2D or 3D surface.
    
    """
    
    __colors = [ 'red', 'blue', 'darkgreen', 'brown', 'violet', 
                 'deepskyblue', 'darkgrey', 'lightsalmon', 'deeppink', 'yellow',
                 'black', 'mediumspringgreen', 'orange', 'darkviolet', 'darkblue',
                 'silver', 'lime', 'pink', 'gold', 'bisque' ];
    

    def __init__(self, number_canvases = 1, size_row = 1):
        """!
        @brief Constructor of cluster visualizer.
        
        @param[in] number_canvases (uint): Number of canvases that is used for visualization.
        @param[in] size_row (uint): Amount of canvases that can be placed in one row.
        
        Example:
        @code
            # load 2D data sample
            sample_2d = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE1);
            
            # load 3D data sample
            sample_3d = read_sample(FCPS_SAMPLES.SAMPLE_HEPTA);
            
            # extract clusters from the first sample using DBSCAN algorithm
            dbscan_instance = dbscan(sample_2d, 0.4, 2, False);
            dbscan_instance.process();
            clusters_sample_2d = dbscan_instance.get_clusters();
        
            # extract clusters from the second sample using DBSCAN algorithm
            dbscan_instance = dbscan(sample_3d, 1, 3, True);
            dbscan_instance.process();
            clusters_sample_3d = dbscan_instance.get_clusters();
            
            # create plot with two canvases where each row contains 2 canvases.
            size = 2;
            row_size = 2;
            visualizer = cluster_visualizer(size, row_size);
            
            # place clustering result of sample_2d to the first canvas
            visualizer.append_clusters(clusters_sample_2d, sample_2d, 0, markersize = 5);
            
            # place clustering result of sample_3d to the second canvas
            visualizer.append_clusters(clusters_sample_3d, sample_3d, 1, markersize = 30);
            
            # show plot
            visualizer.show();
        @endcode
        
        """
        
        self.__number_canvases = number_canvases;
        self.__size_row = size_row;
        self.__canvas_clusters = [ [] for i in range(number_canvases) ];
        self.__canvas_dimensions = [ None for i in range(number_canvases) ];
        self.__canvas_titles = [ None for i in range(number_canvases) ];
        
        self.__default_2d_marker_size = 5;
        self.__default_3d_marker_size = 30;
    
    
    def append_cluster(self, cluster, data = None, canvas = 0, marker = '.', markersize = None):
        """!
        @brief Appends cluster to canvas for drawing.
        
        @param[in] cluster (list): cluster that may consist of indexes of objects from the data or object itself.
        @param[in] data (list): If defines that each element of cluster is considered as a index of object from the data.
        @param[in] canvas (uint): Number of canvas that should be used for displaying cluster.
        @param[in] marker (string): Marker that is used for displaying objects from cluster on the canvas.
        @param[in] markersize (uint): Size of marker.
        
        """
        
        if (len(cluster) == 0):
            return;
        
        if (canvas > self.__number_canvases):
            raise NameError('Canvas does ' + canvas + ' not exists.');
        
        added_canvas_descriptor = canvas_cluster_descr(cluster, data, marker, markersize);
        self.__canvas_clusters[canvas].append( added_canvas_descriptor );
        if (len(self.__canvas_clusters[canvas]) > len(self.__colors)):
            raise NameError('Not enough colors to display clusters.');
        
        dimension = 0;
        if (data is None):
            dimension = len(cluster[0]);
            if (self.__canvas_dimensions[canvas] is None):
                self.__canvas_dimensions[canvas] = dimension;
            elif (self.__canvas_dimensions[canvas] != dimension):
                raise NameError('Only clusters with the same dimension of objects can be displayed on canvas.');
                
        else:
            dimension = len(data[0]);
            if (self.__canvas_dimensions[canvas] is None):
                self.__canvas_dimensions[canvas] = dimension;
            elif (self.__canvas_dimensions[canvas] != dimension):
                raise NameError('Only clusters with the same dimension of objects can be displayed on canvas.');

        if ( (dimension < 1) and (dimension > 3) ):
            raise NameError('Only objects with size dimension 1 (1D plot), 2 (2D plot) or 3 (3D plot) can be displayed.');
        
        if (markersize is None):
            if (dimension == 2):
                added_canvas_descriptor.markersize = self.__default_2d_marker_size;
            elif (dimension == 3):
                added_canvas_descriptor.markersize = self.__default_3d_marker_size;
    
    
    def append_clusters(self, clusters, data = None, canvas = 0, marker = '.', markersize = None):
        """!
        @brief Appends list of cluster to canvas for drawing.
        
        @param[in] clusters (list): List of clusters where each cluster may consist of indexes of objects from the data or object itself.
        @param[in] data (list): If defines that each element of cluster is considered as a index of object from the data.
        @param[in] canvas (uint): Number of canvas that should be used for displaying clusters.
        @param[in] marker (string): Marker that is used for displaying objects from clusters on the canvas.
        @param[in] markersize (uint): Size of marker.
        
        """
            
        for cluster in clusters:
            self.append_cluster(cluster, data, canvas, marker, markersize);
    
    
    def set_canvas_title(self, text, canvas):
        """!
        @brief Set title for specified canvas.
        
        @param[in] text (string): Title for canvas.
        @param[in] canvas (uint): Index of canvas where title should be displayed.
        
        """
        
        if (canvas > self.__number_canvases):
            raise NameError('Canvas does ' + canvas + ' not exists.');
        
        self.__canvas_titles[canvas] = text;
            
    
    
    def show(self, visible_axis = True, visible_grid = True):
        """!
        @brief Shows clusters (visualize).
        
        @param[in] visible_axis (bool): Defines visibility of axes on each canvas, if True - axes are invisible.
        @param[in] visible_grid (bool): Defines visibility of axes on each canvas, if True - grid is displayed.
        
        """
        
        maximum_cols = self.__size_row;
        maximum_rows = math.ceil(self.__number_canvases / maximum_cols);
        
        grid_spec = gridspec.GridSpec(maximum_rows, maximum_cols);
        
        for index_canvas in range(len(self.__canvas_clusters)):
            canvas = self.__canvas_clusters[index_canvas];
            dimension = self.__canvas_dimensions[index_canvas];
            
            #ax = axes[real_index];
            if (dimension == 2):
                ax = plt.subplot(grid_spec[index_canvas]);
            else:
                ax = plt.subplot(grid_spec[index_canvas], projection='3d');
            
            if (len(canvas) == 0):
                plt.setp(ax, visible = False);
            
            for index_cluster in range(len(canvas)):
                cluster = canvas[index_cluster].cluster;
                data = canvas[index_cluster].data;
                marker = canvas[index_cluster].marker;
                markersize = canvas[index_cluster].markersize;
                color = self.__colors[index_cluster];
                
                for item in cluster:
                    if (dimension == 1):
                        if (data is None):
                            ax.plot(item[0], 0.0, color = color, marker = marker, markersize = markersize);
                        else:
                            ax.plot(data[item][0], 0.0, color = color, marker = marker, markersize = markersize);

                    if (dimension == 2):
                        if (data is None):
                            ax.plot(item[0], item[1], color = color, marker = marker, markersize = markersize);
                        else:
                            ax.plot(data[item][0], data[item][1], color = color, marker = marker, markersize = markersize);
                
                    elif (dimension == 3):
                        if (data is None):
                            ax.scatter(item[0], item[1], item[2], c = color, marker = marker, s = markersize);
                        else:
                            ax.scatter(data[item][0], data[item][1], data[item][2], c = color, marker = marker, s = markersize);
                            
            if (visible_axis is True):
                ax.xaxis.set_ticklabels([]);
                ax.yaxis.set_ticklabels([]);
                
                if (dimension == 3):
                    ax.zaxis.set_ticklabels([]);
            
            if (self.__canvas_titles[index_canvas] is not None):
                ax.set_title(self.__canvas_titles[index_canvas]);
            
            ax.grid(visible_grid);
        
        plt.show();

    