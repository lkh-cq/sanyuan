#!/usr/bin/env Rscript

# Endoscope base-R adapter.
# Hard dependency: base R only. The Python controller treats this adapter as optional.

json_escape <- function(x) {
  x <- enc2utf8(as.character(x))
  x <- gsub("\\\\", "\\\\\\\\", x)
  x <- gsub('"', '\\\\"', x, fixed = TRUE)
  x <- gsub("\n", "\\\\n", x, fixed = TRUE)
  x <- gsub("\r", "\\\\r", x, fixed = TRUE)
  x <- gsub("\t", "\\\\t", x, fixed = TRUE)
  x
}

json_scalar <- function(x) {
  if (is.null(x) || length(x) == 0L || is.na(x[[1L]])) return("null")
  if (is.logical(x)) return(if (isTRUE(x[[1L]])) "true" else "false")
  if (is.numeric(x)) return(as.character(x[[1L]]))
  paste0('"', json_escape(x[[1L]]), '"')
}

json_value <- function(x) {
  if (is.null(x)) return("null")
  if (is.list(x)) {
    nms <- names(x)
    if (!is.null(nms) && all(nzchar(nms))) {
      parts <- mapply(
        function(nm, value) paste0('"', json_escape(nm), '":', json_value(value)),
        nms,
        x,
        SIMPLIFY = TRUE,
        USE.NAMES = FALSE
      )
      return(paste0("{", paste(parts, collapse = ","), "}"))
    }
    return(paste0("[", paste(vapply(x, json_value, character(1L)), collapse = ","), "]"))
  }
  if (length(x) > 1L) {
    return(paste0("[", paste(vapply(as.list(x), json_value, character(1L)), collapse = ","), "]"))
  }
  json_scalar(x)
}

line_signal <- function(lines, pattern, signal, severity = "medium", fixed = FALSE) {
  idx <- grep(pattern, lines, ignore.case = TRUE, perl = !fixed, fixed = fixed)
  lapply(idx, function(i) {
    list(
      signal = signal,
      severity = severity,
      line = as.integer(i),
      match = trimws(substr(lines[[i]], 1L, 160L))
    )
  })
}

probe_file <- function(path) {
  lines <- readLines(path, warn = FALSE, encoding = "UTF-8")
  parsed <- tryCatch(
    parse(file = path, keep.source = TRUE),
    error = function(e) e
  )

  parse_ok <- !inherits(parsed, "error")
  parse_error <- if (parse_ok) NULL else list(message = conditionMessage(parsed))
  expression_count <- if (parse_ok) length(parsed) else 0L

  signals <- c(
    line_signal(lines, "<<-|\\.GlobalEnv|assign\\s*\\(", "r_global_assign", "medium"),
    line_signal(lines, "file\\.remove\\s*\\(|unlink\\s*\\(", "destructive_write", "critical"),
    line_signal(lines, "write\\.csv\\s*\\(|write\\.table\\s*\\(|writeLines\\s*\\(|saveRDS\\s*\\(|dbExecute\\s*\\(", "external_write", "high"),
    line_signal(lines, "system2?\\s*\\(", "dynamic_exec", "high"),
    line_signal(lines, "parallel::|future::", "concurrency", "high"),
    line_signal(lines, "as\\.(numeric|integer)\\s*\\(", "r_coercion_sensitive", "medium"),
    line_signal(lines, "\\bif\\s*\\([^)]*[><=!]=?", "na_sensitive_branch", "medium"),
    line_signal(lines, "setwd\\s*\\(|options\\s*\\(", "environment_mutation", "medium")
  )

  if (!parse_ok) {
    signals <- c(signals, list(list(
      signal = "parse_error",
      severity = "high",
      line = NULL,
      match = conditionMessage(parsed)
    )))
  }

  list(
    protocol_version = "0.2.0",
    engine = "base-r",
    parse_ok = parse_ok,
    parse_error = parse_error,
    expression_count = as.integer(expression_count),
    nesting = NA_integer_,
    signals = signals
  )
}

selftest <- function() {
  tmp <- tempfile(fileext = ".R")
  writeLines(c(
    'x <- as.integer("x")',
    'if (x > 5) print(x)',
    'saveRDS(x, tempfile())'
  ), tmp, useBytes = TRUE)
  on.exit(unlink(tmp), add = TRUE)
  result <- probe_file(tmp)
  names_found <- vapply(result$signals, function(x) x$signal, character(1L))
  pass <- isTRUE(result$parse_ok) &&
    "na_sensitive_branch" %in% names_found &&
    "external_write" %in% names_found
  if (!pass) stop("Endoscope R adapter selftest failed")
  list(protocol_version = "0.2.0", status = "PASS", engine = "base-r")
}

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1L) {
  cat(json_value(list(status = "ERROR", error = "usage: endoscope_r.R probe FILE | selftest")))
  quit(status = 2L)
}

command <- args[[1L]]
result <- tryCatch({
  if (identical(command, "probe")) {
    if (length(args) != 2L) stop("probe requires exactly one file")
    probe_file(args[[2L]])
  } else if (identical(command, "selftest")) {
    selftest()
  } else {
    stop(paste("unknown command", command))
  }
}, error = function(e) {
  list(protocol_version = "0.2.0", status = "ERROR", error = conditionMessage(e))
})

cat(json_value(result))
if (!is.null(result$status) && identical(result$status, "ERROR")) quit(status = 2L)
