encode_pal <- function(shells, core) {
  out <- paste0("{", core, "}")
  for (s in rev(shells)) {
    out <- paste0("{", s, out, s, "}")
  }
  out
}

unfold_pal <- function(shells, core) {
  c(shells, core, rev(shells))
}

validate_pal <- function(shells, core) {
  if (length(unfold_pal(shells, core)) %% 2 == 0) stop("PAL expansion must be odd")
  TRUE
}

as_jiugong <- function(shells, core) {
  x <- unfold_pal(shells, core)
  if (length(x) != 9) stop("Only fourth-order PAL maps to 3x3 carrier")
  matrix(x, nrow=3, byrow=TRUE)
}

complement_address <- function(i, n) n + 1L - i
