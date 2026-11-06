# UTM-PLEIADES isolated staging dry run

This is a **simulation**, not a remote deployment. A temporary local directory is used as the isolated staging workspace. It executes the pinned plaintext master core on a fixed finite input, checks deterministic JSON output, health conditions, SHA-256 artifact integrity, and simulates rollback by deleting only the temporary result.

The workflow uses read-only GitHub permissions and no deployment secrets. It cannot create cloud resources, publish images, deploy a service, or roll back any actual cloud service.

Real staging deployment requires a selected provider, isolated environment, narrowly scoped credentials, readiness checks, and a provider-specific rollback procedure. Production remains out of scope.
