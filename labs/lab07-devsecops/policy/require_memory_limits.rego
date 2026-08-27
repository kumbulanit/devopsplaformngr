# Policy: every container must declare a memory limit.
#
# Why: a container with no limit can consume the whole node and starve its
# neighbours. This is the rule most platform teams enforce first, because it
# protects everyone else's workloads rather than the offending team's own.
package main

import rego.v1

deny contains msg if {
	input.kind == "Deployment"
	some container in input.spec.template.spec.containers
	not container.resources.limits.memory
	msg := sprintf("Container %q must set resources.limits.memory", [container.name])
}

deny contains msg if {
	input.kind == "Deployment"
	some container in input.spec.template.spec.containers
	not container.resources.requests.memory
	msg := sprintf("Container %q must set resources.requests.memory (the scheduler needs it)", [container.name])
}
