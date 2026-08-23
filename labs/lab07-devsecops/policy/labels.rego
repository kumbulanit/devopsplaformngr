package main
deny[msg] {
  input.kind == "Deployment"
  not input.metadata.labels.course
  msg := "Deployment must have a 'course' label"
}
