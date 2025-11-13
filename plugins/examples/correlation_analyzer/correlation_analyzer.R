# Correlation Analyzer Plugin - OmniScope AI Plugin
# Calculates correlation matrices and identifies significant correlations
#
# Author: OmniScope Team
# Version: 1.0.0

library(jsonlite)

# Main plugin class
CorrelationAnalyzer <- setRefClass(
  "CorrelationAnalyzer",
  
  fields = list(
    context = "list",
    config = "list",
    plugin_id = "character",
    plugin_name = "character"
  ),
  
  methods = list(
    initialize = function(context) {
      "Initialize plugin"
      .self$context <- context
      .self$config <- context$config
      .self$plugin_id <- context$plugin_id
      .self$plugin_name <- context$plugin_name
    },
    
    validate_input = function(input_data) {
      "Validate input data"
      if (!"data" %in% names(input_data)) {
        stop("Missing required field: data")
      }
      
      parameters <- input_data$parameters
      method <- ifelse(is.null(parameters$method), "pearson", parameters$method)
      
      if (!method %in% c("pearson", "spearman", "kendall")) {
        stop(paste("Invalid correlation method:", method))
      }
      
      return(TRUE)
    },
    
    execute = function(input_data) {
      "Execute plugin logic"
      data <- input_data$data
      parameters <- input_data$parameters
      
      # Get correlation method
      method <- ifelse(is.null(parameters$method), "pearson", parameters$method)
      threshold <- ifelse(is.null(parameters$threshold), 0.7, parameters$threshold)
      
      # Calculate correlation
      result <- .self$calculate_correlation(data, method, threshold)
      
      return(list(
        data = result,
        metadata = list(
          plugin_id = .self$plugin_id,
          plugin_name = .self$plugin_name,
          method = method,
          threshold = threshold
        ),
        logs = list(paste("Correlation calculated using", method, "method")),
        warnings = list(),
        errors = list()
      ))
    },
    
    calculate_correlation = function(data, method, threshold) {
      "Calculate correlation matrix"
      # Convert to data frame
      df <- as.data.frame(data)
      
      # Calculate correlation matrix
      cor_matrix <- cor(df, method = method, use = "pairwise.complete.obs")
      
      # Find significant correlations
      significant <- list()
      n <- nrow(cor_matrix)
      
      for (i in 1:(n-1)) {
        for (j in (i+1):n) {
          if (abs(cor_matrix[i, j]) >= threshold) {
            significant[[length(significant) + 1]] <- list(
              var1 = rownames(cor_matrix)[i],
              var2 = colnames(cor_matrix)[j],
              correlation = cor_matrix[i, j]
            )
          }
        }
      }
      
      return(list(
        correlation_matrix = cor_matrix,
        significant_correlations = significant,
        method = method,
        threshold = threshold
      ))
    },
    
    cleanup = function() {
      "Cleanup resources"
    }
  )
)

# Main entry point
main <- function() {
  # Read input from file
  input_data <- fromJSON("/plugin/input.json")
  
  # Read context
  context <- input_data$context
  
  # Initialize plugin
  plugin <- CorrelationAnalyzer$new(context)
  
  # Validate input
  plugin$validate_input(input_data)
  
  # Execute plugin
  output <- plugin$execute(input_data)
  
  # Write output to file
  write_json(output, "/plugin/output.json", auto_unbox = TRUE, pretty = TRUE)
  
  # Cleanup
  plugin$cleanup()
}

# Run main function
tryCatch(
  {
    main()
    quit(status = 0)
  },
  error = function(e) {
    error_output <- list(
      data = NULL,
      errors = list(as.character(e)),
      logs = list(),
      warnings = list()
    )
    write_json(error_output, "/plugin/output.json", auto_unbox = TRUE, pretty = TRUE)
    quit(status = 1)
  }
)
