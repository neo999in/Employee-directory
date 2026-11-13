export interface Employee {
  id: number;
  name: string;
  email: string;
  department: string;
  designation: string;
  date_of_joining: string;
}

export interface EmployeeSearchResponse {
  count: number;
  employees: Employee[];
}

export interface ApiError {
  detail: string;
  errors?: string[];
}
