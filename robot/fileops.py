# # **** File Handling ****

# import sys # To find out what platform we are running on.
# import paths

# # These globals must change for a PC.  They are MAC-biased :)

# def get_correct_slash():
#     if sys.platform == "darwin" or sys.platform == "linux2":
#         return "/"
#     elif sys.platform == "win32" or sys.platform == "win64":
#         return "\\"

# # The double-slash for PC's is really a single slash, since the first one acts as an escape
# _kd_path_slash_ = get_correct_slash()

# # This is (hopefully) the only thing that is user-specific

# #_kd_basepath_ = "C:\\Users\\kaiolae\\PycharmProjects\\SEVANN_project\\"
# #_kd_basepath_ = "/Users/keithd/core/python/"
# _kd_basepath_ = paths._kd_basepath_
# _sevann_basepath_ = paths._sevann_basepath_


# # Each dictionary entry = key + (file-extension, default-file-path(from _kd_basepath_)
# _file_dir_library_ = {"evann_topo": ["eas", "sevann specs topology"], "evann_sys": ["eva", "sevann specs system"],\
#                       "gene_spec": ["gsp", "sevann specs gene"], "niomap": ["nio", "sevann specs niomap"],\
#                       "evann_dataset": ["dat", "SEVANN data datasets"], "evann_weight": ["wgt", "SEVANN data weights"],\
#                       "evann_ann":  ["ann", "SEVANN data anns"], \
#                       "probe_data": ["dat", "sevann data probed"], "probe_results": ["pdf", "sevann results probed"],
#                         "evann_individuals": ["evi", "sevann results individuals"],
#                       "network":  ["txt", "data carpoints"], "gifage": ['gif',"data images"],
#                       "jpage": ['jpg',"data images"], "grid": ['grd',"data grids"],
#                       "texage": ['txt',"data images"], "nlp": ['txt', "data nlp"]}
# # Above:  The "age" names (gifage,jpage,texage) refer to imAGE files in different formats.
# _sevann_code_dirs_ = [ ["code","genetic"],  ["code", "neural"],  ["code", "prims"],  ["code", "gui"],  ["code", "dataset"],
#                ["code", "plotting"], ["code", "sevann_api"]]

# def build_default_file_path(filename, type, extension=None):
#     spec = _file_dir_library_[type]
#     path = _kd_basepath_
#     for directory in spec[1].split(): path += (directory + _kd_path_slash_)
#     suffix = "." + (extension if extension else spec[0])
#     return path + filename + suffix

# # When running SEVANN, this adds important directories to PYTHONPATH.
# def add_sevann_code_dirs():
#     slash = _kd_path_slash_
#     dirs_list = _sevann_code_dirs_
#     for dirs in dirs_list:
#         path = _sevann_basepath_
#         for dir in dirs: path += (dir + slash)
#         sys.path.append(path) # adds to PYTHONPATH
    


# def file_path_p(str):
#     if str.find(_kd_path_slash_) >= 0:
#         return True
#     else: return False

# def strip_filepath_prefix_dots(str):
# 	while str[0:3] == '..' + _kd_path_slash_:
# 		str = str[3:]
# 	return str

# def complete_file_path(fid, type):
#     if file_path_p(fid):
#         return fid # which is assumed to be a complete path due to presence of a slash
#     else:
#         return build_default_file_path(fid, type)

# # NOTE:  This is CALLED the FIRST time this file is imported
# add_sevann_code_dirs()
