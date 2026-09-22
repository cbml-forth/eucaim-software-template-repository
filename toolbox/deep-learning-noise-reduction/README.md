# Contributing a tool to EUCAIM

Tool providers contribute by submitting Pull Requests containing a new tool directory under

```text
toolbox/
```

This template helps tool providers to create the three parts that are compulsory to make available a new software tool in EUCAIM federated compute platform:
1) All container images registered in EUCAIM Harbor
2) Metadata describing how EUCAIM platform can run the new tool
3) Test dataset to validate the integration 

As explained in the [main README file](https://github.com/EUCAIM/software-template-repository/blob/main/README.md), the easiest approach is to start forking the whole repository, copying `tool_template/` and renaming it to your own tool name `toolbox/<tool_name>`. 

**For more details check the [EUCAIM Software Packaging Guide v1.4](https://docs.google.com/document/d/18vvCtJbzcM3VPOUA0wF03Vg8RohkNByWi0iqlbZ3Zmk/edit?usp=sharing)**

# How to prepare task container images
A EUCAIM tools can consist of one or a set of tasks, where a separate Docker image is expected for each task.

The platform requires containers to:

* Run applications as a non-root user.
* Support dynamic UID/GID assignment at runtime.
* Preserve platform security controls implemented in the provided entrypoint.
* Allow application-specific startup commands through Docker `CMD`.
* Read node's data from a infra-specific path
* Write application's output in a infra-specific path

Tool providers are free to build images using their own CI/CD pipelines.

### Template structure

```text
├── tool_template/
│   ├── README.md
│   ├── LICENSE
│   ├── task_containers/
│   │   ├── container_name_task-A
|   │   │   ├── dockerfile
|   │   │   ├── app/
|   │   │   └── entrypoint.sh
│   │   ├── another_task_cotainer
│   │   └── ...
│   ├── metadata/
│   │   ├── FEM/
|   │   │   ├── tool_bundle.cwl
│   │   │   └── ...
│   │   └── jobman/
│   ├── docs/
│   └── test/
│       └── example_input/
│       └── example_output/
```

#### Files

| File                           | Description                                                                                                 |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `README.md`                    | Template documentation and usage instructions.                                                              |
| `LICENSE`                      | License terms and conditions governing the use, distribution, and modification of this project.                                                              |
| `task_containers`    |  Contains one or more task-specific container implementations. Each task container includes the Dockerfile, application source code, and the entrypoint.sh required to build and execute the container. |
| `task_containers/container_name_task-A/dockerfile`    | Reference Dockerfile to build your application image.                                                       |
| `task_containers/container_name_task-A/entrypoint.sh` | Platform-managed startup script. Performs runtime user configuration and launches the application securely. |
| `task_containers/container_name_task-A/app/`          | Place your application source code, binaries, scripts, and assets here.                                     |
| `metadata`    | Contains tool descriptors and metadata required for integration with the EUCAIM platform (e.g., CWL descriptors, workflow definitions, and execution metadata).                                                        |
| `docs/`                        | Optional documentation for your application.                                                                |
| `test/`                        |  Contains the resources required to validate the tool, including representative input datasets and the corresponding expected outputs.                                                                |



## Important Requirements

#### Do Not Modify `entrypoint.sh`

The provided `entrypoint.sh` is responsible for:

* Creating or updating the runtime user.
* Mapping host UID and GID values.
* Fixing file ownership where required.
* Dropping root privileges.
* Launching the application as a non-root user.

The platform relies on this behavior for security and compatibility.

Application providers should not replace or bypass this script.


## How Application Startup Works

The template uses the following pattern:

```dockerfile
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python3", "/app/main.py"]
```

At container startup:

1. `entrypoint.sh` executes first.
2. Runtime UID/GID mappings are applied.
3. A non-root user is configured.
4. The command specified by `CMD` is executed using `gosu`.

Example:

```dockerfile
CMD ["python3", "/app/script.py"]
```

Results in:

```bash
gosu application-user python3 /app/script.py
```


## Creating Your Application Container

### Step 1: Copy Your Application

Place your application files inside:

```text
task_containers/container_name_task-A/app/
```

### Step 2: Install Dependencies

Modify the Dockerfile to install your application's dependencies.

Example:

```dockerfile
FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip gosu

COPY entrypoint.sh /app/entrypoint.sh
COPY app/ /app/

RUN chown -R root:root /app && chmod 755 /app/main.py /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python3", "/app/server.py"]
```

### Step 3: Define Your Startup Command

Specify how your application should start using `CMD`.

Examples:

##### Python application
```dockerfile
CMD ["python3", "/app/server.py"]
```
##### Node.js application
```dockerfile
CMD ["node", "/app/index.js"]
```
##### Java application
```dockerfile
CMD ["java", "-jar", "/app/application.jar"]
```
##### Custom executable
```dockerfile
CMD ["/app/bin/my-service"]
```

The platform injects runtime values used by the entrypoint:

| Variable    | Description                                           |
| ----------- | ----------------------------------------------------- |
| `HOST_UID`  | User ID that should own and execute the application.  |
| `HOST_GID`  | Group ID that should own and execute the application. |
| `HOST_USER` | Runtime username created inside the container.        |

These values are managed automatically by the platform and should not be hardcoded.


### Step 4: Building the Docker Image

From the `container_name` directory:

```bash
docker build -t my-application:v1.0 .
```

Verify that the image was created successfully:

```bash
docker images | grep my-application
```

Expected output:

```text
my-application   latest   <IMAGE_ID>   <DATE>   <SIZE>
```

# How to prepare test dataset

At minimum contributors shall provide

```text
test/
├── example_input/
└── example_output/
```

Input datasets shall correspond to the minimal dataset required by the tool and follow

* EUCAIM Common Data Model
* EUCAIM file-system conventions

Expected outputs shall be deterministic whenever possible.

If outputs are non deterministic,

```text
test/example_output/description.md
```

shall explain which properties should be checked during integration testing.

Providing expected execution logs is recommended.

# How to prepare Metadata

Metadata shall contain the information required for execution within EUCAIM compute infrastructures.

Particular focus is placed on execution through FEM.

Contributors shall provide

```text
metadata/FEM/
```

including

* CWL descriptions for each task
* a workflow CWL describing the complete tool execution
* `bundle.cwl` defining the overall workflow

More information can be fined (here)[https://docs.google.com/document/d/19cZr_iYzuy8YEssWTFLVitIHBXTGpK5c9rQizbE9R6w/edit?usp=sharing]. Additional metadata formats may be added in the future.

# Support

If your application cannot run correctly within this template, provide the following information when contacting EUCAIM to (support@eucaim)[support_eucaim@example]:

* Dockerfile
* Application startup command (`CMD`)
* Container logs
* Dependency requirements
* Test dataset description
* Expected output description

This information will help validate compatibility with the platform runtime environment.

# Security Guidelines

Applications should:

* Avoid requiring root privileges.
* Store writable data in designated application directories.
* Use relative paths where possible.
* Handle termination signals correctly (`SIGTERM`, `SIGINT`).

Applications should not:

* Modify `/etc/passwd` or `/etc/group`.
* Replace the provided entrypoint.
* Attempt privilege escalation.

