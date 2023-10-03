hildreths_algorithm <- function(P0, G, c, l, u, epsilon, alpha) {
  M <- length(P0)
  k_hil <- 0
  k_cim <- 0
  B <- length(G)
  
  P <- P0
  
  while (TRUE) {
    # Step 1: Hildreth's Algorithm 3 - Box constraints update
    for (n in 1:M) {
      if (P[n] <= l[n]) {
        P[n] <- l[n]
      } else if (l[n] <= P[n] && P[n] <= u[n]) {
        P[n] <- P[n]
      } else if (P[n] >= u[n]) {
        P[n] <- u[n]
      }
    }
    
    k_hil <- k_hil + 1
    
    # Step 2: Check for termination
    if (sum(sapply(1:B, function(b) sum(G[[b]] %*% P))) == sum(unlist(c))) {
      P_star <- P
      return(P_star)
    }
    
    # Step 3: Block projections (Cimmino's Algorithm)
    P_p <- list()
    for (b in 1:B) {
      G_b <- G[[b]]
      c_b <- c[[b]]
      M_b <- ncol(G_b)
      P_m <- P
      m <- 0
      
      while (TRUE) {
        P_m_next <- P_m + c_b - G_b %*% P_m
        m <- m + 1
        if (m == M_b) {
          if (norm(G_b %*% P_m - c_b) < epsilon) {
            P_p[[b]] <- P_m
            break
          }
        }
        P_m <- P_m_next
      }
    }
    
    k_cim <- k_cim + 1
    
    # Step 4: Compute the barycentre of all projections
    P_b <- rowMeans(do.call(cbind, P_p))
    
    # Step 5: Perform Scolnik's Acceleration
    d <- P_b - P
    d_b <- lapply(P_p, function(P_i) P_i - P)
    alpha_star <- sum(sapply(1:B, function(i) norm(d_b[[i]])^2)) / (B * norm(d)^2)
    P <- P + alpha_star * d
    
    # Step 6: Check for termination
    if (sum(sapply(1:B, function(b) sum(G[[b]] %*% P))) == sum(unlist(c))) {
      P_star <- P
      return(P_star)
    }
    
    print(P)
  }
}

# Example usage:
P0 <- c(0.5, 0.5)  # Initial estimate
G <- list(matrix(c(1, -1), nrow = 1), matrix(c(1, 1), nrow = 1))  # Block constraint matrices
c <- list(c(0), c(2))  # Right-hand side vectors
l <- c(0, 0)  # Lower bounds
u <- c(1, 1)  # Upper bounds
epsilon <- 1e-6  # Tolerance
alpha <- 0.1  # Learning rate

result <- hildreths_algorithm(P0, G, c, l, u, epsilon, alpha)
cat("Optimal solution:", result, "\n")

