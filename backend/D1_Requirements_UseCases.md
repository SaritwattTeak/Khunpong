**Gemini Project**

**System user**

| User role | Description |
| :---- | :---- |
| Astronomer | Using gemini to collect science data |
| Science Observer | This is the on-site person responsible for monitoring the data acquisition and validating the data being collected for the astronomer |
| Telescope Operator | The on-site controller of the telescope and instruments |
| Support Staff | On-site (or near-site) support personnel are responsible for the maintenance of the system |
| Administrator | Administrators are responsible for high-level functional control of the Gemini system as an integrated system. |

**Functional Requirements**

**For Astronomer**

* System shall allow to create a science plan  
* System shall allow to use virtual telescope to test a science plan  
* System shall allow submit science plan  
* System shall allow to observe/monitor status  
* System should allow to access observation data

**For Science Observers**

* System shall allow to validate science plan  
* System shall allow to execute approved observing programs  
* System shall allow to transform a science plan into an observing program  
* System shall allow to monitor observation progress  
* System shall allow to validate collected data quality

**For Telescope Operator**

* System shall allow to directly control telescope  
* System shall allow to stop observations in unsafe conditions  
* System shall allow to monitor all subsystems  
* System shall allow to change operational modes

**For Support Staff**

* System shall allow to install and remove instruments  
* System shall allow to run maintenance diagnostics  
* System shall to update system configurations


**For Administrators**

* System shall allow to view system status  
* System shall allow to access scheduling information  
* System shall prevent from controlling the telescope


**Non-Functional Requirements for Developer Role**

**Security & Control**

* System shall restrict developer access to test and maintenance modes  
* System shall log all developer actions  
* System shall enforce strict access permissions

**Reliability**

* System shall ensure that development activities do not impact ongoing operations  
* System shall allow rollback if an update fails


**Usability**

* The system shall provide clear system status indicators  
* The system shall clearly distinguish test mode from observing mode  
* The system shall provide clear feedback for failed tests

### **Maintainability**

* The system shall support modular updates  
* The system shall support long-term maintenance  
* The system shall support system evolution without redesigning core operations

**Use Case Diagram**


  <img width="760" height="1548" alt="observatory_workflow" src="https://github.com/user-attachments/assets/961b1123-56f2-477b-81d7-eaed7d7784fb" />
