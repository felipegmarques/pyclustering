'''

Wrapper for CCORE library (part of this project).

Copyright (C) 2015    Andrei Novikov (spb.andr@yandex.ru)

pyclustering is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyclustering is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

from ctypes import *;

from pyclustering.core.definitions import *;


# API that is required for interaction with DLL.
def create_pointer_data(sample):
    "Allocates memory for representing input data for processing that is described by structure 'data_representation' and returns pointer this structure."
    
    "(in) sample    - dataset for processing."
    
    "Returns pointer to the data for processing."
    
    input_data = data_representation();
    input_data.number_objects = len(sample);
    input_data.dimension = len(sample[0]);
    
    pointer_objects = (POINTER(c_double) * input_data.number_objects)();
     
    for index in range(0, input_data.number_objects):
        point = (c_double * input_data.dimension)();
        for dimension in range(0, input_data.dimension):
            point[dimension] = sample[index][dimension];
            
        pointer_objects[index] = cast(point, POINTER(c_double));
       
    input_data.pointer_objects = cast(pointer_objects, POINTER(POINTER(c_double)));
    input_data = pointer(input_data);
    
    return input_data;


def extract_clusters(ccore_result):
    "Parse clustering result that is provided by the CCORE. Return Python list of clusters."
    
    "(in) ccore_result    - pointer to clustering result that has been returned by CCORE."
    
    "Returns Python list of clusters."
    
    pointer_clustering_result = cast(ccore_result, POINTER(clustering_result));    # clustering_result * clusters
    number_clusters = pointer_clustering_result[0].number_clusters;
    
    list_of_clusters = [];
    
    for index_cluster in range(0, number_clusters):
        clusters = cast(pointer_clustering_result[0].pointer_clusters, POINTER(cluster_representation));  # cluster_representation * cluster
        
        objects = cast(clusters[index_cluster].pointer_objects, POINTER(c_uint));   # cluster->objects (unsigned int *)
        
        list_of_clusters.append([]);
        pointer_container = list_of_clusters[index_cluster];

        for index_object in range(0, clusters[index_cluster].number_objects):
            pointer_container.append(objects[index_object]);
    
    return list_of_clusters;


def extract_dynamics(ccore_result):
    "Parse dynamic result that is provided by the CCORE. Return Python tuple that represent dynamics (times, dynamic)."
    
    "(in) ccore_result    - pointer to dynamic result that has been returned by CCORE."
    
    "Returns Python tuple dynamic (times, dynamic)."
    
    pointer_dynamic_result = cast(ccore_result, POINTER(dynamic_result));   # dynamic_result * pointer_dynamic_result
    size_dynamic = pointer_dynamic_result[0].size_dynamic;
    size_network = pointer_dynamic_result[0].size_network;
    
    pointer_time = cast(pointer_dynamic_result[0].times, POINTER(c_double));
    pointer_pointer_dynamic = cast(pointer_dynamic_result[0].dynamic, POINTER(POINTER(c_double)));
    
    times = [];
    dynamic = [];
    
    for index in range(0, size_dynamic):
        times.append(pointer_time[index]);
        dynamic.append([]);
        
        pointer_dynamic = cast(pointer_pointer_dynamic[index], POINTER(c_double));
        
        for object_dynamic in range(0, size_network):
            dynamic[index].append(pointer_dynamic[object_dynamic]);
        
    return (times, dynamic);

def extract_pyclustering_package(ccore_package_pointer):
    if (ccore_package_pointer == 0):
        return [];
    
    pointer_package = cast(ccore_package_pointer, POINTER(pyclustering_package));
    size = pointer_package[0].size;
    type_package = pointer_package[0].type;
    
    result = [];
    pointer_data = None;
    
    if (type_package == pyclustering_type_data.PYCLUSTERING_TYPE_INT):
        pointer_data = cast(pointer_package[0].data, POINTER(c_int));
    
    elif (type_package == pyclustering_type_data.PYCLUSTERING_TYPE_UNSIGNED_INT):
        pointer_data = cast(pointer_package[0].data, POINTER(c_uint));
    
    elif (type_package == pyclustering_type_data.PYCLUSTERING_TYPE_FLOAT):
        pointer_data = cast(pointer_package[0].data, POINTER(c_float));
    
    elif (type_package == pyclustering_type_data.PYCLUSTERING_TYPE_DOUBLE):
        pointer_data = cast(pointer_package[0].data, POINTER(c_double));
    
    elif (type_package == pyclustering_type_data.PYCLUSTERING_TYPE_LONG):
        pointer_data = cast(pointer_package[0].data, POINTER(c_long));
    
    elif (type_package == pyclustering_type_data.PYCLUSTERING_TYPE_UNSIGNED_LONG):
        pointer_data = cast(pointer_package[0].data, POINTER(c_ulong));
    
    elif (type_package == pyclustering_type_data.PYCLUSTERING_TYPE_LIST):
        # pointer_package[0].data == pyclustering_package **
        pointer_data = cast(pointer_package[0].data, POINTER(POINTER(pyclustering_package)));
        
        for index in range(0, size):
            pointer_package = cast(pointer_data[index], (POINTER(pyclustering_package)));
            result.append(extract_pyclustering_package(pointer_package));

    else:
        assert(0);
    
    if (type_package != pyclustering_type_data.PYCLUSTERING_TYPE_LIST):
        for index in range(0, size):
            result.append(pointer_data[index]);
    
    return result;
    

# Implemented algorithms.
def dbscan(sample, eps, min_neighbors, return_noise = False):
    "Clustering algorithm DBSCAN returns allocated clusters and noise that are consisted from input data. Calculation is performed via CCORE."
    
    "(in) data            - input data that is presented as list of points (objects), each point should be represented by list or tuple."
    "(in) eps             - connectivity radius between points, points may be connected if distance between them less then the radius."
    "(in) min_neighbors   - minimum number of shared neighbors that is requied for establish links between points."
    "(in) return_noise    - if True than list of points that have been marked as noise will be returned."
    
    "If return_noise is False: Returns list of allocated clusters, each cluster contains indexes of objects in list of data."
    "If return_noise is True: Returns tuple of list of allicated clusters and list of points that are marked as noise."
    
    pointer_data = create_pointer_data(sample);
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    result = ccore.dbscan_algorithm(pointer_data, c_double(eps), c_uint(min_neighbors));

    list_of_clusters = extract_clusters(result);
    ccore.free_clustering_result(result);
    
    noise = list_of_clusters[len(list_of_clusters) - 1];
    list_of_clusters.remove(noise);
    
    if (return_noise is True):
        return (list_of_clusters, noise);
    else:
        return list_of_clusters;

def cure(sample, number_clusters, number_represent_points, compression):    
    pointer_data = create_pointer_data(sample);
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    result = ccore.cure_algorithm(pointer_data, c_uint(number_clusters), c_uint(number_represent_points), c_double(compression));
    
    list_of_clusters = extract_clusters(result);
    
    ccore.free_clustering_result(result);
    return list_of_clusters;

def hierarchical(sample, number_clusters):
    "Clustering algorithm hierarchical returns allocated clusters and noise that are consisted from input data. Calculation is performed via CCORE."
    
    "(in) data               - input data that is presented as list of points (objects), each point should be represented by list or tuple."
    "(in) number_clusters    - number of cluster that should be allocated."
    
    "Returns list of allocated clusters, each cluster contains indexes of objects in list of data."
    
    pointer_data = create_pointer_data(sample);
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    result = ccore.hierarchical_algorithm(pointer_data, c_uint(number_clusters));
    
    list_of_clusters = extract_clusters(result);
    
    ccore.free_clustering_result(result);
    return list_of_clusters;


def kmeans(sample, centers, tolerance):
    "Clustering algorithm K-Means returns allocated clusters. Calculation is performed via CCORE."
    
    "(in) data        - input data that is presented as list of points (objects), each point should be represented by list or tuple."
    "(in) centers     - initial coordinates of centers of clusters that are represented by list: [center1, center2, ...]."
    "(in) tolerance   - stop condition: if maximum value of change of centers of clusters is less than tolerance than algorithm will stop processing."
    
    "Returns list of allocated clusters, each cluster contains indexes of objects in list of data."
    
    pointer_data = create_pointer_data(sample);
    pointer_centers = create_pointer_data(centers);
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    result = ccore.kmeans_algorithm(pointer_data, pointer_centers, c_double(tolerance));
    
    list_of_clusters = extract_clusters(result);
    
    ccore.free_clustering_result(result);
    return list_of_clusters;


def rock(sample, eps, number_clusters, threshold):
    "Clustering algorithm ROCK returns allocated clusters and noise that are consisted from input data. Calculation is performed via CCORE."
    
    "(in) data                - input data - list of points where each point is represented by list of coordinates."
    "(in) eps                 - connectivity radius (similarity threshold), points are neighbors if distance between them is less than connectivity radius."
    "(in) number_clusters     - defines number of clusters that should be allocated from the input data set."
    "(in) threshold           - value that defines degree of normalization that influences on choice of clusters for merging during processing."
    
    "Returns list of allocated clusters, each cluster contains indexes of objects in list of data."
    
    pointer_data = create_pointer_data(sample);
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    result = ccore.rock_algorithm(pointer_data, c_double(eps), c_uint(number_clusters), c_double(threshold));
    
    list_of_clusters = extract_clusters(result);
    
    ccore.free_clustering_result(result);
    return list_of_clusters;    


def xmeans(sample, centers, kmax, tolerance):
    "Clustering algorithm X-Means returns allocated clusters. Calculation is performed via CCORE."
    
    "(in) data        - input data that is presented as list of points (objects), each point should be represented by list or tuple."
    "(in) centers     - initial coordinates of centers of clusters that are represented by list: [center1, center2, ...]."
    "(in) kmax        - maximum number of clusters that can be allocated."
    
    "Returns list of allocated clusters, each cluster contains indexes of objects in list of data."
    
    pointer_data = create_pointer_data(sample);
    pointer_centers = create_pointer_data(centers);
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    result = ccore.xmeans_algorithm(pointer_data, pointer_centers, c_uint(kmax), c_double(tolerance));
    
    list_of_clusters = extract_clusters(result);
    
    ccore.free_clustering_result(result);
    return list_of_clusters;


"CCORE Interface for SYNC oscillatory network"

def create_sync_network(num_osc, weight, frequency, type_conn, initial_phases):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    pointer_network = ccore.create_sync_network(c_uint(num_osc), c_double(weight), c_double(frequency), c_uint(type_conn), c_uint(initial_phases));
    
    return pointer_network;


def destroy_sync_network(pointer_network):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore.destroy_sync_network(pointer_network);


def simulate_sync_network(pointer_network, steps, time, solution, collect_dynamic):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore_dynamic_result = ccore.simulate_sync_network(pointer_network, c_uint(steps), c_double(time), c_uint(solution), c_bool(collect_dynamic));
    
    python_dynamic_result = extract_dynamics(ccore_dynamic_result);
    ccore.free_dynamic_result(ccore_dynamic_result);
    
    return python_dynamic_result;


def simulate_dynamic_sync_network(pointer_network, order, solution, collect_dynamic, step, int_step, threshold_changes):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore_dynamic_result = ccore.simulate_dynamic_sync_network(pointer_network, c_double(order), c_uint(solution), c_bool(collect_dynamic), c_double(step), c_double(int_step), c_double(threshold_changes));
    
    python_dynamic_result = extract_dynamics(ccore_dynamic_result);
    ccore.free_dynamic_result(ccore_dynamic_result);
    
    return python_dynamic_result;    


def allocate_sync_ensembles_sync_network(pointer_network, tolerance):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore_cluster_result = ccore.allocate_sync_ensembles_sync_network(pointer_network, c_double(tolerance));
    
    list_of_clusters = extract_clusters(ccore_cluster_result);
    
    ccore.free_clustering_result(ccore_cluster_result);
    return list_of_clusters; 


def sync_order(pointer_network):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore.sync_order.restype = c_double;
    
    return ccore.sync_order(pointer_network);
    
    
def sync_local_order(pointer_network):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore.sync_local_order.restype = c_double;
    
    return ccore.sync_local_order(pointer_network);


"CCORE Interface for SYNCNET oscillatory network"

def create_syncnet_network(sample, radius, initial_phases, enable_conn_weight):
    pointer_data = create_pointer_data(sample);
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    pointer_network = ccore.create_syncnet_network(pointer_data, c_double(radius), c_uint(initial_phases), c_bool(enable_conn_weight));
    
    return pointer_network;


def destroy_syncnet_network(pointer_network):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore.destroy_syncnet_network(pointer_network);


def process_syncnet(network_pointer, order, solution, collect_dynamic):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore_dynamic_result = ccore.process_syncnet(network_pointer, c_double(order), c_uint(solution), c_bool(collect_dynamic));

    python_dynamic_result = extract_dynamics(ccore_dynamic_result);
    ccore.free_dynamic_result(ccore_dynamic_result);
    
    return python_dynamic_result;    


def get_clusters_syncnet(pointer_network, tolerance):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore_cluster_result = ccore.get_clusters_syncnet(pointer_network, c_double(tolerance));
    
    list_of_clusters = extract_clusters(ccore_cluster_result);
    
    ccore.free_clustering_result(ccore_cluster_result);
    return list_of_clusters; 


"CCORE Interface for HSYNCNET oscillatory network"

def create_hsyncnet(sample, number_clusters, initial_phases):
    pointer_data = create_pointer_data(sample);
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    pointer_network = ccore.create_hsyncnet(pointer_data, c_uint(number_clusters), c_uint(initial_phases));
    
    return pointer_network;


def destroy_hsyncnet_network(pointer_network):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore.destroy_hsyncnet_network(pointer_network);


def process_hsyncnet(network_pointer, order, solution, collect_dynamic):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore_dynamic_result = ccore.process_hsyncnet(network_pointer, c_double(order), c_uint(solution), c_bool(collect_dynamic));

    python_dynamic_result = extract_dynamics(ccore_dynamic_result);
    ccore.free_dynamic_result(ccore_dynamic_result);
    
    return python_dynamic_result;  


def destroy_object(pointer_object):
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore.destroy_object(pointer_object);
    

"CCORE Interface for self-organized feature map (SOM)"
    
def som_create(data, rows, cols, epochs, conn_type, init_type):
    "Constructor of self-organized map."
    
    "(in) data        - input data - list of points where each point is represented by list of features, for example coordinates."
    "(in) rows        - number of neurons in the column (number of rows)."
    "(in) cols        - number of neurons in the row (number of columns)."
    "(in) epochs      - number of epochs for training."
    "(in) conn_type   - type of connection between oscillators in the network (grid four, grid eight, honeycomb, function neighbour)."
    "(in) init_type   - type of initialization of initial neuron weights (random, random in center of the input data, random distributed in data, ditributed in line with uniform grid)."    
    
    pointer_data = create_pointer_data(data);
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    som_pointer = ccore.som_create(pointer_data, c_uint(rows), c_uint(cols), c_uint(epochs), c_uint(conn_type), c_uint(init_type));
    
    return som_pointer;

def som_destroy(som_pointer):
    "Destructor of self-organized map."
    
    "(in) som_pointer    - pointer to object of self-organized map."
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    ccore.som_destroy(som_pointer);
    
def som_train(som_pointer, autostop):
    "Trains self-organized feature map (SOM)."
    
    "(in) som_pointer    - pointer to object of self-organized map."
    "(in) autostop       - automatic termination of learining process when adaptation is not occurred."   
     
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    return ccore.som_train(som_pointer, autostop);

def som_simulate(som_pointer, pattern):
    "Processes input pattern (no learining) and returns index of neuron-winner."
    "Using index of neuron winner catched object can be obtained using property capture_objects."
    
    "(in) som_pointer      - pointer to object of self-organized map."
    "(in) input_pattern    - input pattern."
        
    "Returns index of neuron-winner."
            
    pointer_data = create_pointer_data(pattern);
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    return ccore.som_simulate(som_pointer, pointer_data);

def som_get_winner_number(som_pointer):
    "Returns of number of winner at the last step of learning process."
    
    "(in) som_pointer    - pointer to object of self-organized map."
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    return ccore.som_get_winner_number(som_pointer);

def som_get_size(som_pointer):
    "Returns size of self-organized map (number of neurons)."
    
    "(in) som_pointer    - pointer to object of self-organized map."
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    return ccore.som_get_size(som_pointer);

def som_get_capture_objects(som_pointer):
    "Returns list of indexes of captured objects by each neuron."
    
    "(in) som_pointer    - pointer to object of self-organized map."
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    package = ccore.som_get_capture_objects(som_pointer);
    
    result = extract_pyclustering_package(package);
    return result;

def som_get_weights(som_pointer):
    "Returns list of weights of each neuron."
    
    "(in) som_pointer    - pointer to object of self-organized map."
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    package = ccore.som_get_weights(som_pointer);
    
    result = extract_pyclustering_package(package);
    return result;   

def som_get_awards(som_pointer):
    "Returns list of numbers of captured objects by each neuron."
    
    "(in) som_pointer    - pointer to object of self-organized map."
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    package = ccore.som_get_awards(som_pointer);
    
    result = extract_pyclustering_package(package);
    return result;  

def som_get_neighbors(som_pointer):
    "Returns list of indexes of neighbors of each neuron."
    
    "(in) som_pointer    - pointer to object of self-organized map."
    
    ccore = cdll.LoadLibrary(PATH_DLL_CCORE_WIN64);
    package = ccore.som_get_neighbors(som_pointer);
    
    result = extract_pyclustering_package(package);
    return result;  



# from pyclustering.support import draw_dynamics, draw_clusters, read_sample;
# from pyclustering.samples.definitions import SIMPLE_SAMPLES, FCPS_SAMPLES;
#   
# sample = read_sample(SIMPLE_SAMPLES.SAMPLE_SIMPLE3);
# som_pointer = som_create(sample, 1, 3, 100, 0, 3);
# iterations = som_train(som_pointer, False);
# 
# capture_objects = som_get_capture_objects(som_pointer);
# awards = som_get_awards(som_pointer);
# weights = som_get_weights(som_pointer);
# 
# print("Captured objects:", capture_objects);
# print("Awards:", awards);
# print("Weights:", weights);
# 
# som_destroy(som_pointer);
