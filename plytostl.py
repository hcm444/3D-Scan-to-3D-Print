import open3d as o3d
import numpy as np
import os
import glob
import pymeshfix
import argparse
import logging

def convert_ply_to_stl(ply_files, output_dir, min_triangles=10000):
    for ply_file in ply_files:

        if not ply_file.lower().endswith('.ply'):
            logging.warning(f'Skipping "{ply_file}" because it is filetype: "{os.path.splitext(ply_file)[1]}"')
            continue

        try:

            mesh = o3d.io.read_triangle_mesh(ply_file)
            mesh.compute_vertex_normals()

            while len(mesh.triangles) < min_triangles:
                mesh = mesh.subdivide_midpoint(number_of_iterations=1)


            mesh.remove_duplicated_vertices()
            mesh.remove_duplicated_triangles()
            mesh.remove_degenerate_triangles()
            mesh.remove_non_manifold_edges()


            vertices = np.asarray(mesh.vertices)
            faces = np.asarray(mesh.triangles)


            meshfix = pymeshfix.MeshFix(vertices, faces)
            meshfix.repair()


            watertight_mesh = o3d.geometry.TriangleMesh()
            watertight_mesh.vertices = o3d.utility.Vector3dVector(meshfix.v)
            watertight_mesh.triangles = o3d.utility.Vector3iVector(meshfix.f)


            watertight_mesh.compute_vertex_normals()


            stl_file = os.path.join(output_dir, os.path.basename(ply_file).replace('.ply', '.stl'))
            o3d.io.write_triangle_mesh(stl_file, watertight_mesh)
            logging.info(f"Converted {ply_file} to {stl_file} with {len(watertight_mesh.triangles)} triangles")
        except Exception as e:
            logging.error(f"Failed to process {ply_file}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PLY files to STL files.")
    parser.add_argument("ply_folder", type=str, help="Directory containing PLY files")
    parser.add_argument("output_dir", type=str, help="Directory to save STL files")
    parser.add_argument("--min_triangles", type=int, default=10000, help="Minimum number of triangles in the output mesh")
    args = parser.parse_args()


    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


    ply_files = glob.glob(os.path.join(args.ply_folder, "*"))


    os.makedirs(args.output_dir, exist_ok=True)

    convert_ply_to_stl(ply_files, args.output_dir, args.min_triangles)

    logging.info("Finished converting all PLY files to STL files.")
