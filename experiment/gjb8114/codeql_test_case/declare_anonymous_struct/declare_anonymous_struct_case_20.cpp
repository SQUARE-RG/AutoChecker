#include <stdio.h>

struct Employee {
    int id;
    struct Info {
        char name[30];
        int age;
        struct Department {
            char dept_name[20];
            int dept_id;
        } department;
    } info;  // 符合：完整命名结构体体系
};

int main(void) {
    struct Employee emp;
    emp.id = 1001;
    emp.info.age = 30;
    emp.info.department.dept_id = 5;
    return 0;
}