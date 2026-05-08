from __future__ import annotations

import time
from typing import Any

import streamlit as st

from enrollment_starter import Config, EnrollmentDatabase, EnrollmentService


LOGGED_IN_STUDENT = {
    "user_id": "u100",
    "name": "Kayleigh O'Donnell",
    "email": "kayleigh.odonnell@example.edu",
}


def initialize_session_state() -> None:
    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard"
    if "role" not in st.session_state:
        st.session_state["role"] = "user"
    if "selected_class_id" not in st.session_state:
        st.session_state["selected_class_id"] = None
    if "selected_class_info" not in st.session_state:
        st.session_state["selected_class_info"] = None
    if "enrollment_key_input" not in st.session_state:
        st.session_state["enrollment_key_input"] = ""
    if "selected_course_label" not in st.session_state:
        st.session_state["selected_course_label"] = None
    if "status_message" not in st.session_state:
        st.session_state["status_message"] = None


def build_course_label(course: dict[str, Any]) -> str:
    return f"{course['course_id']} — {course['course_name']}"


def get_course_by_label(
    courses: list[dict[str, Any]], selected_label: str | None
) -> dict[str, Any] | None:
    if not selected_label:
        return None
    return next(
        (course for course in courses if build_course_label(course) == selected_label),
        None,
    )


def render_dashboard(service: EnrollmentService, config: Config) -> None:
    st.title("Student Dashboard")
    st.write(f"Logged in as **{LOGGED_IN_STUDENT['name']}**")
    st.write(f"Role: **{st.session_state['role']}**")

    user_id = LOGGED_IN_STUDENT["user_id"]
    email = LOGGED_IN_STUDENT["email"]
    available_courses = service.get_available_course_keys()
    enrolled_courses = service.get_student_enrollments(user_id)

    with st.container():
        st.subheader("Your Enrolled Classes")
        if enrolled_courses:
            for record in enrolled_courses:
                st.markdown(
                    f"- **{record['course_id']}** — {record['course_name']} — {record['instructor']}"
                )
        else:
            st.info("You are not enrolled in any classes yet.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Go to Class")
        course_labels = [build_course_label(course) for course in available_courses]
        if course_labels:
            st.selectbox(
                "Select a class",
                course_labels,
                key="selected_course_label",
            )
        else:
            st.selectbox("Select a class", ["No classes available"], disabled=True)

        if st.button("Go To Class"):
            with st.spinner("Processing..."):
                time.sleep(2)
                target_course = get_course_by_label(
                    available_courses, st.session_state["selected_course_label"]
                )
                if not target_course:
                    st.error("Please select a class to continue.")
                else:
                    st.success("Opening class details...")
                    st.session_state["selected_class_id"] = target_course["course_id"]
                    st.session_state["selected_class_info"] = target_course
                    st.session_state["page"] = "class"

    with col2:
        st.subheader("Enroll or Unenroll")
        st.text_input("Enter enrollment key", key="enrollment_key_input")

        if st.button("Enroll"):
            with st.spinner("Processing..."):
                time.sleep(2)
                enrollment_key = st.session_state["enrollment_key_input"].strip()
                if not enrollment_key:
                    st.error("Please enter an enrollment key to continue.")
                else:
                    course = service.get_course_by_key(enrollment_key)
                    if not course:
                        st.error("Enrollment key is invalid. Please check and try again.")
                    else:
                        enrollment_record = service.enroll_with_key(user_id, email, enrollment_key)
                        if enrollment_record:
                            st.success(f"Successfully enrolled in {course['course_id']}.")
                            st.session_state["selected_class_id"] = course["course_id"]
                            st.session_state["selected_class_info"] = course
                            st.session_state["page"] = "class"
                        else:
                            st.error("Enrollment failed. Please try again.")

        if st.button("Unenroll"):
            with st.spinner("Processing..."):
                time.sleep(2)
                enrollment_key = st.session_state["enrollment_key_input"].strip()
                if not enrollment_key:
                    st.error("Please enter an enrollment key to continue.")
                else:
                    course = service.get_course_by_key(enrollment_key)
                    if not course:
                        st.error("Enrollment key is invalid. Please check and try again.")
                    else:
                        history = service.get_student_enrollment_history(user_id)
                        currently_enrolled = next(
                            (
                                record
                                for record in history
                                if record["course_id"] == course["course_id"]
                                and record["status"] == config.STATUS_ENROLLED
                            ),
                            None,
                        )
                        if not currently_enrolled:
                            st.error(
                                "Cannot unenroll because you are not currently enrolled in this class."
                            )
                        else:
                            success = service.soft_unenroll_student(
                                user_id, course["course_id"]
                            )
                            if success:
                                st.success(
                                    f"You have been unenrolled from {course['course_id']}.")
                            else:
                                st.error("Unenrollment failed. Please try again.")

    with st.container():
        summary = service.get_student_summary(user_id)
        st.write(
            f"Enrollment summary: {summary['total_records']} records, "
            f"{summary[config.STATUS_ENROLLED]} enrolled, "
            f"{summary[config.STATUS_UNENROLLED]} unenrolled."
        )


def render_class_page(service: EnrollmentService, config: Config) -> None:
    st.title("Your Class")
    if st.button("Back to Dashboard"):
        st.session_state["page"] = "dashboard"
        return

    selected_class = st.session_state.get("selected_class_info")
    if not selected_class and st.session_state.get("selected_class_id"):
        available_courses = service.get_available_course_keys()
        selected_class = next(
            (
                course
                for course in available_courses
                if course["course_id"] == st.session_state["selected_class_id"]
            ),
            None,
        )
        st.session_state["selected_class_info"] = selected_class

    if not selected_class:
        st.error("No class selected. Returning to dashboard.")
        st.session_state["page"] = "dashboard"
        return

    with st.container():
        st.subheader("Class Details")
        st.markdown(f"**Course ID:** {selected_class['course_id']}")
        st.markdown(f"**Course Name:** {selected_class['course_name']}")
        st.markdown(f"**Instructor:** {selected_class['instructor']}")
        st.markdown(f"**Enrollment Key:** {selected_class['enrollment_key']}")

        user_id = LOGGED_IN_STUDENT["user_id"]
        history = service.get_student_enrollment_history(user_id)
        enrolled_status = any(
            record["course_id"] == selected_class["course_id"]
            and record["status"] == config.STATUS_ENROLLED
            for record in history
        )
        status_label = "Currently enrolled" if enrolled_status else "Not currently enrolled"
        st.info(status_label)


def run_streamlit_app(service: EnrollmentService, config: Config) -> None:
    initialize_session_state()

    if st.session_state["role"] != "user":
        st.warning("Access restricted. User role required.")
        return

    if st.session_state["page"] == "class":
        render_class_page(service, config)
    else:
        render_dashboard(service, config)


def main() -> None:
    config = Config()
    database = EnrollmentDatabase(config)
    service = EnrollmentService(database, config)

    database.create_tables()
    database.seed_sample_data()

    run_streamlit_app(service, config)


if __name__ == "__main__":
    main()
