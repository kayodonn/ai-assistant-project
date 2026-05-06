| Method/Constant | Layer | Task Level | State/Data | Next Location | Notes |
|-----------------|-------|------------|------------|---------------|-------|
| DB_PATH | Database | Single | Reads Global State | Constant/Config | Global constant; hurts maintainability by making database path hard-coded and not configurable. |
| SNAPSHOT_PATH | Database | Single | Reads Global State | Constant/Config | Global constant; similar to DB_PATH, reduces flexibility for different environments. |
| CURRENT_STUDENT | Service | Single | Reads Global State | Constant/Config | Global state for current user; mixes service logic with global data, hurting testability and scalability. |
| STATUS_ENROLLED | Service | Single | Reads Global State | Constant/Config | Status constants; should be centralized config, but global access reduces encapsulation. |
| STATUS_UNENROLLED | Service | Single | Reads Global State | Constant/Config | Same as above. |
| AVAILABLE_COURSE_KEYS | Database | Single | Reads Global State | Database Class | Hard-coded course data; should be in database layer for seeding, but global list hurts maintainability. |
| SAMPLE_ENROLLMENTS | Database | Single | Reads Global State | Database Class | Sample data; belongs in database seeding, but global constant mixes concerns. |
| connect() | Database | Single | Self-Contained | Database Class | Pure database connection; good separation, but global DB_PATH usage ties it to global state. |
| create_tables() | Database | Single | Reads Global State | Database Class | Creates schema; database layer, but relies on global connection. |
| seed_sample_data() | Database | Single | Reads Global State | Database Class | Seeds data; database layer, but uses global constants, mixing data with logic. |
| rows_to_dicts() | Database | Single | Self-Contained | Database Class | Utility for row conversion; pure database helper. |
| get_available_course_keys() | Mixed | Mixed | Requires Passing State | Split up | Queries courses but formats for UI/service; mixes database query with service presentation, hurting separation. |
| get_course_by_key() | Mixed | Mixed | Requires Passing State | Split up | Validates key (service logic) and queries (database); database code makes service decision on key validation. |
| get_student_enrollments() | Mixed | Mixed | Requires Passing State | Split up | Filters by enrolled status (service logic) in database query; database layer shouldn't enforce business rules. |
| get_student_enrollment_history() | Mixed | Mixed | Requires Passing State | Split up | Similar to above, but includes all statuses; still mixes service filtering with database access. |
| get_student_course_record() | Mixed | Mixed | Requires Passing State | Split up | Direct database query with minimal logic; could be pure database, but parameter validation is service-like. |
| enroll_with_key() | Service | Single | Self-Contained | Service Class | Business logic for enrollment; calls database, but orchestrates the flow. |
| soft_unenroll_student() | Service | Single | Self-Contained | Service Class | Business logic for unenrollment; pure service operation. |
| get_student_summary() | Mixed | Mixed | Requires Passing State | Split up | Aggregates data (service logic) from database queries; mixes computation with data access. |
| get_all_enrollment_records() | Mixed | Mixed | Requires Passing State | Split up | Fetches all records for export (service use); database query with service intent. |
| export_database_snapshot() | Service | Single | Reads Global State | Service Class | Exports data; service operation, but uses global paths and calls database functions. |
| main() | Service | Mixed | Reads Global State | Service Class | Test runner; orchestrates multiple layers, reads globals, not for production. |

### Structural Issues
- **Global Constants and State**: Constants like DB_PATH, CURRENT_STUDENT, and AVAILABLE_COURSE_KEYS are defined globally, making the code tightly coupled to specific values. This hurts maintainability because changing a database path or user requires editing the source code, and scalability is impacted as the application can't easily support multiple databases or users without code changes. It also makes testing difficult since global state persists across tests.
- **Mixed Concerns in Functions**: Functions like get_available_course_keys() and get_student_enrollments() perform both database queries and service-level decisions (e.g., filtering by status or formatting data). This violates separation of concerns, making it hard to maintain (changes to business logic require touching database code) and scale (database layer can't be reused independently for different service needs).
- **Database Code Making Service Decisions**: In get_course_by_key(), the database query includes key validation (checking if enrollment_key is provided), which is a service-level concern. Similarly, enroll_with_key() checks email format and course existence before database operations. This blurs layers, reducing maintainability (service rules are embedded in database functions) and scalability (can't change validation rules without affecting database code, and makes unit testing database functions harder since they depend on business logic).
- **Procedural Structure**: The entire file is procedural with top-level functions and globals, lacking classes. This hurts scalability as adding features requires modifying the global namespace, and maintainability suffers from no encapsulation (functions can access any global, leading to unintended side effects).
- **Hard-Coded Sample Data**: AVAILABLE_COURSE_KEYS and SAMPLE_ENROLLMENTS are hard-coded lists used for seeding. This reduces maintainability (data changes require code edits) and scalability (can't dynamically load data from external sources without refactoring).
- **Direct Database Calls in Service Logic**: Functions like enroll_with_key() directly call database functions, mixing layers. This makes it hard to mock databases for testing, hurting maintainability, and scalability (can't easily switch databases or add caching without changing service code).


What matched my thinking?
Some of the locations/layers for the methods matched my thinking. I noticed that some things would need to be moved, which the AI also pointed out.
What changed my thinking?
The AI suggested splitting up many of the mixed methods into different methods, which I initially wasn't thinking much about. But I see that this is what will be most effective and make the layers more usuable.
What still needs clarification?
Some suggestions were included about changing the hard coding done and structure of some methods. It's unclear whether this should stay or go because I understand some of the hard coding might just be included because of the nature of the assignment.





### Backend Refactor Plan: From Procedural to Object-Oriented, Layered Design

Based on the structural analysis, this plan outlines a transition from the current procedural code to an object-oriented (OO) design with clear separation of concerns across layers. The goal is to improve maintainability and scalability by isolating database operations, business logic, and configuration. We'll introduce classes to encapsulate behavior, eliminate global state where possible, and ensure each layer has a single responsibility.

#### Key Principles Guiding the Refactor
- **Layer Separation**:
  - **Database Layer**: Handles all SQLite interactions (connections, queries, inserts, updates). Focuses purely on data persistence without business logic. Methods here should be low-level, returning raw rows or performing direct CRUD operations. No validation, filtering, or decision-making beyond basic SQL constraints.
  - **Service Layer**: Contains business logic, including enrollment-key validation, status filtering (e.g., "enrolled" vs. "unenrolled"), summary calculations, and orchestration of database calls. This layer interprets data for "dashboard meaning" (e.g., what enrollments to show to a user) and handles high-level operations like enrollment workflows.
  - **Config/Constants Layer**: Centralized, immutable configuration for paths, statuses, and sample data. This avoids global constants and allows for environment-specific overrides (e.g., different DB paths for testing).
- **OO Design**: Group related methods into classes (e.g., `EnrollmentDatabase` for data access, `EnrollmentService` for business rules). Use dependency injection to pass database instances to services, reducing tight coupling.
- **Addressing Structural Issues**:
  - **Global Constants and State**: Move all globals (e.g., `DB_PATH`, `CURRENT_STUDENT`, `AVAILABLE_COURSE_KEYS`) to a `Config` class or module. This makes them injectable/configurable, improving testability and scalability (e.g., mock configs for different environments).
  - **Database Code Making Service Decisions**: Remove validation and business logic from database methods. For example, `get_course_by_key` should only query; validation moves to service. This clarifies responsibilities and allows independent testing/unit mocking of layers.
  - **Direct Database Calls in Service Logic**: Services will call database methods via injected instances, not directly. This enables mocking for tests, easier database switching (e.g., from SQLite to PostgreSQL), and potential caching layers.
  - **Mixed Concerns**: Split "mixed" methods (e.g., `get_available_course_keys`) into pure database queries and service transformations. For instance, a database method fetches raw course data, and a service method formats it for "dashboard" use.
  - **Hard-Coding**: Retain hard-coded sample data (e.g., `AVAILABLE_COURSE_KEYS`) as-is for this assignment's seeding purposes, but encapsulate it in the config layer. If scalability requires dynamic loading later, it can be refactored without affecting other layers.
- **Order of Refactoring**: Follow dependencies—start with config/constants, then database, then service. This ensures lower layers are stable before building higher ones.
- **No UI Focus**: This plan ignores UI concerns, focusing solely on backend layers.

#### Proposed Layered Architecture
- **Config Layer**: A simple class or module for constants and sample data.
- **Database Layer**: `EnrollmentDatabase` class with methods for raw data access.
- **Service Layer**: `EnrollmentService` class with business logic, injecting `EnrollmentDatabase`.
- **No Mixed Layer**: Eliminate "mixed" by splitting; all methods belong clearly to one layer.
- **Testing/Runner**: Keep `main()` as a simple test runner, but make it instantiate classes instead of calling globals.

#### Detailed Method/Constant Mapping and Refactor Order
Methods/constants are grouped by layer. For each, specify:
- **Current Issues**: Ties to structural problems.
- **Refactor Action**: How to move/split it, including order (e.g., "after config is set up").
- **New Location**: Class and method name.
- **Dependencies**: What must be done first.

1. **Config Layer (First: Establish foundations to eliminate globals)**
   - **DB_PATH**: Current Issues: Global, hard-coded path hurts scalability. Refactor Action: Move to `Config` class as a property; make injectable for testing. Order: First, as everything depends on paths. New Location: `Config.db_path`.
   - **SNAPSHOT_PATH**: Current Issues: Global path. Refactor Action: Same as DB_PATH. Order: With DB_PATH. New Location: `Config.snapshot_path`.
   - **CURRENT_STUDENT**: Current Issues: Global user state mixes service with data. Refactor Action: Move to `Config` as sample data; services can accept user_id/email as parameters instead of reading globals. Order: After paths. New Location: `Config.current_student`.
   - **STATUS_ENROLLED/STATUS_UNENROLLED**: Current Issues: Global constants. Refactor Action: Move to `Config` as class constants. Order: With other constants. New Location: `Config.STATUS_ENROLLED`, etc.
   - **AVAILABLE_COURSE_KEYS**: Current Issues: Global hard-coded list. Refactor Action: Move to `Config`; database seeding uses it. Order: After constants. New Location: `Config.available_course_keys`.
   - **SAMPLE_ENROLLMENTS**: Current Issues: Global sample data. Refactor Action: Move to `Config`. Order: With AVAILABLE_COURSE_KEYS. New Location: `Config.sample_enrollments`.

2. **Database Layer (Second: Build data access after config is ready)**
   - **connect()**: Current Issues: Uses global DB_PATH. Refactor Action: Move to `EnrollmentDatabase` class; accept config as parameter. Order: After config. New Location: `EnrollmentDatabase.__init__` and `connect()`.
   - **create_tables()**: Current Issues: None major. Refactor Action: Move to `EnrollmentDatabase`; call via instance. Order: After connect. New Location: `EnrollmentDatabase.create_tables()`.
   - **seed_sample_data()**: Current Issues: Uses global lists. Refactor Action: Move to `EnrollmentDatabase`; accept config for sample data. Order: After create_tables. New Location: `EnrollmentDatabase.seed_sample_data(config)`.
   - **rows_to_dicts()**: Current Issues: None. Refactor Action: Move to `EnrollmentDatabase` as utility. Order: Early in database. New Location: `EnrollmentDatabase.rows_to_dicts()`.
   - **get_course_by_key()**: Current Issues: Includes validation (service decision). Refactor Action: Split—pure query in database (no validation), validation in service. Order: After connect. New Location: `EnrollmentDatabase.get_course_by_key_raw(enrollment_key)` (removes validation).
   - **get_student_course_record()**: Current Issues: Minimal, but parameter checks could be service. Refactor Action: Move pure query to database; remove checks. Order: After connect. New Location: `EnrollmentDatabase.get_student_course_record(user_id, course_id)`.
   - **get_available_course_keys()**: Current Issues: Mixed (queries and formats). Refactor Action: Split—database returns raw rows, service formats. Order: After connect. New Location: `EnrollmentDatabase.get_all_courses()` (raw query).
   - **get_student_enrollments()**: Current Issues: Filters by status in query (service logic). Refactor Action: Split—database fetches all enrollments for user, service filters. Order: After connect. New Location: `EnrollmentDatabase.get_student_enrollment_records(user_id)` (raw, no status filter).
   - **get_student_enrollment_history()**: Current Issues: Similar to above. Refactor Action: Use same split as get_student_enrollments. Order: With get_student_enrollments. New Location: Same as above (raw).
   - **get_all_enrollment_records()**: Current Issues: Fetches for export (service intent). Refactor Action: Move raw query to database. Order: After connect. New Location: `EnrollmentDatabase.get_all_enrollment_records()`.
   - **enroll_with_key()**: Current Issues: Direct database call with validation. Refactor Action: Move insert logic to database (pure SQL), validation/orchestration to service. Order: After get_course_by_key_raw. New Location: `EnrollmentDatabase.enroll_or_update_enrollment(user_id, email, course_id, status)`.
   - **soft_unenroll_student()**: Current Issues: Direct update. Refactor Action: Move to database. Order: After connect. New Location: `EnrollmentDatabase.update_enrollment_status(user_id, course_id, status)`.

3. **Service Layer (Third: Build business logic after database is complete)**
   - **get_course_by_key() (validation part)**: Current Issues: Was mixed. Refactor Action: Service validates key and calls database. Order: After database get_course_by_key_raw. New Location: `EnrollmentService.get_course_by_key(enrollment_key)` (validates, then calls database).
   - **get_available_course_keys() (formatting part)**: Current Issues: Was mixed. Refactor Action: Service calls database and formats for dashboard. Order: After database get_all_courses. New Location: `EnrollmentService.get_available_course_keys()` (transforms raw data).
   - **get_student_enrollments() (filtering part)**: Current Issues: Was mixed. Refactor Action: Service calls database and filters by enrolled status. Order: After database get_student_enrollment_records. New Location: `EnrollmentService.get_student_enrollments(user_id)` (filters for dashboard).
   - **get_student_enrollment_history() (filtering part)**: Current Issues: Was mixed. Refactor Action: Service calls database (same as enrollments, but no filter). Order: With get_student_enrollments. New Location: `EnrollmentService.get_student_enrollment_history(user_id)` (no filter, all records).
   - **enroll_with_key() (orchestration part)**: Current Issues: Was mixed. Refactor Action: Service validates inputs, checks course, calls database. Order: After service get_course_by_key and database enroll_or_update. New Location: `EnrollmentService.enroll_with_key(user_id, email, enrollment_key)`.
   - **soft_unenroll_student()**: Current Issues: Direct call. Refactor Action: Service calls database update. Order: After database update_enrollment_status. New Location: `EnrollmentService.soft_unenroll_student(user_id, course_id)`.
   - **get_student_summary()**: Current Issues: Aggregates data (business logic). Refactor Action: Service calls history and computes counts. Order: After get_student_enrollment_history. New Location: `EnrollmentService.get_student_summary(user_id)`.
   - **export_database_snapshot()**: Current Issues: Orchestrates export (service). Refactor Action: Service calls database methods and writes JSON. Order: After all database/service methods. New Location: `EnrollmentService.export_database_snapshot(config)`.

4. **Runner/Test Layer (Last: Update after layers are built)**
   - **main()**: Current Issues: Reads globals, calls functions directly. Refactor Action: Instantiate classes, inject config/database. Order: After all layers. New Location: Remains top-level, but uses `EnrollmentService` and `EnrollmentDatabase`.

#### Implementation Prompt
"Refactor the enrollment_starter.py file into an object-oriented, layered design based on the provided plan. Create classes for Config, EnrollmentDatabase, and EnrollmentService. Move constants and sample data to Config. Implement EnrollmentDatabase with pure SQLite methods, injecting config. Build EnrollmentService with business logic, injecting EnrollmentDatabase. Split mixed methods as specified, ensuring database focuses on queries/updates and service handles validation, filtering, and orchestration. Update main() to use the new classes. Preserve all original functionality, but eliminate globals and direct database calls in services. Do not add UI code or change hard-coded sample data beyond encapsulation."


What is interesting or useful in the plan?
Global constants will be moved to their own constants/configs class to make them more configurable across classes. Also, validation and business logic will be removed from database methods, so that the layers can be separated and consistent. The order of classes will be config, database, service, and test/runner. 
What might be missing or need revision?
It is unclear whether the methods being separated will be named appropriately to make it clear that they are now two different methods in two different layers. This might be something that needs to be revised.