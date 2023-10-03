import numpy as np

def hildreths_algorithm(P0, G, c, l, u, epsilon, alpha):
    M = len(P0)
    k_hil = 0
    k_cim = 0
    B = len(G)
    
    P = P0.copy()
    
    while True:
        # Step 1: Hildreth's Algorithm 3 - Box constraints update
        for n in range(M):
            if P[n] <= l[n]:
                P[n] = l[n]
            elif l[n] <= P[n] <= u[n]:
                P[n] = P[n]
            elif P[n] >= u[n]:
                P[n] = u[n]
        
        k_hil += 1
        
        # Step 2: Check for termination
        if np.linalg.norm(sum([np.dot(G[b], P) for b in range(B)]) - sum(c)) == 0:
            P_star = P
            return P_star
        
        # Step 3: Block projections (Cimmino's Algorithm)
        P_p = []
        for b in range(B):
            G_b = G[b]
            c_b = c[b]
            M_b = len(G_b)
            P_m = P.copy()
            m = 0
            
            while True:
                P_m_next = P_m + c_b - np.dot(G_b, P_m)
                m += 1
                if m == M_b:
                    if np.linalg.norm(np.dot(G_b, P_m) - c_b) < epsilon:
                        P_p.append(P_m)
                        break
                P_m = P_m_next
        
        k_cim += 1
        
        # Step 4: Compute the barycentre of all projections
        P_b = np.mean(P_p, axis=0)
        
        # Step 5: Perform Scolnik's Acceleration
        d = P_b - P
        d_b = [P_p[i] - P for i in range(B)]
        alpha_star = sum([np.linalg.norm(d_b[i])**2 for i in range(B)]) / (B * np.linalg.norm(d)**2)
        P = P + alpha_star * d
        
        # Step 6: Check for termination
        if np.linalg.norm(sum([np.dot(G[b], P) for b in range(B)]) - sum(c)) == 0:
            P_star = P
            return P_star
        print(P)

# Example usage:
P0 = np.array([0.5, 0.5])  # Initial estimate
G = [np.array([[1, -1]]), np.array([[1, 1]])]  # Block constraint matrices
c = [np.array([0]), np.array([2])]  # Right-hand side vectors
l = np.array([0, 0])  # Lower bounds
u = np.array([1, 1])  # Upper bounds
epsilon = 1e-6  # Tolerance
alpha = 0.1  # Learning rate

result = hildreths_algorithm(P0, G, c, l, u, epsilon, alpha)
print("Optimal solution:", result)
