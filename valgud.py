import os
from typing import List, Tuple, Set

def read_input_file(filename: str) -> Tuple[int, int, int, int, List[int], List[int], List[float]]:
    """Read and parse an input file"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Parse first line
    n, m, k, H = map(int, lines[0].strip().split())
    
    # Parse start points
    A = list(map(int, lines[1].strip().split()))
    
    # Parse ground points
    B = list(map(int, lines[2].strip().split()))
    
    # Parse coefficients
    coefficients = list(map(float, lines[3].strip().split()))
    
    return n, m, k, H, A, B, coefficients

def build_lightning_bolt(start_x: int, H: int, ground_points: List[int], air_count: int) -> List[Tuple[int, int]]:
    """Build a valid lightning bolt where every point has a valid parent"""
    points = set()
    
    # Start with the cloud point
    points.add((start_x, H))
    
    # For simple case: one ground point, no air endpoints
    if len(ground_points) == 1 and air_count == 0:
        end_x = ground_points[0]
        current_x, current_y = start_x, H
        
        # Calculate the path
        dx = end_x - start_x
        dy = H
        
        # Check if direct path is possible
        if abs(dx) <= dy and (dy + dx) % 2 == 0:
            # Calculate number of left and right moves
            R = (dy + dx) // 2
            L = (dy - dx) // 2
            
            # Generate path
            for _ in range(L):
                current_x -= 1
                current_y -= 1
                points.add((current_x, current_y))
            
            for _ in range(R):
                current_x += 1
                current_y -= 1
                points.add((current_x, current_y))
        else:
            # Use zigzag path
            current_x, current_y = start_x, H
            while current_y > 0:
                current_y -= 1
                # Move toward target, but ensure we don't overshoot
                if current_x < end_x:
                    current_x += 1
                elif current_x > end_x:
                    current_x -= 1
                else:
                    # At correct x, alternate to create natural look
                    if (H - current_y) % 2 == 0:
                        current_x += 1
                    else:
                        current_x -= 1
                points.add((current_x, current_y))
    
    else:
        # Complex case: multiple ground points and/or air endpoints
        # Create a main trunk
        trunk_height = H // 2
        if trunk_height < 1:
            trunk_height = 1
            
        current_x, current_y = start_x, H
        
        # Build trunk from start to branching point
        while current_y > trunk_height:
            current_y -= 1
            # Slight zigzag to make it look natural
            if (H - current_y) % 3 == 0:
                current_x += 1
            elif (H - current_y) % 3 == 1:
                current_x -= 1
            points.add((current_x, current_y))
        
        trunk_x, trunk_y = current_x, current_y
        
        # Branch to ground points
        for i, ground_x in enumerate(ground_points):
            # Create a path from trunk to ground point
            path_x, path_y = trunk_x, trunk_y
            
            while path_y > 0:
                path_y -= 1
                # Move toward ground point
                if path_x < ground_x:
                    path_x += 1
                elif path_x > ground_x:
                    path_x -= 1
                else:
                    # At correct x, alternate slightly
                    if i % 2 == 0:
                        path_x += 1
                    else:
                        path_x -= 1
                points.add((path_x, path_y))
        
        # Add air endpoints
        for i in range(air_count):
            # Determine position for air endpoint
            air_y = max(1, trunk_y - (i + 1) * 2)
            air_x = trunk_x + (1 if i % 2 == 0 else -1) * (i + 1)
            
            points.add((air_x, air_y))
            
            # Connect air endpoint to trunk
            connect_x, connect_y = trunk_x, trunk_y
            while connect_y > air_y:
                connect_y -= 1
                # Move toward air endpoint
                if connect_x < air_x:
                    connect_x += 1
                elif connect_x > air_x:
                    connect_x -= 1
                else:
                    # At correct x, alternate slightly
                    if i % 2 == 0:
                        connect_x += 1
                    else:
                        connect_x -= 1
                points.add((connect_x, connect_y))
    
    return list(points)

def solve_input_file(input_file: str, output_file: str):
    """Solve a single input file and write output"""
    try:
        n, m, k, H, A, B, coefficients = read_input_file(input_file)
        
        # Distribute ground points among bolts
        assigned_grounds = [[] for _ in range(n)]
        
        if n == 1:
            # All ground points go to the single bolt
            assigned_grounds[0] = B
        else:
            # Distribute ground points to nearest start points
            for ground_x in B:
                # Find closest start point
                min_dist = float('inf')
                best_bolt = 0
                for i, start_x in enumerate(A):
                    dist = abs(start_x - ground_x)
                    if dist < min_dist:
                        min_dist = dist
                        best_bolt = i
                assigned_grounds[best_bolt].append(ground_x)
        
        # Distribute air endpoints
        airs_per_bolt = k // n
        extra_airs = k % n
        assigned_airs = [airs_per_bolt + (1 if i < extra_airs else 0) for i in range(n)]
        
        output_lines = []
        
        for i in range(n):
            start_x = A[i]
            grounds = assigned_grounds[i]
            air_count = assigned_airs[i]
            
            # Generate valid lightning bolt
            bolt_points = build_lightning_bolt(start_x, H, grounds, air_count)
            
            # Ensure we have the start point
            if (start_x, H) not in bolt_points:
                bolt_points.append((start_x, H))
            
            # Output the bolt
            output_lines.append(str(len(bolt_points)))
            for x, y in bolt_points:
                output_lines.append(f"{x} {y}")
        
        # Write output file
        with open(output_file, 'w') as f:
            f.write("\n".join(output_lines))
            
        print(f"Generated {output_file}")
        
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        import traceback
        traceback.print_exc()

def process_all_inputs(input_folder: str = "valgud", output_folder: str = "submission"):
    """Process all input files in the folder"""
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Find all input files
    input_files = [f for f in os.listdir(input_folder) if f.startswith('input_') and f.endswith('.txt')]
    
    if not input_files:
        print("No input files found!")
        return
    
    # Sort files to ensure consistent processing
    input_files.sort()
    
    for input_file in input_files:
        # Generate output filename
        file_num = input_file.replace('input_', '').replace('.txt', '')
        output_file = os.path.join(output_folder, f'output_{file_num}.txt')
        input_path = os.path.join(input_folder, input_file)
        
        solve_input_file(input_path, output_file)

if __name__ == "__main__":
    print("Processing all input files...")
    process_all_inputs()
    print("Processing complete!")