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