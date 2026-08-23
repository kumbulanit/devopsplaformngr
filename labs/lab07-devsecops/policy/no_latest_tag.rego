# Policy: container images must not use the mutable ":latest" tag.
# Used by the Lab 07 stretch goal.
package main

import rego.v1

deny contains msg if {
	input.kind == "Deployment"
	some container in input.spec.template.spec.containers
	endswith(container.image, ":latest")
	msg := sprintf("Container %q must not use the 'latest' image tag", [container.name])
}

deny contains msg if {
	input.kind == "Deployment"
	some container in input.spec.template.spec.containers
	not contains(container.image, ":")
	msg := sprintf("Container %q has no image tag (defaults to 'latest')", [container.name])
}
