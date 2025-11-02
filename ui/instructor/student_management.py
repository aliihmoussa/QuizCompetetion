"""
Instructor Student Management Module
View and manage students with statistics
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from shared import ui_components as ui
from shared.styles import COLORS


class StudentManagementView:
    """Student management view for instructors"""
    
    def __init__(self, student_service, scoring_service):
        """
        Initialize student management view
        
        Args:
            student_service: StudentService instance
            scoring_service: ScoringService instance
        """
        self.student_service = student_service
        self.scoring_service = scoring_service
    
    def render(self, instructor_id):
        """
        Render the student management interface
        
        Args:
            instructor_id: UUID of the logged-in instructor
        """
        ui.section_header(
            "Student Management",
            "View and manage all students in the system",
            "👥"
        )
        
        try:
            # Search and filter controls
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                search_query = st.text_input(
                    "🔍 Search students",
                    placeholder="Search by username or email...",
                    key="student_search"
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Last Active", "Name", "Total Sessions"],
                    key="student_sort"
                )
            
            with col3:
                per_page = st.selectbox(
                    "Per page",
                    [25, 50, 100],
                    key="students_per_page"
                )
            
            st.divider()
            
            # Get all students with stats
            students = self.student_service.get_all_students_with_stats(
                instructor_id=instructor_id,
                search=search_query if search_query else None
            )
            
            if not students:
                ui.empty_state(
                    "👥",
                    "No Students Found",
                    "No students match your search criteria." if search_query else "No students have registered yet."
                )
                return
            
            # Display total count
            st.markdown(f"### Found {len(students)} student{'s' if len(students) != 1 else ''}")
            
            # Sort students
            if sort_by == "Name":
                students = sorted(students, key=lambda x: x['username'])
            elif sort_by == "Last Active":
                students = sorted(students, key=lambda x: x['last_active'] or datetime.min, reverse=True)
            elif sort_by == "Total Sessions":
                students = sorted(students, key=lambda x: x['total_sessions'], reverse=True)
            
            # Display students in a grid
            for student in students[:per_page]:
                self._render_student_card(student)
            
            # Export button
            st.divider()
            if st.button("📊 Export Student Data to CSV", use_container_width=True):
                self._export_to_csv(students)
        
        except Exception as e:
            st.error(f"Error loading students: {e}")
    
    def _render_student_card(self, student):
        """Render a single student card"""
        with st.expander(
            f"👤 {student['username']} ({student['email']})",
            expanded=False
        ):
            cols = st.columns(4)
            
            with cols[0]:
                st.metric(
                    "Total Sessions",
                    student.get('total_sessions', 0)
                )
            
            with cols[1]:
                st.metric(
                    "Total Answers",
                    student.get('total_answers', 0)
                )
            
            with cols[2]:
                avg_score = student.get('avg_score', 0)
                st.metric(
                    "Avg Score",
                    f"{avg_score:.1f}%" if avg_score else "N/A"
                )
            
            with cols[3]:
                last_active = student.get('last_active')
                if last_active:
                    last_active_str = last_active.strftime("%Y-%m-%d %H:%M")
                else:
                    last_active_str = "Never"
                
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <div style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin-bottom: 0.25rem;">Last Active</div>
                        <div style="color: {COLORS['text_primary']}; font-weight: 600;">{last_active_str}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Additional details
            st.divider()
            
            detail_cols = st.columns(2)
            with detail_cols[0]:
                st.markdown(f"**User ID:** `{str(student['id'])[:8]}...`")
                st.markdown(f"**Created:** {student.get('created_at', 'N/A')}")
            
            with detail_cols[1]:
                st.markdown(f"**Role:** {student.get('role', 'STUDENT')}")
                st.markdown(f"**Status:** {'Active' if student.get('last_active') else 'Inactive'}")
    
    def _export_to_csv(self, students):
        """Export student data to CSV"""
        try:
            # Prepare data for export
            export_data = []
            for student in students:
                export_data.append({
                    'Username': student['username'],
                    'Email': student['email'],
                    'Total Sessions': student.get('total_sessions', 0),
                    'Total Answers': student.get('total_answers', 0),
                    'Avg Score': f"{student.get('avg_score', 0):.1f}%",
                    'Last Active': student.get('last_active', 'Never'),
                    'Created At': student.get('created_at', 'N/A')
                })
            
            # Create DataFrame
            df = pd.DataFrame(export_data)
            
            # Generate CSV
            csv = df.to_csv(index=False)
            
            # Download button
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.success("✅ CSV ready for download!")
        
        except Exception as e:
            st.error(f"Error exporting data: {e}")

