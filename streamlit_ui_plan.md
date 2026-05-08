# Streamlit UI Plan

## Overview

This plan describes a two-page Streamlit application that uses the existing backend in `enrollment_starter.py`.

- Page 1: `dashboard`
- Page 2: `class`

The UI uses `st.session_state` for routing, role, and selected class state. It makes minimal changes to backend behavior and calls the service layer methods in `EnrollmentService`.

## Session State

Use `st.session_state` to manage the app state:

- `st.session_state["page"]`: controls the current visible page
  - initial value: `"dashboard"`
  - other value: `"class"`
- `st.session_state["role"]`: controls the user role
  - value: `"user"`
- `st.session_state["selected_class_id"]`: stores the selected course ID for the `class` page
- `st.session_state["selected_class_info"]`: optional container for the selected course details
- `st.session_state["enrollment_key_input"]`: text input value for enrollment/unenrollment

Assume the student is already logged in as Kayleigh O'Donnell.

## How the UI Uses the Service Layer

The UI should call the service layer methods from `EnrollmentService`:

- `get_available_course_keys()` to populate available courses and the class select box
- `get_student_enrollments(user_id)` to display currently enrolled classes
- `get_course_by_key(enrollment_key)` to validate an enrollment key and retrieve course details
- `enroll_with_key(user_id, email, enrollment_key)` to enroll or re-enroll the student through the service
- `soft_unenroll_student(user_id, course_id)` to soft-unenroll a student from a class
- optionally `get_student_summary(user_id)` for dashboard summary data

The backend has built-in seed data and the selected student should map to the existing seeded student.

## Page 1: Dashboard (`dashboard`)

### Page title

- `st.title("Student Dashboard")`

### Page structure

1. Student greeting and current role
2. Container with current enrolled classes
3. Two equal-width columns
   - Left column: select box and Go To Class button
   - Right column: enrollment key textbox and Enroll / Unenroll buttons

### Top section

- Display a short greeting for the logged-in student: `Kayleigh O'Donnell`
- Display that this is the user dashboard for role `user`
- Optional summary text: `You are currently enrolled in X classes.`

### Enrolled classes container

- Use `st.container()` or `st.expander("Current Enrolled Classes")`
- List each enrolled class in a clear format, such as:
  - `MISY350 — Python for Business Analytics — Dr. Rivera`
  - `WEB220 — Web Apps With Streamlit — Dr. Chen`
- If no enrolled classes exist, show a message like: `You are not enrolled in any classes yet.`

### Two-column layout

Use `st.columns(2)` to create two equal-width columns.

#### Left column: class selection

- `st.selectbox("Select a class", options=course_labels, key="selected_course_label")`
  - `course_labels` should be built from `get_available_course_keys()`
  - include either course names or a combination of `course_id` and `course_name`
- `Go To Class` button
  - label: `"Go To Class"`
  - type: default button style
  - when clicked:
    - if no course is selected, show `st.error("Please select a class to continue.")`
    - otherwise store the selected course ID in `st.session_state["selected_class_id"]`
    - optionally store selected class info in `st.session_state["selected_class_info"]`
    - show a success message with `st.success("Opening class details...")`
    - set `st.session_state["page"] = "class"`

#### Right column: enrollment key box + actions

- `st.text_input("Enter enrollment key", key="enrollment_key_input")`
- Buttons:
  - `Enroll` button
    - style: primary
    - when clicked:
      - run `service.validate_enrollment_key(enrollment_key)` or `service.get_course_by_key(enrollment_key)`
      - if key is invalid or course lookup fails, show `st.error("Enrollment key is invalid. Please check and try again.")`
      - otherwise call `service.enroll_with_key(user_id, email, enrollment_key)`
      - on success show `st.success("You are now enrolled in {course_id}.")`
      - store the enrolled course ID in `st.session_state["selected_class_id"]`
      - optionally store selected class info in `st.session_state["selected_class_info"]`
      - set `st.session_state["page"] = "class"` to navigate to the class page with the newly enrolled class details
  - `Unenroll` button
    - style: secondary or default
    - when clicked:
      - validate the enrollment key format
      - if key is invalid, show `st.error("Enrollment key is invalid. Please check and try again.")`
      - if valid, get course by key
      - if the student is not currently enrolled in that course, show `st.error("Cannot unenroll because you are not currently enrolled in this class.")`
      - otherwise call `service.soft_unenroll_student(user_id, course_id)`
      - on success show `st.success("You have been unenrolled from {course_id}.")`
      - refresh dashboard data after success and remain on `dashboard`

### Validation and behavior for dashboard actions

- Key validation should use `service.validate_enrollment_key()` and `service.get_course_by_key()`
- Enrollment is only attempted if the key is present and valid
- Unenrollment is only attempted if the course is currently enrolled
- If the student tries to enroll in a course they already have as enrolled, the backend may update or re-enroll; show a success message anyway
- If the student enters a valid key for a class they are already enrolled in and clicks `enroll`, treat it as a re-enrollment success

### Data refresh behavior

- After a successful unenrollment, refresh the enrolled class list from `service.get_student_enrollments(user_id)` and remain on `dashboard`
- After a successful enrollment, store the course details and navigate to the `class` page so the student sees the newly enrolled class immediately

## Page 2: Class (`class`)

### Page title

- `st.title("Your Class")`

### Page structure

1. A back button at the top
2. A container showing selected class details in digestible text
3. Optional summary or enrollment status display

### Navigation

- Use a button such as `st.button("Back to Dashboard")`
  - when clicked, set `st.session_state["page"] = "dashboard"`
  - optionally clear `st.session_state["selected_class_id"]`

### Class details container

- Use `st.container()` or `st.expander("Class Details")`
- Show each property on its own line with a clear label, for example:
  - `Course ID: MISY350`
  - `Course Name: Python for Business Analytics`
  - `Instructor: Dr. Rivera`
  - `Enrollment Key: MISY350-SPRING`
- Avoid printing raw dictionaries

### Data source for the class page

- Determine selected course info from one of these sources:
  - `st.session_state["selected_class_info"]` if stored by the dashboard
  - or call `service.get_course_by_key(enrollment_key)` if enrollment key is available
  - or call `service.get_available_course_keys()` and filter by selected course ID
- If `selected_class_id` is missing, show an error message and navigate back to `dashboard`

### Optional class page details

- Mention whether the student is currently enrolled in the selected class
- Use summary text like: `You are viewing details for the class you selected.`

## Actions and Feedback

### Button behavior and delay

- Wrap every actionable button callback in `with st.spinner("Processing..."):`
- Include a `time.sleep(2)` delay inside the spinner on each button press to meet the requirement

### Status messaging

- `st.success` for all successful operations
- `st.error` for invalid keys and failed actions
- `st.warning` for warnings such as missing selection or soft-unenroll attempts when not enrolled

### Specific messages

- Success messages:
  - `"Successfully enrolled in MISY350."`
  - `"Successfully re-enrolled in DATA210."`
  - `"You have been unenrolled from WEB220."`
  - `"Opening class details..."`
- Error messages:
  - `"Enrollment key is invalid. Please check and try again."`
  - `"Please enter an enrollment key to continue."`
  - `"Cannot unenroll because you are not currently enrolled in this class."`
  - `"Please select a class to continue."`
- Warning messages:
  - `"You are already enrolled in this class."` (optional warning if the UI chooses to point that out before re-enrollment)

### Refresh and page switch behavior

- After successful enrollment or unenrollment, remain on `dashboard` and refresh the displayed list
- After successful `Go To Class`, show `st.success("Opening class details...")`, then set `st.session_state["page"] = "class"`
- On the `class` page, the Back button returns to `dashboard`

## Role and page control

- Initialize `st.session_state["role"] = "user"`
- Ensure the Dashboard UI only renders for `role == "user"`
- If other role values are present, show a restricted-access warning or fallback to dashboard

## Minimal backend assumptions

The UI should treat `enrollment_starter.py` as the service layer provider. The current backend already includes:

- course lookup by enrollment key
- enrollment and soft unenrollment behavior
- retrieval of current student enrollments
- seeded sample data

The UI should not require new backend changes other than wiring the Streamlit app to the service methods.

## Example navigation flow

1. App starts with `st.session_state["page"] = "dashboard"`
2. Student sees enrolled classes and a key input
3. Student enters `DATA210-SPRING` and clicks `Enroll`
4. App validates key, calls `service.enroll_with_key(...)`, shows success, stores the enrolled class details, and switches to `page = "class"`
5. Student sees formatted details for the newly enrolled class
6. Student clicks `Back to Dashboard`
7. App returns to dashboard and shows updated data
8. Student can select another class and click `Go To Class` to see that page as well

## File deliverable

- `streamlit_ui_plan.md` is the review artifact and does not include implementation code.
- This document is a specification to guide the Streamlit implementation.
