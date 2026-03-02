#include <stdlib.h>

struct Employee {
    int id;
    char name[30];
};

void test_proper_struct_free(void) {
    struct Employee *emp = (struct Employee*)malloc(sizeof(struct Employee));
    if (emp != NULL) {
        emp->id = 2001;
        free(emp);
        emp = NULL;  // 符合：结构体指针释放后置空
    }
}

int main(void) {
    test_proper_struct_free();
    return 0;
}