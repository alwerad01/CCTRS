# Human-Computer Interaction (HCI) - Civic Complaint Tracking System

## 1. UI/UX Principles & Design Approach
The Civic Complaint Tracking System (CCTS) follows essential Human-Computer Interaction (HCI) principles to ensure usability, learnability, and accessibility for diverse users (citizens and municipal staff).
- **Mobile-First Responsive Design:** Built using **Bootstrap 5**, ensuring seamless experiences across desktops, tablets, and smartphones.
- **Minimal Cognitive Load:** Forms are simple and broken down, minimizing the effort required to submit a complaint. The split-screen login and modern gradient branding provide a premium feel without overwhelming visual clutter.

## 2. Affordance & Feedback
System interactions consistently afford their purpose and provide immediate visual feedback corresponding to user actions:
- **Status Badges:** Color-coded Bootstrap badges visually differentiate the 11 complaint states (e.g., Green for 'Resolved', Yellow for 'On Hold', Red for 'Rejected').
- **Toast Notifications & Validation:** The system utilizes Flask flash messages and client-side form validation (JavaScript) to alert users about successful submissions or missing required fields before form submission.
- **Interactive Map:** Providing an embedded map (Leaflet.js) offers a tangible affordance for pinning visual location data, highly superior to asking users to type out coordinates manually.

## 3. Consistency and Navigation
- **Universal Dashboard Layouts:** All 7 internal roles interact with DataTables.js structured dashboards offering pagination, sorting, and live searching. Once a citizen or officer learns the dashboard paradigm, it remains consistent throughout the application.
- **Breadcrumb Navigation & Clear Calls-to-Action:** The navigation bar clearly contrasts active routes from inactive ones, reducing spatial disorientation. Action buttons ("Submit", "Save Draft", "Upload Evidence") use distinct active colors (Primary Blue / Success Green).

## 4. Role-Specific Cognitive Filtering
The interface proactively curates information based on the user's logged-in role to avoid overwhelming them:
- **Officers:** Only see their exact assigned complaints on their specific dashboard view, hiding extraneous data from other municipal departments.
- **Supervisors:** Visualize data (using interactivity via Chart.js) tailored exactly to tracking officer workload, without directly cluttering the screen with detailed resolution text.

## 5. Error Prevention & Recovery
- **Enforced Transitions:** Officers are provided dropdowns strictly filtering out impossible lifecycle transitions (e.g., 'Draft' directly to 'Resolved' is disabled). The UI physically prevents incorrect data input.
- **Draft Saving:** Citizens can save complaint progress mid-way as a 'Draft', preventing data loss in the event of browser closures or network interruptions.
- **File Upload Guard:** The evidence uploader interface strictly accepts pre-vetted formats (PDFs, MP4s, Images) ensuring users don't face sudden backend errors when attaching media.
