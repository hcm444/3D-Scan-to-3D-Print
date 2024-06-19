import open3d as o3d
import numpy as np
import os
import glob
import pymeshfix

def convert_ply_to_stl(ply_files, output_dir, min_triangles=10000):
    for ply_file in ply_files:
        
        #Skip non ply files
        if not ply_file.lower().endswith('.ply'):
            print(f'Skipping "{ply_file}" because it is filetype: "{os.path.splitext(ply_file)[1]}"')
            continue
        
        # Load the mesh using Open3D
        mesh = o3d.io.read_triangle_mesh(ply_file)
        mesh.compute_vertex_normals()  # Compute normals before processing
        
        # Subdivide the mesh to increase the number of triangles
        while len(mesh.triangles) < min_triangles:
            mesh = mesh.subdivide_midpoint(number_of_iterations=1)
        
        # Clean up the mesh to make it watertight
        mesh.remove_duplicated_vertices()
        mesh.remove_duplicated_triangles()
        mesh.remove_degenerate_triangles()
        mesh.remove_non_manifold_edges()
        
        # Convert Open3D mesh to numpy arrays for pymeshfix
        vertices = np.asarray(mesh.vertices)
        faces = np.asarray(mesh.triangles)
        
        # Use pymeshfix to fill holes
        meshfix = pymeshfix.MeshFix(vertices, faces)
        meshfix.repair()
        
        # Convert back to Open3D mesh
        watertight_mesh = o3d.geometry.TriangleMesh()
        watertight_mesh.vertices = o3d.utility.Vector3dVector(meshfix.v)
        watertight_mesh.triangles = o3d.utility.Vector3iVector(meshfix.f)
        
        # Compute normals for the watertight mesh
        watertight_mesh.compute_vertex_normals()
        
        # Export the high-resolution watertight mesh to STL
        stl_file = os.path.join(output_dir, os.path.basename(ply_file).replace('.ply', '.stl'))
        o3d.io.write_triangle_mesh(stl_file, watertight_mesh)
        print(f"Converted {ply_file} to {stl_file} with {len(watertight_mesh.triangles)} triangles")

if __name__ == "__main__":
    ply_folder = "ply files"
    output_dir = "stl files"

    # Get all files in the specified folder
    ply_files = glob.glob(os.path.join(ply_folder, "*"))

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    convert_ply_to_stl(ply_files, output_dir)

    print("Finished converting all PLY files to STL files.")
