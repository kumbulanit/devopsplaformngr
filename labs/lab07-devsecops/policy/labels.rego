# Policy: every Kubernetes Deployment must carry a "course" label.
# Written in modern Rego (OPA >= 1.0 / current Conftest): `deny contains msg if`.
package main

import rego.v1

deny contains msg if {
	input.kind == "Deployment"
	not input.metadata.labels.course
	msg := sprintf("Deployment %q must have a 'course' label", [input.metadata.name])
}
