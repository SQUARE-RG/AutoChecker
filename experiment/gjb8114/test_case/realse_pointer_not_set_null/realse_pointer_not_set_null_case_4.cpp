#include <stdlib.h>

struct Student {
    int id;
    char name[20];
};

void test_struct_pointer(void) {
    struct Student *stu = (struct Student*)malloc(sizeof(struct Student));
    if (stu != NULL) {
        stu->id = 1001;
        free(stu);  // 违反：结构体指针释放后未置空
        // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
    }
}

int main(void) {
    test_struct_pointer();
    return 0;
}