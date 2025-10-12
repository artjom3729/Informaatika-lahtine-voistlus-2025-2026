import sys
import math
from collections import defaultdict

def main():
    mode = sys.stdin.readline().strip()
    
    if mode == 'ENC':
        # Read M, N
        data = sys.stdin.readline().split()
        M = int(data[0])
        N = int(data[1])
        wagons = list(map(int, sys.stdin.readline().split()))
        
        # Calculate minimal k such that k! >= M
        k = 0
        fact = 1
        while fact < M and k < N:
            k += 1
            fact *= k
        
        # If k == 0, we need at least 1 wagon
        if k == 0:
            k = 1
        
        # Get k smallest distinct values
        distinct_values = sorted(set(wagons))[:k]
        
        # Create mapping from values to available wagons
        value_to_count = defaultdict(int)
        for wagon in wagons:
            value_to_count[wagon] += 1
        
        # Build the selected wagons (one per distinct value)
        selected_wagons = []
        remaining_wagons = []
        
        # First, add one of each distinct value
        for val in distinct_values:
            selected_wagons.append(val)
            value_to_count[val] -= 1
        
        # Then add all remaining wagons
        for val, count in value_to_count.items():
            for _ in range(count):
                remaining_wagons.append(val)
        
        # Precompute factorials
        facts = [1] * (k + 1)
        for i in range(1, k + 1):
            facts[i] = facts[i-1] * i
        
        # Process each S
        while True:
            line = sys.stdin.readline().strip()
            if not line:
                break
            
            S = int(line)
            if S == -1:
                break
            
            # Encode S as permutation of selected wagons
            available = distinct_values[:]
            encoded = []
            temp_S = S
            
            for i in range(k):
                fact_val = facts[k - 1 - i]
                idx = temp_S // fact_val
                temp_S %= fact_val
                encoded.append(available.pop(idx))
            
            # Build the full output
            result = encoded + remaining_wagons
            print(' '.join(map(str, result)), flush=True)
    
    elif mode == 'DEC':
        # Read M, N
        data = sys.stdin.readline().split()
        M = int(data[0])
        N = int(data[1])
        
        # Calculate the same k as encoder
        k = 0
        fact = 1
        while fact < M and k < N:
            k += 1
            fact *= k
        
        if k == 0:
            k = 1
        
        # Precompute factorials
        facts = [1] * (k + 1)
        for i in range(1, k + 1):
            facts[i] = facts[i-1] * i
        
        # Process trains
        while True:
            # Read first k wagons
            first_k = []
            for _ in range(k):
                print('R', flush=True)
                line = sys.stdin.readline().strip()
                if not line:
                    return
                
                wagon = int(line)
                if wagon == -1:
                    return
                first_k.append(wagon)
            
            # Get distinct values from first k wagons
            distinct_values = sorted(set(first_k))
            
            # Decode the permutation
            available = distinct_values[:]
            S = 0
            
            for i in range(k):
                fact_val = facts[k - 1 - i]
                val = first_k[i]
                idx = available.index(val)
                S += idx * fact_val
                available.pop(idx)
            
            print(S, flush=True)

if __name__ == '__main__':
    main()