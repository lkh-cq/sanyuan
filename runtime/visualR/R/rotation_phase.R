rotation_measure <- function(level) {
  if (!level %in% 1:6) stop("rotation measure must be 1-6")
  level
}

jiugong_state <- function(shells, core, phase=5L) {
  list(
    shells = shells,
    core = core,
    rotation_measure = rotation_measure(phase)
  )
}
